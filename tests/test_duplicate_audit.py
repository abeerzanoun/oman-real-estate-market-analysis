"""Audit real uploaded rows; replay tests use actual source occurrences only."""
from io import BytesIO
import json

import pandas as pd
import pytest

from src.audit_duplicates import ROOT, build, digest, lineage_assessment, csv_read, CONFIG, audit_csv_inventory, run
from src.audit_uploaded_data import BROKER_HEADERS, LAND_HEADERS, LAND_2024_HEADERS


@pytest.fixture(scope='module')
def audited():
    return build()


def table(audited,name):
    return pd.read_csv(BytesIO(audited[0][name]),encoding='utf-8-sig')


def test_current_full_source_columns_are_exact(audited):
    profiles={p['dataset_id']:p for p in audited[1]['datasets']}
    assert profiles['muscat_brokerage_2025']['source_columns_in_current_detection']==BROKER_HEADERS
    assert profiles['land_nov_2022']['source_columns_in_current_detection']==LAND_HEADERS
    assert profiles['land_dec_2022']['source_columns_in_current_detection']==LAND_HEADERS
    assert profiles['land_oct_2024']['source_columns_in_current_detection']==LAND_2024_HEADERS
    assert profiles['land_oct_2024']['source_columns_omitted_from_export']==['DATE_OF_BIRTH','GENDER_NAME_AR','GENDER_NAME_EN']


def test_real_source_and_exported_payload_counts(audited):
    profiles=audited[1]['datasets']
    assert [(p['source_rows'],p['full_source_equality']['repeated_groups'],p['full_source_equality']['repeat_occurrences_after_first'],p['full_source_equality']['occurrences_in_repeated_groups']) for p in profiles]==[
        (9366,1396,6778,8174),(7501,1046,2629,3675),(5667,757,1843,2600),(6024,0,0,0)]
    assert [(p['exported_payload_equality']['repeated_groups'],p['exported_payload_equality']['repeat_occurrences_after_first'],p['exported_payload_equality']['occurrences_in_repeated_groups']) for p in profiles]==[
        (1396,6778,8174),(1094,3076,4170),(804,2138,2942),(232,278,510)]
    assert [(p['projection_collision_groups'],p['projection_collision_occurrences']) for p in profiles]==[(0,0),(437,2391),(286,1604),(232,510)]


def test_identifiers_and_economic_identity_not_invented(audited):
    report=audited[1]
    assert report['confirmed_duplicate_ingestion_occurrences']==0
    assert report['confirmed_duplicate_economic_transactions']==0
    assert report['actual_duplicate_economic_transaction_count'] is None
    for p in report['datasets']:
        assert not p['reliable_official_transaction_or_record_id']
        assert not any(c['unique_complete_column'] for c in p['source_column_identity_assessment'])
    candidate=report['datasets'][-1]['candidate_identifier_columns']
    assert len(candidate)==1 and candidate[0]['column']=='SERVICE_SUB_ID'
    assert candidate[0]['distinct_nonmissing']==2 and not candidate[0]['reliable_unique_transaction_id']


def test_existing_source_repetitions_are_not_ingestion_duplicates():
    frame=csv_read(ROOT/'data/processed/audited/71008482abd46aa7f0bc/muscat_brokerage_records_2025.csv')
    signature=frame.loc[frame.repeated_row_group_size.astype(int).gt(1),'raw_row_signature'].iloc[0]
    records=frame[frame.raw_row_signature==signature].head(2)
    assert len(records)==2 and records.record_id.is_unique
    payload=['transaction_category_ar','source_wilayat_ar','transaction_date','property_use_ar','property_description_ar']
    assert len(records[payload].drop_duplicates())==1
    result=lineage_assessment(records,payload)
    assert result['repeated_lineage_occurrences_after_first']==0
    assert result['conflicting_lineage_groups']==0


def test_ingestion_replay_of_one_actual_source_row_is_confirmable():
    frame=csv_read(ROOT/'data/processed/audited/71008482abd46aa7f0bc/muscat_brokerage_records_2025.csv')
    # Two copies of the SAME real source occurrence, in memory only; no new market observation.
    replay=frame.iloc[[0,0]].copy()
    result=lineage_assessment(replay,['transaction_category_ar','transaction_date','source_wilayat_ar'])
    assert result['repeated_lineage_occurrences_after_first']==1
    assert result['repeated_generated_ids_after_first']==1
    assert result['conflicting_lineage_groups']==0


def test_all_occurrences_retained_in_evidence_ledgers(audited):
    for p in audited[1]['datasets']:
        f=table(audited,p['dataset_id']+'_occurrence_review.csv')
        assert len(f)==p['source_rows'] and f.record_id.is_unique
        assert f.source_row.is_unique and f.processed_record_ordinal.is_unique
        assert not f.removed.any()
        assert sum(f.full_source_group_size.gt(1))==p['full_source_equality']['occurrences_in_repeated_groups']
        assert sum(f.processed_payload_group_size.gt(1))==p['exported_payload_equality']['occurrences_in_repeated_groups']
        assert not {'DATE_OF_BIRTH','GENDER_NAME_AR','GENDER_NAME_EN','reported_re_value'} & set(f.columns)
    assert audited[1]['source_occurrences']==28558
    assert audited[1]['rows_removed']==0 and audited[1]['cleaned_outputs_created']==[]
    assert audited[1]['powerbi_modeling_performed'] is False


def test_group_ledgers_and_actual_examples_reconcile(audited):
    for p in audited[1]['datasets']:
        groups=table(audited,p['dataset_id']+'_repeated_groups.csv')
        for criterion,stat in [('full_source_equality','full_source_equality'),('exported_payload_equality','exported_payload_equality')]:
            rows=groups[groups.criterion==criterion]
            assert len(rows)==p[stat]['repeated_groups']
            assert rows.group_size.sum()==p[stat]['occurrences_in_repeated_groups']
            assert rows.repeat_occurrences_after_first.sum()==p[stat]['repeat_occurrences_after_first']
        for example in p['examples']:
            actual_rows=[int(n) for n in example['source_rows'].split(';')]
            assert len(actual_rows)==example['group_size'] and len(set(actual_rows))==len(actual_rows)
            assert not {'DATE_OF_BIRTH','GENDER_NAME_AR','GENDER_NAME_EN','RE_VALUE'} & set(example['sample_values'])
        assert p['examples']


def test_every_snapshot_csv_and_metadata_copy_assessed(audited):
    inventory=table(audited,'processed_csv_inventory.csv')
    assert len(inventory)==43
    assert inventory.exact_full_csv_row_repeats_after_first.eq(0).all()
    assert inventory.checksum_verified_against_existing_manifest.all()
    copies=audited[1]['intentional_identical_csv_copies']
    assert len(copies)==5
    assert {entry['files'][0].rsplit('/',1)[-1] for entry in copies}=={'coverage_matrix_2020_2026.csv','source_column_quality.csv','dim_wilayat.csv','dim_governorate.csv','dim_dataset.csv'}
    for entry in copies:
        assert len(entry['files'])==2
        assert all(digest((ROOT/path).read_bytes())==entry['sha256'] for path in entry['files'])


def test_aggregate_grain_and_multiplicity_are_preserved(audited):
    results=audited[1]['analytical_aggregate_validation']
    assert [(r['physical_aggregate_rows'],r['preserved_source_occurrences'],r['reported_record_count_sum']) for r in results]==[(361,13168,13168),(257,6024,6024),(403,9366,9366)]
    assert all(r['grain'] for r in results)
    assert not any(pair['date_ranges_overlap'] or pair['shared_observed_date_count'] for pair in audited[1]['cross_file_date_ranges'])
    assert len(audited[1]['cross_file_date_ranges'])==6


def test_protected_originals_and_processed_files_unchanged(audited):
    manifest=json.loads(audited[0]['manifest.json'])
    assert len(manifest['protected_inputs'])==47
    for entry in manifest['protected_inputs']:
        assert digest((ROOT/entry['file']).read_bytes())==entry['sha256']
    for name,sha in manifest['output_sha256'].items():
        assert digest(audited[0][name])==sha


def test_immutable_reports_refuse_changed_existing_outputs(audited,tmp_path,monkeypatch):
    monkeypatch.setattr('src.audit_duplicates.build',lambda **kwargs:audited)
    _,target=run(output_root=tmp_path)
    _,again=run(output_root=tmp_path)
    assert again==target
    (target/'README.md').write_text('changed')
    with pytest.raises(ValueError,match='refusing to overwrite'):
        run(output_root=tmp_path)


def test_modified_csv_manifest_check_fails_closed(tmp_path):
    # Use an existing real CSV, corrupt its expected digest rather than creating observations.
    folder=tmp_path/'audited';folder.mkdir()
    payload=(ROOT/'data/processed/audited/71008482abd46aa7f0bc/dim_governorate.csv').read_bytes()
    (folder/'dim_governorate.csv').write_bytes(payload)
    (folder/'manifest.json').write_text(json.dumps({'artifact_sha256':{'dim_governorate.csv':'0'*64}}))
    (tmp_path/'eda').mkdir()
    with pytest.raises(ValueError,match='modified processed CSV'):
        audit_csv_inventory(tmp_path,dict(audited_directory='audited',eda_directory='eda'))
