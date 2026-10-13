"""Integration checks use the actual uploaded workbooks; no mock market records."""
from datetime import date
from io import BytesIO
import json
from pathlib import Path
import pytest
import pandas as pd

from src.audit_uploaded_data import ROOT, REGISTRY, build, run, sha, iso_date
from src.excel_reader import read_workbook
from src.manual_ingestion import run as aggregate_run


@pytest.fixture(scope='module')
def result():
    return build()


def table(result,name):
    return pd.read_csv(BytesIO(result[0][name]),encoding='utf-8-sig')


def test_real_periods_counts_and_originals(result):
    report=result[1]
    assert report['record_count']==28558
    assert [(p['actual_record_count'],p['min_date'],p['max_date']) for p in report['datasets']]==[
        (9366,'2025-01-02','2025-09-30'),(7501,'2022-11-01','2022-11-29'),
        (5667,'2022-12-04','2022-12-29'),(6024,'2024-10-01','2024-10-31')]
    for p in report['datasets']:
        assert sha((ROOT/p['file']).read_bytes())==p['sha256']
        assert p['filename_period_verified']


def test_dimensions_are_recovered_without_resaving(result):
    sheets=[s for p in result[1]['datasets'] for s in p['sheets']]
    assert len(sheets)==6
    assert sum(s['dimension_reset_required'] for s in sheets)==3
    assert [(s['declared_dimensions']['rows'],s['actual_dimensions']['rows']) for s in sheets if s['dimension_reset_required']]==[(1,7502),(1,5668),(1,6025)]
    for p in result[1]['datasets'][1:]:
        assert 'modified' not in p['source_xml_core_properties']


def test_repeats_remain_source_occurrences(result):
    profiles=result[1]['datasets']
    assert [p['exact_repeat_occurrences_after_first'] for p in profiles]==[6778,2629,1843,0]
    assert all(p['rows_removed']==0 for p in profiles)
    frame=table(result,'muscat_brokerage_records_2025.csv')
    assert len(frame)==9366 and frame.record_id.nunique()==9366
    assert (frame.repeated_row_group_size>1).sum()==8174
    assert frame.groupby('month').size().tolist()==[857,1147,819,880,1207,816,1277,1141,1222]


def test_geography_and_coverage_are_explicit(result):
    frame=table(result,'land_records_2022.csv')
    assert frame.groupby('month').governorate_id.nunique().tolist()==[11,11]
    assert frame[frame.source_region_en=='Alsharqia'].governorate_id.nunique()==2
    assert frame.nonstandard_wilayat_label.sum()==2
    matrix=table(result,'coverage_matrix_2020_2026.csv')
    assert len(matrix)==3*7*12*11
    assert (matrix.availability_status=='observed').sum()==42
    assert matrix.loc[matrix.availability_status!='observed','reported_record_count'].isna().all()
    assert not (table(result,'dim_date.csv').year==2026).any()
    observed=table(result,'coverage_observed.csv')
    assert observed.reported_record_count.sum()==28558
    assert table(result,'monthly_reported_records.csv').reported_record_count.sum()==28558


def test_unverified_units_and_missing_values_remain_unknown(result):
    frame=table(result,'land_records_2024.csv')
    assert len(frame)==6024 and frame.reported_re_value.notna().sum()==5657
    assert frame.reported_re_value.isna().sum()==367
    assert frame.currency_unit.isna().all()
    assert set(frame.service_sub_id)=={'RN13A','RN13C'}
    assert (frame.reported_re_value.dropna()>0).all()
    assert 'DATE_OF_BIRTH' not in frame and 'GENDER_NAME_AR' not in frame
    p=result[1]['datasets'][-1]
    assert p['numerical_profile']['raw_unit_sum']=='89547462.666'
    assert p['quality_flags']['birth_date_1900_sentinel']==617
    assert p['quality_flags']['birth_date_after_transaction']==1
    assert p['quality_flags']['birth_date_under_18']==27  # Future birth date is counted separately, not as a minor.
    assert p['quality_flags'].get('ownership_mode_mismatches',0)==0
    assert 'reported_re_value' not in table(result,'land_records_2022.csv')
    assert 'number_of_owners' not in table(result,'muscat_brokerage_records_2025.csv')


def test_lineage_and_manifest_reconcile(result):
    manifest=json.loads(result[0]['manifest.json'])
    for name,digest in manifest['artifact_sha256'].items():
        assert sha(result[0][name])==digest
    for name in ('land_records_2022.csv','land_records_2024.csv','muscat_brokerage_records_2025.csv'):
        frame=table(result,name)
        assert frame.record_id.is_unique
        assert not frame[['dataset_id','source_sha256','source_sheet','source_row']].isna().any().any()
    assert not result[1]['ready_for_2020_2026_market_analysis']
    assert not result[1]['exact_download_urls_verified']


def test_immutable_run_reuses_bytes_and_refuses_overwrite(result,tmp_path,monkeypatch):
    monkeypatch.setattr('src.audit_uploaded_data.build',lambda **kwargs:result)
    _,target=run(tmp_path)
    _,again=run(tmp_path)
    assert target==again
    (target/'dim_date.csv').write_text('changed')
    with pytest.raises(ValueError,match='refusing to overwrite'):
        run(tmp_path)


def test_changed_original_fails_closed(tmp_path):
    registry=json.loads(REGISTRY.read_text())
    registry[0]['sha256']='0'*64
    path=tmp_path/'registry.json';path.write_text(json.dumps(registry))
    with pytest.raises(ValueError,match='checksum mismatch'):
        build(registry_path=path)


def test_dates_are_strict():
    for invalid in ('31/10/2024','2024-02-30','1900-01-01 00:00:00',None):
        with pytest.raises(ValueError):
            iso_date(invalid)
    assert iso_date('2024-10-01')==date(2024,10,1)


def test_empty_aggregate_selection_does_not_read_row_uploads(tmp_path):
    report,code=aggregate_run(ROOT/'data/raw/manual',tmp_path/'out',tmp_path/'status.json',files=[])
    assert code==2 and report['errors']==[] and report['imported_files']==0


def test_powerbi_dimension_keys_and_facts_agree(result):
    for name,key in [('dim_governorate.csv','governorate_id'),('dim_wilayat.csv','wilayat_key'),
                     ('dim_date.csv','transaction_date'),('dim_dataset.csv','dataset_id')]:
        dimension=table(result,name)
        assert dimension[key].is_unique and dimension[key].notna().all()
        for fact in ('land_records_2022.csv','land_records_2024.csv','muscat_brokerage_records_2025.csv'):
            assert set(table(result,fact)[key]) <= set(dimension[key])
