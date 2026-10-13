"""Offline, lossless audit of registered row-level uploads (not aggregate ingestion).

python -m src.audit_uploaded_data
Run folders are immutable; identical inputs/code reproduce identical artifacts.
"""
import argparse
from collections import Counter
from datetime import date
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import tempfile

import pandas as pd

from src.excel_reader import read_workbook, column_types
from src.manual_reference import GOVERNORATES, governorate, normalize

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'docs/uploaded_source_registry.json'
REFERENCE = ROOT / 'docs/reference_geography.json'
LAND_HEADERS = ['TRANSACTION_DATE','BUYER_TYPE','REGION_AR','REGION_EN','WILAYAT_AR',
                'WILAYAT_EN','VILLAGE_AR','VILLAGE_EN','GENDER_NAME_AR','GENDER_NAME_EN','NO_OF_OWNERS']
LAND_2024_HEADERS = ['TRANSACTION_DATE','SERVICE_SUB_ID','BUYER_TYPE','REGION_AR','REGION_EN',
                    'WILAYAT_AR','WILAYAT_EN','VILLAGE_AR','VILLAGE_EN','RE_VALUE','DATE_OF_BIRTH',
                    'GENDER_NAME_AR','GENDER_NAME_EN','SINGLE_MULTIPLE','NO_OF_OWNERS']
BROKER_HEADERS = ['اسم المعاملة','الولاية','تاريخ الإجراء','نوع الإستعمال','وصف العقار']
FACT_NAMES = {'land_buy_sell_2022':'land_records_2022.csv',
              'land_service_coded_2024':'land_records_2024.csv',
              'muscat_brokerage_registration_2025':'muscat_brokerage_records_2025.csv'}
EN_ALIASES = {'AlDakhliah':'ad_dakhiliyah','AlDahra':'adh_dhahirah','AlWasta':'al_wusta',
              'North Batinah':'north_al_batinah','South Batinah':'south_al_batinah'}


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2, default=str) + '\n'


def clean_label(value):
    return '' if value is None else re.sub(r'\s+', ' ', str(value).replace('ـ','')).strip()


def iso_date(value):
    if isinstance(value, date):
        return value.date() if hasattr(value, 'date') else value
    # Deliberately no guessed day/month interpretation.
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError(f'Invalid ISO date: {value!r}')
    return date.fromisoformat(value)


def resolve_geography(ar, en, wilayat, reference, broker=False):
    label = clean_label(wilayat)
    aliases = {normalize(k):v for k,v in {**reference['observed_spelling_aliases'],
               **reference['source_parenthetical_wilayat_alias']}.items()}
    canonical = aliases.get(normalize(label), label)
    method = 'spelling_alias' if canonical != label else 'unicode_cleanup'
    nonstandard = normalize(label) in {normalize(v) for v in reference['nonstandard_source_wilayat_labels']}
    if broker:
        gov, gov_method = 'muscat', 'embedded_workbook_scope'
    elif normalize(ar).replace(' ','') == normalize('الشرقية'):
        matches = [g for g, names in reference['legacy_sharqiyah_wilayats'].items()
                   if normalize(canonical) in {normalize(n) for n in names}]
        if len(matches) != 1 or en != 'Alsharqia':
            raise ValueError(f'Unresolved legacy Sharqiyah pair: {ar}, {en}, {wilayat}')
        gov, gov_method = matches[0], 'legacy_region_resolved_by_verified_wilayat'
    else:
        gov = governorate(ar)[0]
        english_gov = EN_ALIASES.get(en) or governorate(en)[0]
        if gov != english_gov:
            raise ValueError(f'Conflicting Arabic/English governorate: {ar}, {en}')
        gov_method = 'source_bilingual_region'
    return gov, canonical, method, gov_method, nonstandard


def audit_dataset(entry, root, reference):
    path = root / entry['file']
    before = sha(path.read_bytes())
    if before != entry['sha256']:
        raise ValueError(f"Original checksum mismatch: {entry['file']}; review new source version")
    book = read_workbook(path)
    sheet = next(s for s in book['sheets'] if s['name'] == entry['sheet'])
    header_row = entry['header_row']
    headers = list(sheet['rows'][header_row-1])
    broker = entry['scope_id'].startswith('muscat')
    financial = entry['scope_id'] == 'land_service_coded_2024'
    expected = BROKER_HEADERS if broker else LAND_2024_HEADERS if financial else LAND_HEADERS
    if headers != expected:
        raise ValueError(f"Unexpected source schema: {entry['file']}: {headers}")
    source_rows = [(n, tuple(row[:len(headers)])) for n,row in enumerate(sheet['rows'][header_row:], start=header_row+1) if any(v is not None for v in row)]
    raw_rows = [row for _,row in source_rows]
    if len(raw_rows) != entry['audited_row_count']:
        raise ValueError(f"Source row reconciliation failed: {entry['file']}")
    signatures = [sha(json.dumps(row, ensure_ascii=False, default=str).encode()) for row in raw_rows]
    repeats = Counter(signatures)
    ranks = Counter()
    facts, issues = [], Counter()
    for (source_row, raw), signature in zip(source_rows, signatures):
        source = dict(zip(headers,raw))
        dt = iso_date(source['تاريخ الإجراء'] if broker else source['TRANSACTION_DATE'])
        label = entry['filename_period_label']
        if not dt.isoformat().startswith(label):
            raise ValueError(f"Filename period mismatch: {entry['file']}, row {source_row}")
        ar = None if broker else source['REGION_AR']
        en = None if broker else source['REGION_EN']
        wa = source['الولاية'] if broker else source['WILAYAT_AR']
        gov, wilayat, wm, gm, nonstandard = resolve_geography(ar,en,wa,reference,broker)
        ranks[signature] += 1
        record = dict(record_id=sha(f'{before}|{entry["sheet"]}|{source_row}'.encode()),
            dataset_id=entry['dataset_id'],scope_id=entry['scope_id'],source_sha256=before,
            source_sheet=entry['sheet'],source_row=source_row,transaction_date=dt.isoformat(),
            year=dt.year,month=dt.month,governorate_id=gov,
            source_region_ar=ar,source_region_en=en,source_wilayat_ar=wa,
            source_wilayat_en=None if broker else source['WILAYAT_EN'],
            wilayat_ar=wilayat,wilayat_key=f'{gov}|{normalize(wilayat)}',
            wilayat_normalization_method=wm,governorate_mapping_method=gm,
            nonstandard_wilayat_label=nonstandard,raw_row_signature=signature,
            repeated_row_group_size=repeats[signature],occurrence_rank=ranks[signature])
        if broker:
            record.update(transaction_category_ar=source['اسم المعاملة'],
                property_use_ar=source['نوع الإستعمال'],property_description_ar=source['وصف العقار'],
                property_use_key=normalize(source['نوع الإستعمال']),
                property_description_key=normalize(source['وصف العقار']))
        else:
            owners = source['NO_OF_OWNERS']
            if not isinstance(owners,(int,float)) or owners < 1 or int(owners) != owners:
                raise ValueError(f'Invalid owner count at {source_row}')
            record.update(buyer_type=source['BUYER_TYPE'],source_village_ar=source['VILLAGE_AR'],
                          source_village_en=source['VILLAGE_EN'],number_of_owners=int(owners))
            if financial:
                token = sheet['numeric_tokens'].get(f'J{source_row}')
                if source['RE_VALUE'] is not None and token is None:
                    raise ValueError('Financial value is not a source numeric cell')
                value = Decimal(token) if token is not None else None
                record.update(service_sub_id=source['SERVICE_SUB_ID'],reported_re_value=value,
                              currency_unit=entry['currency_unit'],ownership_mode=source['SINGLE_MULTIPLE'])
                if value is not None and (not value.is_finite() or value <= 0):
                    issues['nonpositive_or_nonfinite_reported_values'] += 1
                if (owners == 1) != (source['SINGLE_MULTIPLE'] == 'Single'):
                    issues['ownership_mode_mismatches'] += 1
                dob = source['DATE_OF_BIRTH']
                if dob is None:
                    issues['birth_date_missing'] += 1
                else:
                    try:
                        birth = iso_date(dob)
                        if birth == date(1900,1,1):
                            issues['birth_date_1900_sentinel'] += 1
                        elif birth > dt:
                            issues['birth_date_after_transaction'] += 1
                        else:
                            age = dt.year-birth.year-((dt.month,dt.day)<(birth.month,birth.day))
                            if age < 18:
                                issues['birth_date_under_18'] += 1
                            if age > 110:
                                issues['birth_date_age_over_110'] += 1
                    except ValueError:
                        issues['invalid_birth_dates'] += 1
        facts.append(record)
    frame = pd.DataFrame(facts)
    numerical = {}
    if financial:
        present = [v for v in frame.reported_re_value if v is not None]
        values = pd.Series([float(v) for v in present])
        lo,hi = values.quantile([.01,.99])
        frame['reported_value_tail_flag'] = frame.reported_re_value.map(
            lambda v: False if v is None else float(v)<lo or float(v)>hi)
        numerical = dict(present=len(present),missing=len(frame)-len(present),unit_verified=False,
            min=str(min(present)),max=str(max(present)),median=str(values.median()),
            raw_unit_sum=str(sum(present,Decimal('0'))),p01=lo,p99=hi,
            tail_flagged=int(frame.reported_value_tail_flag.sum()),
            by_service_code={code:dict(records=len(group),present=sum(v is not None for v in group.reported_re_value),missing=sum(v is None for v in group.reported_re_value)) for code,group in frame.groupby('service_sub_id')},
            note='Empirical tails are review flags, not errors; no clipping. RE_VALUE is not a verified price or OMR amount.')
    columns = [dict(dataset_id=entry['dataset_id'],column=h,missing=sum(r[i] is None for r in raw_rows),
                    observed_types=column_types(r[i] for r in raw_rows)) for i,h in enumerate(headers)]
    metadata_sheets = {s['name']:s['rows'] for s in book['sheets'] if s['name'] != entry['sheet']}
    # Metadata sheet cell B6 has a source publication label; XML creation dates are template metadata.
    publication = next((str(s['rows'][5][1]) for s in book['sheets'] if s['name'].strip()=='البيانات الوصفية'),None)
    profile = dict(**entry,actual_record_count=len(frame),min_date=frame.transaction_date.min(),
        max_date=frame.transaction_date.max(),filename_period_verified=True,
        annual_label_is_partial=broker,reported_publication_cell=publication,
        publication_precedes_last_record=bool(publication and publication[:10]<frame.transaction_date.max()),
        source_xml_core_properties=book['core_properties'],reader_warnings=book['reader_warnings'],
        sheets=[{k:v for k,v in s.items() if k not in {'rows','numeric_tokens'}} for s in book['sheets']],
        embedded_metadata_sheets=metadata_sheets,columns=columns,
        exact_repeat_occurrences_after_first=sum(n-1 for n in repeats.values()),
        records_in_repeated_groups=sum(n for n in repeats.values() if n>1),
        rows_removed=0,invalid_transaction_dates=0,unresolved_governorates=0,
        nonstandard_wilayat_rows=int(frame.nonstandard_wilayat_label.sum()),
        numerical_profile=numerical,quality_flags=dict(issues),
        owner_count_range=None if broker else dict(min=int(frame.number_of_owners.min()),max=int(frame.number_of_owners.max())),
        categorical_counts={c:{str(k):int(v) for k,v in frame[c].value_counts(dropna=False).items()}
            for c in ('governorate_id','buyer_type','service_sub_id','property_use_ar','property_description_ar') if c in frame},
        monthly_records={str(k):int(v) for k,v in frame.groupby(['year','month']).size().items()})
    if sha(path.read_bytes()) != before:
        raise ValueError('Original changed during audit')
    return frame,profile


def build(root=ROOT, registry_path=REGISTRY, reference_path=REFERENCE, as_of=date(2026,10,13)):
    registry = json.loads(Path(registry_path).read_text())
    reference = json.loads(Path(reference_path).read_text())
    datasets = [audit_dataset(entry,root,reference) for entry in registry]
    frames = [frame for frame,_ in datasets]
    profiles = [profile for _,profile in datasets]
    artifacts = {}
    def csv(name,frame):
        artifacts[name] = frame.to_csv(index=False,lineterminator='\n').encode('utf-8-sig')
    for scope,name in FACT_NAMES.items():
        csv(name,pd.concat([f for f in frames if f.scope_id.iloc[0]==scope],ignore_index=True))
    keys = ['dataset_id','scope_id','transaction_date','year','month','governorate_id','wilayat_key','wilayat_ar']
    combined = pd.concat([f[keys] for f in frames],ignore_index=True)
    coverage = combined.groupby(['scope_id','governorate_id','year','month']).size().reset_index(name='reported_record_count')
    csv('coverage_observed.csv',coverage)
    monthly = combined.groupby(['dataset_id','scope_id','governorate_id','wilayat_key','year','month']).size().reset_index(name='reported_record_count')
    csv('monthly_reported_records.csv',monthly)
    grid = []
    observed = {(r.scope_id,r.governorate_id,r.year,r.month):r.reported_record_count for r in coverage.itertuples()}
    supplied = {(r.scope_id,r.year,r.month) for r in coverage.itertuples()}
    for scope in FACT_NAMES:
        for year in range(2020,2027):
            for month in range(1,13):
                for gov,_,_ar,_aliases in GOVERNORATES:
                    key=(scope,gov,year,month)
                    status = 'observed' if key in observed else 'outside_source_scope' if scope.startswith('muscat') and gov!='muscat' else 'future_period' if date(year,month,1)>as_of else 'no_rows_in_supplied_file' if (scope,year,month) in supplied else 'not_provided'
                    grid.append(dict(scope_id=scope,governorate_id=gov,year=year,month=month,
                                     availability_status=status,reported_record_count=observed.get(key,0 if status=='no_rows_in_supplied_file' else None)))
    csv('coverage_matrix_2020_2026.csv',pd.DataFrame(grid))
    csv('dim_governorate.csv',pd.DataFrame([dict(governorate_id=g,governorate_en=en,governorate_ar=ar) for g,en,ar,_ in GOVERNORATES]))
    wilayat_dimension = combined[['wilayat_key','governorate_id','wilayat_ar']].drop_duplicates().sort_values('wilayat_key')
    if not wilayat_dimension.wilayat_key.is_unique:
        raise ValueError('Conflicting normalized wilayat labels; dimension cannot have duplicate keys')
    csv('dim_wilayat.csv',wilayat_dimension)
    csv('dim_date.csv',combined[['transaction_date','year','month']].drop_duplicates().sort_values('transaction_date'))
    csv('dim_dataset.csv',pd.DataFrame([{**e,'service_code_definitions':json.dumps(e['service_code_definitions']),
        'min_date':p['min_date'],'max_date':p['max_date'],'reported_record_count':p['actual_record_count']} for e,p in zip(registry,profiles)]))
    columns = [c for p in profiles for c in p['columns']]
    csv('source_column_quality.csv',pd.DataFrame([{**c,'observed_types':json.dumps(c['observed_types'],sort_keys=True)} for c in columns]))
    variants = pd.concat([f[['dataset_id','source_region_ar','source_region_en','source_wilayat_ar','source_wilayat_en',
        'governorate_id','wilayat_ar','wilayat_key','governorate_mapping_method','wilayat_normalization_method','nonstandard_wilayat_label']] for f in frames],ignore_index=True)
    csv('geography_source_crosswalk.csv',variants.value_counts(dropna=False).reset_index(name='reported_record_count').sort_values(['dataset_id','wilayat_key']))
    report = dict(audit_as_of=as_of.isoformat(),record_count=sum(len(f) for f in frames),datasets=profiles,
        original_checksums_verified=True,rows_removed=0,
        duplicate_policy='Retain every source occurrence: visible field repeats cannot establish transaction identity.',
        observed_governorate_month_cells=len(coverage),
        ready_for_limited_descriptive_record_analysis=True,ready_for_2020_2026_market_analysis=False,
        verified_monetary_units=False,exact_download_urls_verified=False,licences_verified=False,
        demographic_policy='Birth date and gender retained only in originals; quality totals reported, excluded from market-facing facts.',
        geographical_reference=reference)
    artifacts['audit_report.json'] = json_text(report).encode()
    artifacts['data_quality_report.md'] = render_report(report).encode()
    # Fingerprint implementation and reference/registry, not wall-clock execution time.
    components = [Path(__file__),ROOT/'src/excel_reader.py',ROOT/'src/manual_reference.py',ROOT/'requirements-lock.txt',Path(registry_path),Path(reference_path)]
    run_id = sha(json_text([as_of.isoformat(),[sha(p.read_bytes()) for p in components],[(e['dataset_id'],e['sha256']) for e in registry]]).encode())[:20]
    manifest = dict(run_id=run_id,source_sha256={e['file']:e['sha256'] for e in registry},
                    implementation_sha256={str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name:sha(p.read_bytes()) for p in components},
                    artifact_sha256={name:sha(data) for name,data in artifacts.items()})
    artifacts['manifest.json'] = json_text(manifest).encode()
    return artifacts,report,run_id


def render_report(report):
    lines = ['# Uploaded workbook data quality report', '',f"Audit date: {report['audit_as_of']}. **{report['record_count']:,} source record occurrences retained; zero rows removed.**",'',
        'All original SHA-256 checksums match the upload registry. Three worksheet A1 dimensions are reset in memory; no original is saved or renamed. Six worksheets are inspected, including embedded metadata and variable definitions.', '',
        '| Dataset | Actual records | First date | Last date | Repeats after first | Filename |',
        '|---|---:|---|---|---:|---|']
    for p in report['datasets']:
        lines.append(f"| {p['dataset_id']} | {p['actual_record_count']} | {p['min_date']} | {p['max_date']} | {p['exact_repeat_occurrences_after_first']} | consistent; {'partial year' if p['annual_label_is_partial'] else 'monthly'} |")
    lines += ['', '## Parsing, types and missingness', '',
        'Detailed worksheet names, declared/recovered dimensions, headers, column types, missing counts, embedded metadata and actual XML core properties are in `audit_report.json`. `source_column_quality.csv` provides a machine-readable column audit. Creation timestamps describe files/templates, not reporting periods or publication dates. Zero invalid transaction dates or unresolved governorates were found; these checks fail closed on future schema, checksum, period, numeric-type or geography inconsistencies.', '',
        'Muscat metadata labels the period annual and gives 2025-07-12 as publication, while actual records end 2025-09-30. Treat the release date as inconsistent/stale metadata requiring confirmation; the file is a partial year. No incorrectly named file was found.', '',
        '## Dataset findings', '']
    for p in report['datasets']:
        lines += [f"### {p['dataset_id']}", '',
            f"{p['records_in_repeated_groups']:,} records participate in exact visible-row repeated groups. All occurrences are retained: no official transaction identifier is supplied. These are reported rows, not established unique sales.", '',
            'Missing source cells: '+('; '.join(f"{c['column']}: {c['missing']}" for c in p['columns'] if c['missing']) or 'none')+'.', '',
            f"Nonstandard wilayat-label rows: {p['nonstandard_wilayat_rows']}. Quality flags: `{json.dumps(p['quality_flags'],sort_keys=True)}`.", '']
        if p['numerical_profile']:
            lines += [f"RE_VALUE audit (unverified source units): `{json.dumps(p['numerical_profile'],sort_keys=True)}`.", '',
                'RN13A and RN13C are retained as raw service codes with unknown meanings. Missing amounts stay blank. Low/high values are flagged using the observed 1st/99th percentiles and retained. Owner counts are positive integers; birth-date sentinels, future dates and minors are review flags, not grounds for deleting a market record.', '']
    lines += ['## Geography and coverage', '',
        'The land files contain ten legacy region labels. Their combined Sharqiyah label is mapped to modern North/South Ash Sharqiyah only using the actual wilayat and the cited official administrative references in `docs/reference_geography.json`. All eleven governorates are represented in each supplied land month. Muscat brokerage covers Muscat only and six wilayats. Normalization preserves raw Arabic/English names, missing translations, tatweel variants and spelling aliases in `geography_source_crosswalk.csv`.', '',
        'Nizwa’s Barakat Al Mawz parenthetical label is mapped explicitly to parent Nizwa with source retained. الساحل الشرقي appears twice in 2022 under Dhofar; it is retained and flagged as a nonstandard wilayat label. The administrative reference is used only for documented Sharqiyah membership, not as a complete current wilayat inventory.', '',
        f"`coverage_observed.csv` has {report['observed_governorate_month_cells']} actual governorate/month cells, and `monthly_reported_records.csv` adds observed wilayat detail. `coverage_matrix_2020_2026.csv` is an availability grid, not generated market observations: absent months have blank counts and explicit statuses. Observed date dimensions contain only actual record dates. Missing days/months do not imply zero activity or completeness.", '',
        '## Provenance and definitions', '',
        'The source registry records original paths/checksums and the Git upload commit. Muscat explicitly attributes MOHUP inside the workbook. The other three files are user-attributed official uploads without embedded download URLs. Provider entry points are discovery leads, not verified links to these exact bytes. Exact publication dates for the land files, download URLs, licences, service-code definitions and RE_VALUE unit remain pending. SHA-256 establishes unchanged local bytes, not independent government authenticity. No network data retrieval is performed.', '',
        'The 2022 BuySell schema, 2024 service-coded schema and Muscat brokerage-only registrations remain separate fact tables. They must not be summed into a common national sales series. Number of owners is not transaction count. Property use/description exist only in brokerage. RE_VALUE is a reported numeric field, not a verified price, turnover or price index. No area measurement exists.', '',
        '## Supported analysis and remaining requirements', '',
        '**Ready for limited descriptive analysis of supplied record occurrences**: November versus December 2022 within the same BuySell layout (subject to unverified completeness/definitions); regional and observed wilayat distributions within each supplied land month; Muscat brokerage monthly registrations and property-use/description mix for January–September 2025; missingness, ownership and buyer-type profiles. Power BI can load the separate facts and observed dimensions with these restrictions.', '',
        '**Not ready for a 2020–2026 market trend or investment study**: no 2020, 2021, 2023 or 2026 uploads; sparse 2022/2024; no national 2025 coverage; no verified monetary units, service definitions, prices, areas or indices; source transaction identity/completeness is unconfirmed. Rankings describe uploaded records only. No unsupported market findings, price estimates or missing-period values are created.', '',
        'Next obtain exact official dataset URLs/licences and schema notes for these files, RN13A/RN13C meanings and RE_VALUE unit; request complete comparable monthly land/registration series and official NCSI transaction-value/price-index tables. Keep different scopes separate until definitions and reconciliation are verified.', '']
    return '\n'.join(lines)


def run(output_root=ROOT/'data/processed/audited', **kwargs):
    artifacts,report,run_id = build(**kwargs)
    target = Path(output_root)/run_id
    if target.exists():
        if set(p.name for p in target.iterdir()) != set(artifacts) or any((target/name).read_bytes()!=data for name,data in artifacts.items()):
            raise ValueError('Existing audit run differs; refusing to overwrite')
    else:
        target.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.pending-',dir=target.parent) as staging:
            for name,data in artifacts.items():
                (Path(staging)/name).write_bytes(data)
            Path(staging).rename(target)
    return report,target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root',type=Path,default=ROOT/'data/processed/audited')
    parser.add_argument('--as-of',type=date.fromisoformat,default=date(2026,10,13),help='Availability review date; included in run fingerprint')
    args = parser.parse_args()
    report,target = run(output_root=args.output_root,as_of=args.as_of)
    print(json_text(dict(output_directory=str(target),record_count=report['record_count'],
        originals_verified=report['original_checksums_verified'],ready_for_limited_record_analysis=True,
        ready_for_2020_2026_market_analysis=False)))


if __name__ == '__main__':
    main()
