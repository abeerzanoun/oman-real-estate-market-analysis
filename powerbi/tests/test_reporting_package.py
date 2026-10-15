"""Real-input model and formula checks; no generated market observations."""
import copy
import hashlib
import json
import re

import pytest

from powerbi.dax_reference import evaluate, parse_measures, validate_bindings
from powerbi.prepare_package import (
    CONTRACT, PACKAGE, ROOT, build, load_tables, parse_value, validate_model,
)


@pytest.fixture(scope='module')
def model():
    return json.loads(CONTRACT.read_text(encoding='utf-8'))


@pytest.fixture(scope='module')
def tables(model):
    return load_tables(model)


@pytest.fixture(scope='module')
def measures():
    return parse_measures((PACKAGE/'EDA_MEASURES.dax').read_text(encoding='utf-8'))


def test_generated_package_is_reproducible_and_preserves_originals():
    original_paths = list((ROOT/'data/raw/manual').glob('*.xlsx'))
    before = {p:hashlib.sha256(p.read_bytes()).hexdigest() for p in original_paths}
    files, report = build()
    assert len(before) == 4
    assert before == {p:hashlib.sha256(p.read_bytes()).hexdigest() for p in original_paths}
    for name, text in files.items():
        assert (PACKAGE/name).read_bytes() == text.encode(), name
    assert report['tables'] == 16 and report['relationships'] == 19
    assert report['measures'] == 17 and report['semantic_checks'] == 2227
    assert report['filter_contexts'] == 131
    assert not report['microsoft_dax_engine_executed'] and not report['pbix_created']


def test_verified_model_and_no_implicit_metadata_links(model, tables):
    validate_model(model, tables)
    for rel in model['relationships']:
        assert rel['from_table'].startswith('dim_')
        assert rel['to_table'].startswith('fact_')
    assert len(tables['coverage_matrix_2020_2026']) == 2772
    assert tables['coverage_matrix_2020_2026'].reported_record_count.isna().sum() == 2730
    assert set(tables['dim_service_code'].definition_status) == {'meaning_unverified'}
    assert not tables['data_quality_summary'].monetary_unit_verified.any()


def test_duplicate_dimension_keys_are_rejected(model, tables):
    altered = dict(tables)
    altered['dim_governorate'] = tables['dim_governorate'].copy()
    altered['dim_governorate'].loc[1,'governorate_id'] = altered['dim_governorate'].loc[0,'governorate_id']
    with pytest.raises(ValueError, match='Invalid dimension key'):
        validate_model(model, altered)


def test_orphan_fact_key_is_rejected(model, tables):
    altered = dict(tables)
    altered['fact_land_2022'] = tables['fact_land_2022'].copy()
    altered['fact_land_2022'].loc[0,'buyer_type'] = '__INVALID_KEY__'
    with pytest.raises(ValueError, match='Orphaned foreign key'):
        validate_model(model, altered)


def test_disallowed_relationship_direction_is_rejected(model, tables):
    altered = copy.deepcopy(model)
    altered['relationships'][0]['cross_filter'] = 'both'
    with pytest.raises(ValueError, match='single-direction'):
        validate_model(altered, tables)


def test_unknown_dax_column_and_text_sum_fail_closed(measures, tables):
    text = (PACKAGE/'EDA_MEASURES.dax').read_text(encoding='utf-8')
    with pytest.raises(ValueError, match='Unknown column'):
        validate_bindings(parse_measures(text.replace('[reported_record_count]', '[absent_column]')), tables)
    with pytest.raises(ValueError, match='numeric column'):
        validate_bindings(parse_measures(text.replace('[reported_record_count]', '[dataset_id]')), tables)
    validate_bindings(measures, tables)


def test_unreviewed_dax_function_is_rejected(tables):
    text = (PACKAGE/'EDA_MEASURES.dax').read_text(encoding='utf-8').replace('SUM (', 'COUNTROWS (', 1)
    with pytest.raises(ValueError, match='Unsupported function'):
        validate_bindings(parse_measures(text), tables)


def test_observed_totals_and_blank_are_different(model, tables, measures):
    args = (tables, model['relationships'])
    assert evaluate('Land 2022 Reported Records', measures, {}, *args) == 13168
    assert len(tables['fact_land_2022']) == 361
    assert evaluate('Land Oct 2024 Repeated Group Share', measures, {}, *args) == 0
    context = {('dim_period','period_id'):{'2023-01'}}
    assert evaluate('Land Oct 2024 Repeated Group Share', measures, context, *args) is None
    assert evaluate('Land 2022 Reported Records', measures, context, *args) is None


def test_comparison_explicitly_clears_dataset_and_period_but_keeps_geography(model, tables, measures):
    context = {('dim_period','period_id'):{'2024-10'}, ('dim_dataset','dataset_id'):{'land_oct_2024'},
               ('dim_governorate','governorate_id'):{'muscat'}}
    args = (tables, model['relationships'])
    assert evaluate('Land 2022 November Rows', measures, context, *args) == 960
    assert evaluate('Land 2022 December Rows', measures, context, *args) == 734
    assert evaluate('Land 2022 Nov Dec Row Difference', measures, context, *args) == -226


def test_geographic_share_keeps_period_but_clears_both_geography_dimensions(model, tables, measures):
    context = {('dim_period','period_id'):{'2022-11'}, ('dim_governorate','governorate_id'):{'muscat'}}
    assert evaluate('Land 2022 Geographic Share', measures, context, tables, model['relationships']) == pytest.approx(960/7501)


def test_integrity_failure_rejects_changed_csv(tmp_path, model):
    folder = tmp_path/model['eda_directory']
    folder.mkdir(parents=True)
    original = ROOT/model['eda_directory']
    (folder/'analysis_manifest.json').write_bytes((original/'analysis_manifest.json').read_bytes())
    first = next(iter(model['tables'].values()))['file']
    (folder/first).write_bytes((original/first).read_bytes()+b'\n')
    with pytest.raises(ValueError, match='Checksum mismatch'):
        load_tables(model, tmp_path)


def test_nullable_whole_numbers_do_not_round_or_impute():
    spec = {'name':'reported_amount_missing_records','type':'integer','nullable':True}
    assert parse_value('367.0', spec) == 367
    assert parse_value('', spec) is None
    with pytest.raises(ValueError, match='whole Int64'):
        parse_value('367.5', spec)
    with pytest.raises(ValueError, match='Required value'):
        parse_value('', {**spec,'nullable':False})


def test_m_syntax_report_covers_all_current_queries():
    report = json.loads((PACKAGE/'validation/m_syntax_results.json').read_text(encoding='utf-8'))
    assert not report['microsoft_power_query_engine_executed']
    assert {r['file'] for r in report['queries']} == {str(p.relative_to(PACKAGE)) for p in (PACKAGE/'m').glob('*.pq')}
    for result in report['queries']:
        assert result['syntax'] == 'passed'
        assert result['sha256'] == hashlib.sha256((PACKAGE/result['file']).read_bytes()).hexdigest()


def test_desktop_acceptance_queries_require_engine_checks_and_separate_blank():
    paths = sorted((PACKAGE/'validation').glob('desktop_*.dax'))
    assert len(paths) == 9
    for path in paths:
        text = path.read_text(encoding='utf-8')
        assert text.count('ROW ( "Measure"') == 17
        assert 'ISBLANK' in text and '"Pass"' in text and 'EVALUATE' in text
        assert 'TREATAS ( {}' not in text


def test_package_links_and_theme_json_are_well_formed():
    theme = json.loads((PACKAGE/'report_theme.json').read_text(encoding='utf-8'))
    assert len(theme['dataColors']) == 8
    assert all(re.fullmatch('#[0-9A-Fa-f]{6}', color) for color in theme['dataColors'])
    for path in PACKAGE.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if not target.startswith(('https://','http://','#')):
                assert (path.parent/target.split('#')[0]).exists(), (path.name,target)
