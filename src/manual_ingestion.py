"""Offline ingestion of provenance-reviewed official XLSX/CSV uploads."""
import argparse
import calendar
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
import zipfile
import urllib.parse
from zoneinfo import ZoneInfo

import pandas as pd
from .manual_reference import GOVERNORATES, HEADER_ALIASES, HEADER_LOOKUP, governorate, normalize

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'manual-ingestion-v1'
MISSING = {'', '-', '—', '–', '..', '...', '…', 'n/a', 'na', 'null', 'none'}
KEY_FIELDS = ('scope_id', 'indicator', 'unit', 'period_start', 'period_end', 'frequency',
              'geographic_level', 'governorate_id', 'wilayat', 'property_category',
              'transaction_type', 'index_base_period')
DIGITS = str.maketrans('٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹', '01234567890123456789')


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def blank(value):
    return value is None or (not isinstance(value, (list, dict)) and pd.isna(value)) or str(value).strip().casefold() in MISSING


def text(value):
    return '' if blank(value) else str(value).strip()


def reference_path(path):
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def official_url(value):
    parts = urllib.parse.urlsplit(str(value))
    if parts.scheme != 'https' or not parts.hostname or not parts.hostname.endswith('.gov.om') or parts.username:
        raise ValueError('source_url must identify an official HTTPS gov.om resource')


def validate_metadata(meta, payload):
    for key in ('dataset_id', 'title', 'publisher', 'source_url', 'retrieved_at'):
        if not isinstance(meta.get(key), str) or not meta[key].strip():
            raise ValueError(f'Missing metadata: {key}')
    if not re.fullmatch(r'[a-z0-9_]+', meta['dataset_id']):
        raise ValueError('dataset_id must use lowercase letters, digits and underscores')
    official_url(meta['source_url'])
    timestamp = datetime.fromisoformat(meta['retrieved_at'].replace('Z', '+00:00'))
    if timestamp.tzinfo is None:
        raise ValueError('retrieved_at must include a timezone')
    if meta.get('publication_date') is not None:
        date.fromisoformat(meta['publication_date'])
    if meta.get('expected_sha256') != digest(payload):
        raise ValueError('Original SHA-256 missing or mismatched; do not edit the original')
    verification = meta.get('verification', {})
    if verification.get('status') != 'reviewed_official' or not verification.get('reviewed_by'):
        raise ValueError('Official origin must be reviewed in metadata before ingestion')
    reviewed_at = datetime.fromisoformat(verification['reviewed_at'].replace('Z', '+00:00'))
    if reviewed_at.tzinfo is None:
        raise ValueError('reviewed_at must include a timezone')
    licence = meta.get('licence', {})
    if not licence.get('name') or not licence.get('url') or licence.get('redistribution_allowed') is not True:
        raise ValueError('Record verified licence and redistribution rights before ingestion')
    if urllib.parse.urlsplit(licence['url']).scheme != 'https':
        raise ValueError('licence.url must be HTTPS')
    if not isinstance(meta.get('tables'), list) or not meta['tables']:
        raise ValueError('Select at least one table; no sheet or metric is guessed')


def decimal_value(value, unit, multiplier='1', decimal_separator='.', thousands_separator=','):
    if blank(value):
        return None
    original = str(value).strip()
    if '\u066c' in original or '\u066b' in original:
        decimal_separator, thousands_separator = '.', ','
    token = original.translate(DIGITS).replace('\u066c', ',').replace('\u066b', '.')
    if not decimal_separator or decimal_separator == thousands_separator:
        raise ValueError('Decimal and thousands separators must be different')
    # Arabic separators above use dot/comma; locale settings apply to Latin punctuation.
    if thousands_separator:
        grouping = re.escape(thousands_separator)
        fraction = re.escape(decimal_separator)
        if not re.fullmatch(rf'(?:\d+|\d{{1,3}}(?:{grouping}\d{{3}})+)(?:{fraction}\d+)?', token):
            raise ValueError(f'Invalid numeric syntax: {value!r}')
        token = token.replace(thousands_separator, '')
    else:
        if not re.fullmatch(rf'\d+(?:{re.escape(decimal_separator)}\d+)?', token):
            raise ValueError(f'Invalid numeric syntax: {value!r}')
    token = token.replace(decimal_separator, '.')
    try:
        number, scale = Decimal(token), Decimal(str(multiplier))
    except InvalidOperation as exc:
        raise ValueError('Invalid numeric value or multiplier') from exc
    if not number.is_finite() or number < 0 or not scale.is_finite() or scale <= 0:
        raise ValueError('Values must be finite/nonnegative and multipliers positive')
    if unit not in {'count', 'OMR', 'index_points'}:
        raise ValueError('Supported canonical units: count, OMR, index_points')
    if unit in {'count', 'index_points'} and scale != 1:
        raise ValueError('Counts and indices cannot be scaled')
    if unit == 'count' and number != number.to_integral_value():
        raise ValueError('Counts must be integers')
    if unit == 'index_points' and number <= 0:
        raise ValueError('Price indices must be positive')
    return format(number * scale, 'f')


def integer(value):
    raw = decimal_value(value, 'count')
    if raw is None:
        raise ValueError('Required period component missing')
    return int(Decimal(raw))


def source_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(text(value))


def period(record, constants, as_of):
    get = lambda key: record[key] if key in record else constants.get(key)
    frequencies = {'monthly':'monthly','شهري':'monthly','quarterly':'quarterly','ربع سنوي':'quarterly','annual':'annual','annually':'annual','سنوي':'annual','year to date':'year_to_date','year_to_date':'year_to_date','تراكمي':'year_to_date'}
    frequency = frequencies.get(normalize(get('frequency')), text(get('frequency')))
    if frequency not in {'monthly', 'quarterly', 'annual', 'year_to_date'}:
        raise ValueError('Explicit frequency required: monthly, quarterly, annual, year_to_date')
    start, end = get('period_start'), get('period_end')
    if not blank(start) or not blank(end):
        if blank(start) or blank(end):
            raise ValueError('Both period boundaries must be supplied')
        start, end = source_date(start), source_date(end)
    else:
        year = integer(get('year'))
        if frequency == 'monthly':
            month = integer(get('month'))
            start, end = date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])
        elif frequency == 'quarterly':
            quarter = integer(get('quarter'))
            if quarter not in {1, 2, 3, 4}:
                raise ValueError('Quarter must be 1–4')
            month = 3 * quarter
            start, end = date(year, month-2, 1), date(year, month, calendar.monthrange(year, month)[1])
        elif frequency == 'annual':
            start, end = date(year, 1, 1), date(year, 12, 31)
        else:
            raise ValueError('Year-to-date records need explicit source period boundaries')
    if start > end or start.year < 2020 or end.year > 2026 or end > as_of:
        raise ValueError('Invalid, future or out-of-scope reporting period')
    if not blank(get('year')) and integer(get('year')) != start.year:
        raise ValueError('Year conflicts with reporting boundaries')
    if frequency == 'monthly' and (start.day != 1 or start.year != end.year or start.month != end.month or end.day != calendar.monthrange(end.year, end.month)[1]):
        raise ValueError('Monthly boundaries must cover exactly one complete month')
    if frequency == 'monthly' and not blank(get('month')) and integer(get('month')) != start.month:
        raise ValueError('Month conflicts with reporting boundaries')
    if frequency == 'annual' and (start.month, start.day, end.month, end.day, start.year == end.year) != (1, 1, 12, 31, True):
        raise ValueError('Annual boundaries must cover one complete year')
    if frequency == 'quarterly' and (start.month not in {1,4,7,10} or start.day != 1 or start.year != end.year or end.month != start.month+2 or end.day != calendar.monthrange(end.year,end.month)[1]):
        raise ValueError('Quarterly boundaries must cover one complete quarter')
    if frequency == 'quarterly' and not blank(get('quarter')) and integer(get('quarter')) != (start.month-1)//3+1:
        raise ValueError('Quarter conflicts with reporting boundaries')
    if frequency == 'year_to_date' and ((start.month,start.day) != (1,1) or start.year != end.year):
        raise ValueError('Year-to-date boundaries must start January 1')
    return start.isoformat(), end.isoformat(), frequency


def read_table(path, table):
    if table.get('observation_grain') != 'aggregate':
        raise ValueError('Reviewed aggregate observation_grain required; transaction-level files need a dedicated adapter')
    header = table.get('header_row', 1)
    if not isinstance(header, int) or header < 1:
        raise ValueError('header_row is a positive 1-based row number')
    if path.suffix.lower() == '.xlsx':
        if not isinstance(table.get('sheet'), str) or not table['sheet']:
            raise ValueError('Explicit XLSX sheet name required')
        from src.excel_reader import read_workbook
        sheet = next((s for s in read_workbook(path)['sheets'] if s['name'] == table['sheet']), None)
        if sheet is None or len(sheet['rows']) < header:
            raise ValueError('Selected worksheet or header row is absent')
        rows = sheet['rows']
        frame = pd.DataFrame(rows[header:], columns=rows[header-1], dtype=object)
        frame = frame.where(frame.notna(), '')
    else:
        frame = pd.read_csv(path, header=header-1, dtype=str, keep_default_na=False,
                            encoding=table.get('encoding', 'utf-8-sig'), sep=table.get('delimiter', ','))
    if len(frame) > 500000:
        raise ValueError('Table exceeds 500,000-row safety limit')
    if not frame.empty:
        frame = frame.drop(columns=[c for c in frame.columns if str(c).startswith('Unnamed:') and all(blank(v) for v in frame[c])])
    if {'__source_row','__source_column'} & set(frame.columns):
        raise ValueError('Source header collides with a reserved provenance field')
    frame['__source_row'] = range(header+1, header+1+len(frame))
    if table.get('layout', 'records') == 'wide':
        axis, selected = table['wide_dimension'], table['wide_columns']
        if axis not in {'year', 'governorate'} or not selected:
            raise ValueError('Wide tables require year/governorate axis and explicit columns')
        lookup = {str(c): c for c in frame.columns}
        selected = [lookup[str(c)] for c in selected]
        frame = frame.melt(id_vars=[c for c in frame.columns if c not in selected],
                           value_vars=selected, var_name=axis, value_name=table['wide_value_field'])
        frame['__source_column'] = frame[axis].astype(str)
    elif table.get('layout', 'records') != 'records':
        raise ValueError('Supported layouts: records, wide')
    return frame


def map_columns(frame, table):
    headers = defaultdict(list)
    for column in frame.columns:
        if column not in {'__source_row','__source_column'}:
            headers[normalize(column)].append(column)
    if any(len(v) > 1 for v in headers.values()):
        raise ValueError('Ambiguous normalized headers; provide a clean table selection')
    mapped, used = {}, set()
    for canonical, original in table.get('columns', {}).items():
        if canonical not in HEADER_ALIASES or normalize(original) not in headers:
            raise ValueError(f'Unknown mapping or absent column: {canonical} -> {original}')
        selected = headers[normalize(original)][0]
        if selected in used:
            raise ValueError('One input column cannot represent multiple fields')
        mapped[canonical], used = selected, used | {selected}
    for key, columns in headers.items():
        canonical = HEADER_LOOKUP.get(key)
        if canonical and canonical not in table.get('columns', {}) and columns[0] not in used:
            if canonical in mapped:
                raise ValueError(f'Multiple headers map to {canonical}; choose explicitly')
            mapped[canonical] = columns[0]
    ignored = {normalize(c) for c in table.get('ignored_columns', [])}
    unmapped = [c for c in frame.columns if c not in {'__source_row','__source_column'} and c not in mapped.values() and normalize(c) not in ignored]
    if unmapped:
        raise ValueError(f'Unmapped columns require explicit mapping or ignored_columns: {unmapped}')
    return mapped


def normalize_rows(frame, table, meta, path, sha, as_of):
    mapping = map_columns(frame, table)
    constants = table.get('constants', {})
    for field in constants:
        if field not in HEADER_ALIASES:
            raise ValueError(f'Unsupported constant: {field}')
        if field in mapping:
            raise ValueError(f'Constant cannot override source column: {field}')
    if not re.fullmatch(r'[a-z0-9_]+', str(table.get('scope_id', ''))):
        raise ValueError('A reviewed semantic scope_id is required')
    metrics = table.get('metrics', [])
    if not metrics:
        raise ValueError('Explicit metric definitions are required')
    if len({m.get('field') for m in metrics}) != len(metrics):
        raise ValueError('Each source metric field must have one declared meaning')
    for metric in metrics:
        if metric.get('field') not in {'transaction_count','transaction_value','property_price_index','value'} or metric['field'] not in mapping:
            raise ValueError('Metric field must identify an available mapped value column')
        if not re.fullmatch(r'[a-z0-9_]+', str(metric.get('indicator', ''))):
            raise ValueError('Explicit indicator name required')
        if metric.get('unit') not in {'count','OMR','index_points'}:
            raise ValueError('Explicit canonical metric unit required')
        if not text(metric.get('source_unit')):
            raise ValueError('Explicit source_unit is required for every metric')
        if metric['unit'] == 'OMR' and 'multiplier' not in metric:
            raise ValueError('Currency multiplier must be explicitly reviewed')
        if metric['unit'] == 'index_points' and not metric.get('index_base_period'):
            raise ValueError('Official index base period is required')
    rows, missing, excluded = [], [], []
    for _, original in frame.iterrows():
        if all(blank(original[c]) for c in frame.columns if c not in {'__source_row','__source_column'}):
            continue
        record = {key: original[column] for key,column in mapping.items()}
        get = lambda key: record[key] if key in record else constants.get(key)
        number = int(original['__source_row'])
        try:
            if table.get('geographic_level') not in {'governorate','wilayat','national'}:
                raise ValueError('Explicit geographic_level required')
            if table['geographic_level'] == 'national':
                if not blank(get('governorate')) and governorate(get('governorate')) is not None:
                    raise ValueError('National table contains governorate observations')
                gov = ('', '', '')
            else:
                if blank(get('governorate')):
                    raise ValueError('Governorate is missing')
                gov = governorate(get('governorate'))
                if gov is None:
                    if table.get('totals_policy') != 'exclude':
                        raise ValueError('National total row requires explicit totals_policy=exclude')
                    excluded.append(dict(source_row=number,reason='explicitly excluded national total'))
                    continue
            if table['geographic_level'] == 'governorate' and not blank(get('wilayat')):
                raise ValueError('Governorate aggregates cannot contain wilayat-level rows')
            if table['geographic_level'] == 'wilayat' and blank(get('wilayat')):
                raise ValueError('Wilayat is required for wilayat-level data')
            start,end,frequency = period(record,constants,as_of)
            for metric in metrics:
                value = decimal_value(record[metric['field']], metric['unit'], metric.get('multiplier','1'),
                                      table.get('decimal_separator','.'), table.get('thousands_separator',','))
                if value is None:
                    missing.append(dict(source_row=number,indicator=metric['indicator'],reason='source value missing; not imputed'))
                    continue
                observation = dict(scope_id=table['scope_id'],indicator=metric['indicator'],value=value,
                    unit=metric['unit'],period_start=start,period_end=end,frequency=frequency,
                    geographic_level=table['geographic_level'],governorate_id=gov[0],
                    governorate=gov[1],governorate_ar=gov[2],wilayat=text(get('wilayat')),
                    property_category=text(get('property_category')),transaction_type=text(get('transaction_type')),
                    index_base_period=text(metric.get('index_base_period')))
                provenance = dict(dataset_id=meta['dataset_id'],source_file=reference_path(path),raw_sha256=sha,
                    source_url=meta['source_url'],publisher=meta['publisher'],title=meta['title'],
                    sheet=table.get('sheet',''),source_row=number,source_column=str(original.get('__source_column', mapping[metric['field']])),
                    publication_date=meta.get('publication_date'),retrieved_at=meta['retrieved_at'],
                    verification_status='metadata_reviewed_official',licence=meta['licence']['name'],
                    licence_url=meta['licence']['url'],source_unit=metric['source_unit'],
                    unit_multiplier=str(metric.get('multiplier','1')),scope_id=table['scope_id'])
                rows.append((observation,provenance))
        except (ValueError,KeyError,TypeError) as exc:
            raise ValueError(f'{path.name}, sheet {table.get("sheet", "CSV")}, row {number}: {exc}') from exc
    return rows,missing,excluded


def deduplicate(rows):
    observations, provenance, duplicates = {}, [], 0
    for row, source in rows:
        key = tuple(row[field] for field in KEY_FIELDS)
        identifier = digest(json.dumps(key,ensure_ascii=False).encode())
        if identifier in observations:
            if Decimal(observations[identifier]['value']) != Decimal(row['value']):
                raise ValueError('Conflicting values for the same observation; select a source vintage explicitly')
            duplicates += 1
        else:
            observations[identifier] = dict(observation_id=identifier, **row)
        provenance.append(dict(observation_id=identifier, **source))
    # Identical input-cell provenance is recorded only once; alternate sources remain.
    unique = {json.dumps(p,sort_keys=True,ensure_ascii=False):p for p in provenance}
    return list(observations.values()),list(unique.values()),duplicates


def coverage(rows):
    groups = defaultdict(set)
    group_fields = ('scope_id','indicator','unit','period_start','period_end','frequency',
                    'geographic_level','wilayat','property_category','transaction_type','index_base_period')
    for row in rows:
        # Wilayat observations are not implicitly aggregated to governorates.
        key = tuple(row[field] for field in group_fields)
        if row['geographic_level'] == 'governorate':
            groups[key].add(row['governorate_id'])
        else:
            groups[key]
    return [dict(zip(group_fields,key),**governorate_presence(present))
            for key,present in sorted(groups.items())]


def governorate_presence(present):
    """Compare reference labels only; this function does not create observations."""
    expected = {g[0] for g in GOVERNORATES}
    return dict(governorates_present=sorted(present),missing_governorates=sorted(expected-present),
                all_11_present=present==expected)


def input_files(folder):
    return sorted(p for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in {'.xlsx','.csv'} and not p.name.startswith('~$'))


def init_metadata(path):
    path = Path(path)
    if path.suffix.lower() not in {'.xlsx','.csv'} or not path.is_file():
        raise ValueError('Provide an existing official XLSX/CSV file')
    target = Path(str(path)+'.metadata.json')
    if target.exists():
        raise ValueError('Metadata already exists; it will not be overwritten')
    sha = digest(path.read_bytes())
    meta = dict(dataset_id='upload_'+sha[:12],title=None,publisher=None,source_url=None,
        publication_date=None,retrieved_at=None,expected_sha256=sha,
        verification=dict(status='pending',reviewed_by=None,reviewed_at=None),
        licence=dict(name=None,url=None,redistribution_allowed=False),tables=[])
    target.write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n')
    print(target)


def inspect_files(folder):
    for path in input_files(folder):
        item = dict(file=path.as_posix(),sha256=digest(path.read_bytes()))
        if path.suffix.lower() == '.xlsx':
            with pd.ExcelFile(path,engine='openpyxl') as book:
                item['sheets'] = book.sheet_names
        else:
            item['headers_utf8_comma'] = list(pd.read_csv(path,nrows=0,encoding='utf-8-sig').columns)
        print(json.dumps(item,ensure_ascii=False))


def run(folder, output_root, status_path, as_of=None, files=None):
    as_of = as_of or datetime.now(ZoneInfo('Asia/Muscat')).date()
    files = input_files(folder) if files is None else list(files)
    report = dict(pipeline_version=VERSION,as_of=as_of.isoformat(),state='awaiting_official_files',
        imported_files=0,unique_observations=0,ready_for_python_powerbi=False,
        original_files=[],errors=[],coverage=[],missing_values=[],excluded_rows=[])
    if not files:
        status_path.parent.mkdir(parents=True,exist_ok=True)
        status_path.write_text(json.dumps(report,indent=2)+'\n')
        return report,2
    pairs, fingerprints, seen_ids = [], [], set()
    for path in files:
        try:
            if path.stat().st_size>50*1024*1024:
                raise ValueError('File exceeds 50 MiB ingestion limit')
            payload = path.read_bytes()
            if len(payload)>50*1024*1024:
                raise ValueError('File exceeds 50 MiB ingestion limit')
            metadata_path = Path(str(path)+'.metadata.json')
            metadata_bytes = metadata_path.read_bytes()
            meta = json.loads(metadata_bytes)
            validate_metadata(meta,payload)
            if meta['dataset_id'] in seen_ids:
                raise ValueError('Duplicate dataset_id; preserve a distinct source registration')
            seen_ids.add(meta['dataset_id'])
            sha = digest(payload)
            for table in meta['tables']:
                rows,missing,excluded = normalize_rows(read_table(path,table),table,meta,path,sha,as_of)
                pairs.extend(rows)
                report['missing_values'].extend(dict(dataset_id=meta['dataset_id'],sheet=table.get('sheet',''),**m) for m in missing)
                report['excluded_rows'].extend(dict(dataset_id=meta['dataset_id'],sheet=table.get('sheet',''),**e) for e in excluded)
            # Confirm bytes were not changed by ingestion or a concurrent editor.
            if digest(metadata_path.read_bytes()) != digest(metadata_bytes):
                raise ValueError('Metadata changed during ingestion')
            if digest(path.read_bytes()) != sha:
                raise ValueError('Original changed during ingestion')
            report['original_files'].append(dict(dataset_id=meta['dataset_id'],file=reference_path(path),sha256=sha,metadata_sha256=digest(metadata_bytes)))
            fingerprints.append((sha,digest(metadata_bytes)))
        except (ValueError,OSError,KeyError,TypeError,zipfile.BadZipFile) as exc:
            report['errors'].append(dict(file=path.as_posix(),reason=str(exc)))
    if not report['errors']:
        try:
            observations,lineage,removed = deduplicate(pairs)
            if not observations:
                raise ValueError('No actual metric values were imported')
            report['coverage'] = coverage(observations)
            report.update(imported_files=len(files),unique_observations=len(observations),
                duplicate_observations_removed=removed,
                ready_for_python_powerbi=all(c['all_11_present'] for c in report['coverage']) and not report['missing_values'])
            report['state'] = 'imported_all_11' if report['ready_for_python_powerbi'] else 'imported_incomplete_coverage'
            run_id = digest(json.dumps([VERSION,as_of.isoformat(),sorted(fingerprints)]).encode())[:20]
            target = output_root/run_id
            artifacts = {
                'observations.csv':pd.DataFrame(observations).to_csv(index=False,lineterminator='\n'),
                'provenance.csv':pd.DataFrame(lineage).to_csv(index=False,lineterminator='\n'),
                'coverage.csv':pd.DataFrame([dict(c,governorates_present=';'.join(c['governorates_present']),missing_governorates=';'.join(c['missing_governorates'])) for c in report['coverage']]).to_csv(index=False,lineterminator='\n'),
            }
            report['output_directory'] = reference_path(target)
            report['output_sha256'] = {name:digest(content.encode()) for name,content in artifacts.items()}
            artifacts['validation_report.json'] = json.dumps(report,indent=2,ensure_ascii=False)+'\n'
            if target.exists():
                for name,content in artifacts.items():
                    if not (target/name).is_file() or (target/name).read_bytes()!=content.encode():
                        raise ValueError('Existing run output differs; it will not be overwritten')
            else:
                output_root.mkdir(parents=True,exist_ok=True)
                with tempfile.TemporaryDirectory(prefix='.pending-',dir=output_root) as staging:
                    staged = Path(staging)
                    for name,content in artifacts.items():
                        (staged/name).write_text(content,encoding='utf-8',newline='\n')
                    staged.rename(target)
        except (ValueError,OSError) as exc:
            report['errors'].append(dict(reason=str(exc)))
    if report['errors']:
        report.update(state='validation_failed',ready_for_python_powerbi=False,unique_observations=0,imported_files=0)
    status_path.parent.mkdir(parents=True,exist_ok=True)
    status_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    return report, 1 if report['errors'] else (0 if report['ready_for_python_powerbi'] else 2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['inspect','init','run'])
    parser.add_argument('--file',type=Path)
    parser.add_argument('--input-dir',type=Path,default=ROOT/'data/raw/manual')
    args = parser.parse_args()
    try:
        if args.command == 'init':
            if not args.file:
                parser.error('init requires --file')
            init_metadata(args.file)
        elif args.command == 'inspect':
            inspect_files(args.input_dir)
        else:
            report,code = run(args.input_dir,ROOT/'data/processed/manual',ROOT/'docs/manual_ingestion_status.json')
            print(json.dumps({k:report[k] for k in ('state','imported_files','unique_observations','ready_for_python_powerbi','errors')},indent=2,ensure_ascii=False))
            return code
    except (ValueError,OSError,KeyError,TypeError,zipfile.BadZipFile) as exc:
        print(f'Manual ingestion blocked: {exc}',file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
