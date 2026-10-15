"""Verify immutable inputs and reproduce the reporting scripts and acceptance files.

Run from the repo root: python -m powerbi.prepare_package [--check]
All writes are confined to generated files under powerbi/. No Microsoft engine
is run: the DAX reference evaluator is deliberately limited and documented.
"""
import argparse
from decimal import Decimal
import csv
import hashlib
from io import StringIO
import json
import math
from pathlib import Path

import pandas as pd

from src.dashboard_data import load_dashboard
from src.eda_analysis import load_inputs
from powerbi.dax_reference import evaluate, parse_measures, validate_bindings

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'powerbi'
CONTRACT = PACKAGE / 'model_contract.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'


def csv_text(rows, columns=None):
    out = StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=columns or list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def parse_value(value, column):
    """Strict reviewed types: empty nullable cells only; never NA-token guessing."""
    if value == '':
        if column['nullable']:
            return None
        raise ValueError(f"Required value missing: {column['name']}")
    kind = column['type']
    if kind == 'text':
        return value
    if kind == 'integer':
        number = Decimal(value)
        if not number.is_finite() or number != number.to_integral_value() or not -(2**63) <= number < 2**63:
            raise ValueError(f"Not a whole Int64: {column['name']}")
        return int(number)
    if kind == 'decimal':
        number = float(value)
        if not math.isfinite(number):
            raise ValueError(f"Nonfinite number: {column['name']}")
        return number
    if kind == 'boolean':
        if value not in ('True', 'False'):
            raise ValueError(f"Noncanonical Boolean: {column['name']}")
        return value == 'True'
    if kind == 'date':
        parsed = pd.to_datetime(value, format='%Y-%m-%d', errors='raise')
        if parsed.strftime('%Y-%m-%d') != value:
            raise ValueError('Noncanonical ISO date')
        return parsed.date()
    raise ValueError(f'Unknown type {kind}')


def load_tables(model, root=ROOT):
    folder = root / model['eda_directory']
    if sha(folder / 'analysis_manifest.json') != model['eda_manifest_sha256']:
        raise ValueError('Pinned EDA manifest mismatch')
    tables = {}
    for name, spec in model['tables'].items():
        path = folder / spec['file']
        if sha(path) != spec['sha256']:
            raise ValueError(f'Checksum mismatch: {name}')
        with path.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.reader(stream, strict=True)
            if next(reader) != [c['name'] for c in spec['columns']]:
                raise ValueError(f'Unexpected headers: {name}')
            records = []
            for row in reader:
                if len(row) != len(spec['columns']):
                    raise ValueError(f'Unexpected field count: {name}')
                records.append([parse_value(value, col) for value, col in zip(row, spec['columns'])])
        frame = pd.DataFrame(records, columns=[c['name'] for c in spec['columns']])
        if len(frame) != spec['rows']:
            raise ValueError(f'Unexpected row count: {name}')
        tables[name] = frame
    return tables


def validate_model(model, tables):
    for name, spec in model['tables'].items():
        frame = tables[name]
        if spec['role'] == 'dimension':
            if not frame[spec['key']].is_unique or frame[spec['key']].isna().any():
                raise ValueError(f'Invalid dimension key: {name}')
        if spec['role'] == 'fact':
            if frame.duplicated(spec['grain']).any():
                raise ValueError(f'Fact grain repeated: {name}')
            count = frame.reported_record_count
            if count.sum() != spec['total'] or not count.gt(0).all():
                raise ValueError(f'Fact totals invalid: {name}')
            if not frame.records_in_repeated_groups.between(0, count).all():
                raise ValueError(f'Invalid repeated group counts: {name}')
            scopes = frame.merge(tables['dim_dataset'], on='dataset_id', validate='many_to_one').scope_id
            if set(scopes) != {spec['scope_id']}:
                raise ValueError(f'Mixed source definitions: {name}')
            gov = frame.merge(tables['dim_wilayat'], on='wilayat_key', validate='many_to_one')
            if not gov.governorate_id_x.equals(gov.governorate_id_y):
                raise ValueError(f'Governorate / wilayat disagreement: {name}')
            for dataset_id, actual in frame.groupby('dataset_id').reported_record_count.sum().items():
                expected = tables['dim_dataset'].set_index('dataset_id').loc[dataset_id, 'reported_record_count']
                if actual != expected:
                    raise ValueError(f'Dataset subtotal mismatch: {dataset_id}')
    edges = set()
    for rel in model['relationships']:
        source, target = rel['from_table'], rel['to_table']
        if (model['tables'][source]['role'] != 'dimension' or model['tables'][target]['role'] != 'fact'
                or rel['cardinality'] != 'one_to_many' or rel['cross_filter'] != 'single' or not rel['active']):
            raise ValueError('Only direct active dimension-to-fact single-direction relationships allowed')
        edge = (source, target)
        if edge in edges:
            raise ValueError('Multiple filter paths')
        edges.add(edge)
        values = tables[target][rel['to_column']]
        if values.isna().any() or not set(values) <= set(tables[source][rel['from_column']]):
            raise ValueError(f'Orphaned foreign key: {edge}')
        source_type = next(c['type'] for c in model['tables'][source]['columns'] if c['name'] == rel['from_column'])
        target_type = next(c['type'] for c in model['tables'][target]['columns'] if c['name'] == rel['to_column'])
        if source_type != target_type:
            raise ValueError(f'Relationship type mismatch: {edge}')
    if len(edges) != 19:
        raise ValueError('Reviewed model requires exactly 19 relationships')
    actual_periods = set().union(*(set(tables[n].period_id) for n,s in model['tables'].items() if s['role']=='fact'))
    if set(tables['dim_period'].period_id) != actual_periods:
        raise ValueError('Period dimension must contain only observed months')
    coverage = tables['coverage_matrix_2020_2026']
    if coverage.duplicated(['scope_id', 'governorate_id', 'year', 'month']).any():
        raise ValueError('Repeated coverage cell')
    unavailable = coverage.availability_status.ne('observed')
    if not coverage.loc[unavailable, 'reported_record_count'].isna().all():
        raise ValueError('Unavailable coverage must stay blank')
    for scope, cohort in coverage[~unavailable].groupby('scope_id'):
        name = next(n for n, s in model['tables'].items() if s.get('scope_id') == scope)
        actual = tables[name].groupby(['period_id', 'governorate_id']).reported_record_count.sum().to_dict()
        expected = {(f'{r.year}-{r.month:02}', r.governorate_id): int(r.reported_record_count)
                    for r in cohort.itertuples()}
        if actual != expected:
            raise ValueError(f'Coverage does not reconcile: {scope}')


def catalogue(measures):
    result = []
    for name in measures:
        family = 'land_2022' if name.startswith('Land 2022') else 'land_2024' if name.startswith('Land Oct 2024') else 'brokerage_2025'
        if name.endswith(('Reported Records', 'Registrations')):
            kind = 'count'
        elif name.endswith('Geographic Share'):
            kind = 'geographic_share'
        elif name.endswith('Property Use Share'):
            kind = 'property_use_share'
        elif name.endswith('Supplied Governorates'):
            kind = 'governorates'
        elif name.endswith('Supplied Months'):
            kind = 'months'
        elif name.endswith('Repeated Group Share'):
            kind = 'repeated_share'
        elif name.endswith('November Rows'):
            kind = 'november'
        elif name.endswith('December Rows'):
            kind = 'december'
        elif name.endswith('Row Difference'):
            kind = 'difference'
        elif name.endswith('Row Change'):
            kind = 'change'
        else:
            raise ValueError(f'Unreviewed measure: {name}')
        percentage = 'share' in kind or kind == 'change'
        result.append(dict(measure=name, home_table='fact_'+family, family=family, kind=kind,
                           format='0.00%' if percentage else '#,0;(#,0);0'))
    return result


def contexts(tables):
    result = [('unfiltered', {})]
    for table, col in [('dim_dataset','dataset_id'), ('dim_period','period_id'),
                       ('dim_governorate','governorate_id'), ('dim_wilayat','wilayat_key'),
                       ('dim_buyer_type','buyer_type'), ('dim_ownership_band','ownership_band'),
                       ('dim_service_code','service_sub_id'), ('dim_property_use','property_use_key'),
                       ('dim_property_description','property_description_key')]:
        # Every real dimension value, not simulated observations.
        for value in tables[table][col]:
            result.append((f'{table}:{value}', {(table, col): {value}}))
    result += [
        ('scope_land_2022', {('dim_dataset','scope_id'):{'land_buy_sell_2022'}}),
        ('scope_land_2024', {('dim_dataset','scope_id'):{'land_service_coded_2024'}}),
        ('scope_brokerage', {('dim_dataset','scope_id'):{'muscat_brokerage_registration_2025'}}),
        ('muscat_nov_individual', {('dim_governorate','governorate_id'):{'muscat'},
                                 ('dim_period','period_id'):{'2022-11'}, ('dim_buyer_type','buyer_type'):{'Individual'}}),
        ('incompatible_governorate_and_wilayat', {('dim_governorate','governorate_id'):{'dhofar'},
                                                ('dim_wilayat','wilayat_key'):{'muscat|السيب'}}),
        ('no_period_selected', {('dim_period','period_id'):set()}),
        ('missing_real_period_2023_01', {('dim_period','period_id'):{'2023-01'}}),
        ('brokerage_seeb_residential', {('dim_dataset','scope_id'):{'muscat_brokerage_registration_2025'},
                                      ('dim_wilayat','wilayat_key'):{'muscat|السيب'},
                                      ('dim_property_use','property_use_key'):{'سكني'}}),
    ]
    return result


def enriched_originals(model, tables, inputs):
    result = {}
    for family, source in inputs['facts'].items():
        frame = source.copy()
        for rel in model['relationships']:
            if rel['to_table'] == 'fact_'+family:
                dim = rel['from_table']
                right = tables[dim].add_prefix(dim+'.')
                frame = frame.merge(right, left_on=rel['to_column'], right_on=dim+'.'+rel['from_column'],
                                    validate='many_to_one', how='left')
        if len(frame) != len(source):
            raise ValueError('Original-row join changed occurrence count')
        result[family] = frame
    return result


def oracle(spec, context, originals):
    """Independent source-row arithmetic; does not use aggregate fact weights."""
    def rows(ctx):
        frame = originals[spec['family']]
        for (table, col), allowed in ctx.items():
            name = table+'.'+col
            if name in frame:
                frame = frame[frame[name].isin(allowed)]
        return frame
    def count(ctx):
        frame = rows(ctx)
        return len(frame) if len(frame) else None
    def divide(n, d):
        return None if n is None or not d else n/d
    kind = spec['kind']
    current = rows(context)
    numerator = len(current) if len(current) else None
    if kind == 'count':
        return numerator
    if kind in {'governorates', 'months'}:
        return None if current.empty else int(current['governorate_id' if kind == 'governorates' else 'period_id'].nunique())
    if kind == 'repeated_share':
        return divide(int(current.in_repeated_group.sum()), numerator)
    if kind in {'geographic_share', 'property_use_share'}:
        clear = {'dim_governorate','dim_wilayat'} if kind == 'geographic_share' else {'dim_property_use'}
        denominator_context = {key:value for key,value in context.items() if key[0] not in clear}
        return divide(numerator, count(denominator_context))
    comparison_context = {key:value for key,value in context.items() if key[0] not in {'dim_period','dim_dataset'}}
    nov = count({**comparison_context, ('dim_period','period_id'):{'2022-11'}})
    dec = count({**comparison_context, ('dim_period','period_id'):{'2022-12'}})
    if kind == 'november':
        return nov
    if kind == 'december':
        return dec
    difference = None if nov is None or dec is None else dec-nov
    return divide(difference, nov) if kind == 'change' else difference


def m_string(value):
    return '"' + value.replace('"', '""') + '"'


def generate_m(name, spec):
    columns = ',\n'.join('    [Name='+m_string(c['name'])+', Kind='+m_string(c['type'])+
                           ', Nullable='+str(c['nullable']).lower()+']' for c in spec['columns'])
    return ('// Generated from model_contract.json; do not edit this query independently.\n'
            'let\n    Schema = {\n'+columns+'\n    },\n    Imported = fnAuditedCsv('+m_string(spec['file'])+
            ', Schema, '+str(spec['rows'])+', '+str(spec.get('total','null'))+')\nin\n    Imported\n')


def dax_context(expression, context):
    if not context:
        return expression
    filters = []
    for (table, col), values in sorted(context.items()):
        literals = ', '.join(m_string(str(v)) for v in sorted(values))
        target = "'"+table+"'["+col+"]"
        source = '{'+literals+'}' if values else 'FILTER ( ALL ( '+target+' ), FALSE () )'
        filters.append('TREATAS ( '+source+', '+target+' )')
    return 'CALCULATE ( '+expression+', '+', '.join(filters)+' )'


def acceptance_query(case, context, specs, expected):
    rows = []
    for spec in specs:
        name = spec['measure']
        value = expected[name]
        literal = 'BLANK ()' if value is None else repr(value)
        actual = dax_context('['+name+']', context)
        passed = (f'VAR Actual = {actual} RETURN '
                  f'IF ( ISBLANK ( Actual ), ISBLANK ( {literal} ), '
                  f'NOT ( ISBLANK ( {literal} ) ) && ABS ( Actual - ({literal}) ) < 0.000000001 )')
        rows.append('    ROW ( "Measure", '+m_string(name)+', "Actual", '+actual+
                    ', "Expected", '+literal+', "Pass", '+passed+' )')
    return ('-- Desktop DAX query view; measures must already exist. Case: '+case+'\n'
            '-- Every Pass must be TRUE; blank and zero are intentionally different.\nEVALUATE\nUNION (\n'+',\n'.join(rows)+'\n)\n')


def build():
    # Existing reader verifies originals, all audited/EDA bytes and completed duplicate audit.
    bundle = load_dashboard()
    inputs = load_inputs()
    model = json.loads(CONTRACT.read_text())
    if model['eda_directory'] != bundle['config']['eda_directory']:
        raise ValueError('Model pin differs from reviewed dashboard pin')
    if model['coverage_as_of'] != inputs['audit_report']['audit_as_of']:
        raise ValueError('Coverage snapshot date mismatch')
    tables = load_tables(model)
    validate_model(model, tables)
    measures = parse_measures((PACKAGE/'EDA_MEASURES.dax').read_text())
    validate_bindings(measures, tables)
    specs = catalogue(measures)
    originals = enriched_originals(model, tables, inputs)
    files = {f'm/{name}.pq': generate_m(name, spec) for name, spec in model['tables'].items()}
    files['RELATIONSHIPS.csv'] = csv_text(model['relationships'])
    files['MEASURE_CATALOG.csv'] = csv_text(specs)
    schema = ['# Verified import schema', '', 'Generated from `model_contract.json`; no inferred Desktop types. All columns use Do not summarize unless an explicit measure aggregates them. Dates are metadata only.', '',
              '| Table | Role | CSV rows | Source occurrences (SUM weights) |', '|---|---|---:|---:|']
    for name, spec in model['tables'].items():
        schema.append(f"| {name} | {spec['role']} | {spec['rows']} | {spec.get('total','—')} |")
    for name, spec in model['tables'].items():
        schema += ['', '## '+name, '']
        if 'grain' in spec:
            schema += ['Unique aggregate grain: '+', '.join('`'+c+'`' for c in spec['grain'])+'.', '']
        if 'key' in spec:
            schema += ['Unique non-null key: `'+spec['key']+'`.', '']
        schema += ['| Column | Power Query / Desktop type | Nullable |', '|---|---|---|']
        types = {'text':'Text','integer':'Int64 / Whole number','decimal':'Decimal number','boolean':'True/False','date':'Date (ISO yyyy-MM-dd)'}
        schema += [f"| {c['name']} | {types[c['type']]} | {'yes' if c['nullable'] else 'no'} |" for c in spec['columns']]
    files['SCHEMA.md'] = '\n'.join(schema)+'\n'
    vectors = []
    cases = contexts(tables)
    selected_cases = {'unfiltered','scope_land_2022','scope_land_2024','scope_brokerage',
                      'muscat_nov_individual','incompatible_governorate_and_wilayat',
                      'no_period_selected','missing_real_period_2023_01','brokerage_seeb_residential'}
    for case_id, (case, context) in enumerate(cases):
        expected = {}
        for spec in specs:
            name = spec['measure']
            actual = evaluate(name, measures, context, tables, model['relationships'])
            value = oracle(spec, context, originals)
            if ((actual is None) != (value is None) or
                    (value is not None and not math.isclose(actual, value, rel_tol=1e-12, abs_tol=1e-12))):
                raise ValueError(f'DAX reference/source-row disagreement: {case} / {name}: {actual} vs {value}')
            expected[name] = value
            vectors.append(dict(case=case, filters=json.dumps({t+'.'+c:sorted(v) for (t,c),v in context.items()},ensure_ascii=False,sort_keys=True),
                                measure=name, expected=value, python_reference=actual, passed=True))
        if case in selected_cases:
            files[f'validation/desktop_{case_id:03}.dax'] = acceptance_query(case, context, specs, expected)
    files['validation/measure_test_vectors.csv'] = csv_text(vectors)
    unfiltered = {v['measure']:v['expected'] for v in vectors if v['case']=='unfiltered'}
    report = dict(status='python_model_and_reference_checks_passed; Desktop_acceptance_pending',
                  microsoft_dax_engine_executed=False, microsoft_power_query_engine_executed=False,
                  pbix_created=False, data_modified=False, tables=len(tables), relationships=len(model['relationships']),
                  measures=len(measures), filter_contexts=len(cases), semantic_checks=len(vectors),
                  coverage_as_of=model['coverage_as_of'],
                  coverage_cells_by_status={k:int(v) for k,v in tables['coverage_matrix_2020_2026'].availability_status.value_counts().sort_index().items()},
                  fact_reconciliation=bundle['manifest']['fact_reconciliation'],
                  original_sha256=bundle['manifest']['original_sha256'],
                  parent_audit_manifest_sha256=bundle['manifest']['input_manifest_sha256'],
                  unfiltered_measure_results=unfiltered,
                  input_sha256={str(CONTRACT.relative_to(ROOT)):sha(CONTRACT),
                                'powerbi/EDA_MEASURES.dax':sha(PACKAGE/'EDA_MEASURES.dax'),
                                'powerbi/m/fnAuditedCsv.pq':sha(PACKAGE/'m/fnAuditedCsv.pq'),
                                'powerbi/m/pRepositoryRoot.pq':sha(PACKAGE/'m/pRepositoryRoot.pq'),
                                **{str((ROOT/model['eda_directory']/s['file']).relative_to(ROOT)):s['sha256'] for s in model['tables'].values()}},
                  generated_sha256={name:hashlib.sha256(text.encode()).hexdigest() for name,text in sorted(files.items())})
    files['validation/validation_results.json'] = json_text(report)
    return files, report


def run(check=False):
    files, report = build()
    for relative, text in files.items():
        path = PACKAGE/relative
        if check:
            if not path.exists() or path.read_bytes() != text.encode():
                raise ValueError(f'Stale or missing generated file: {relative}; regenerate the package')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(text.encode())
    print(json_text({key:report[key] for key in ['status','tables','relationships','measures','filter_contexts','semantic_checks','pbix_created']}))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Read-only reproducibility check')
    run(parser.parse_args().check)
