"""Integrity and analytical checks against actual merged-PR4 records, not mock data."""
from pathlib import Path
import json

import nbformat
import pandas as pd
from PIL import Image
import pytest

from src.eda_analysis import ROOT, CONFIG, SCOPES, digest, load_inputs, summarize, compare_2022
from src.run_eda import run, persist_immutable


@pytest.fixture(scope='module')
def inputs():
    return load_inputs()


@pytest.fixture(scope='module')
def tables(inputs):
    return summarize(inputs)


def test_pinned_main_and_originals_are_preserved(inputs):
    assert inputs['config']['merged_audit_pr']==4
    assert inputs['config']['base_main_commit']=='2c4237a5ec24e01b3dde13f2b0ac518b92437db3'
    assert sum(len(f) for f in inputs['facts'].values())==28558
    for path,sha in inputs['manifest']['source_sha256'].items():
        assert digest((ROOT/path).read_bytes())==sha


def test_tampered_input_manifest_is_rejected(tmp_path):
    config=json.loads(CONFIG.read_text());config['audit_manifest_sha256']='0'*64
    path=tmp_path/'config.json';path.write_text(json.dumps(config))
    with pytest.raises(ValueError,match='Pinned audit manifest'):
        load_inputs(config_path=path)


def test_comparison_is_limited_to_real_2022_months(tables):
    result=tables['governorate_nov_dec_2022']
    assert len(result)==11
    assert result.november_records.sum()==7501
    assert result.december_records.sum()==5667
    assert result.record_count_difference.sum()==-1834
    assert result.share_change_percentage_points.sum()==pytest.approx(0,abs=1e-12)
    al_wusta=result.set_index('governorate_id').loc['al_wusta']
    assert al_wusta.november_records==105 and al_wusta.december_records==294
    assert al_wusta.share_change_percentage_points==pytest.approx(3.78811710776)
    data=tables['governorate_counts']
    for subset in (data[data.period_id.eq('2024-10')],data[data.period_id.eq('2022-11')]):
        with pytest.raises(ValueError,match='both comparable supplied months'):
            compare_2022(subset)


def test_governorate_and_wilayat_totals_reconcile(tables):
    assert len(tables['governorate_counts'])==42
    assert tables['governorate_counts'].reported_record_count.sum()==28558
    assert tables['wilayat_counts'].reported_record_count.sum()==28558
    counts=tables['governorate_counts'].groupby('period_id').governorate_id.nunique()
    assert counts.loc[['2022-11','2022-12','2024-10']].eq(11).all()
    assert counts[counts.index.str.startswith('2025')].eq(1).all()
    nonstandard=tables['wilayat_counts'].query('nonstandard_wilayat_label')
    assert nonstandard.reported_record_count.sum()==2
    assert set(nonstandard.governorate_id)=={'dhofar'}


def test_cohort_shares_and_actual_categories(tables):
    assert tables['governorate_counts'].groupby(['dataset_id','period_id']).share_pct.sum().round(8).eq(100).all()
    assert tables['buyer_type_counts'].groupby('period_id').share_pct.sum().round(8).eq(100).all()
    assert tables['ownership_counts'].groupby('period_id').share_pct.sum().round(8).eq(100).all()
    for field in ('property_use','property_description','transaction_category'):
        assert tables['brokerage_'+field].reported_record_count.sum()==9366
        assert tables['brokerage_'+field].share_pct.sum()==pytest.approx(100)
    assert len(tables['brokerage_property_use'])==8
    assert len(tables['brokerage_property_description'])==13
    assert len(tables['brokerage_transaction_category'])==1
    codes=tables['service_code_counts_2024'].set_index('service_sub_id')
    assert codes.reported_record_count.to_dict()=={'RN13A':599,'RN13C':5425}


def test_model_totals_are_source_occurrences_not_fact_row_counts(tables):
    for family,count,rows in [('land_2022',13168,361),('land_2024',6024,257),('brokerage_2025',9366,403)]:
        fact=tables['fact_'+family]
        assert len(fact)==rows and fact.reported_record_count.sum()==count
        assert fact.reported_record_count.gt(0).all()
        assert fact.records_in_repeated_groups.between(0,fact.reported_record_count).all()
    assert tables['fact_land_2022'].records_in_repeated_groups.sum()==6275
    assert tables['fact_brokerage_2025'].records_in_repeated_groups.sum()==8174
    assert tables['fact_land_2024'].records_in_repeated_groups.sum()==0


def test_no_monetary_or_demographic_fact_columns(tables):
    forbidden={'reported_re_value','transaction_value','transaction_value_omr','price','DATE_OF_BIRTH','GENDER_NAME_AR'}
    for name,table in tables.items():
        if name.startswith('fact_'):
            assert not forbidden.intersection(table.columns)
    assert not tables['data_quality_summary'].monetary_unit_verified.any()
    dims=tables['dim_service_code']
    assert dims.definition_status.eq('meaning_unverified').all()


def test_analytical_relationships_have_unique_matched_keys(tables):
    shared={'dim_dataset':'dataset_id','dim_period':'period_id','dim_governorate':'governorate_id','dim_wilayat':'wilayat_key'}
    specific={'dim_property_use':('property_use_key',['fact_brokerage_2025']),
              'dim_property_description':('property_description_key',['fact_brokerage_2025']),
              'dim_buyer_type':('buyer_type',['fact_land_2022','fact_land_2024']),
              'dim_service_code':('service_sub_id',['fact_land_2024']),
              'dim_ownership_band':('ownership_band',['fact_land_2022','fact_land_2024'])}
    fact_names=['fact_land_2022','fact_land_2024','fact_brokerage_2025']
    for dim,key in shared.items():
        specific[dim]=(key,fact_names)
    for dim,(key,linked) in specific.items():
        assert tables[dim][key].is_unique and tables[dim][key].notna().all()
        for fact in linked:
            assert tables[fact][key].notna().all()
            assert set(tables[fact][key]) <= set(tables[dim][key])


def test_no_missing_periods_are_filled(tables):
    periods=set(tables['dim_period'].period_id)
    assert periods=={'2022-11','2022-12','2024-10',*[f'2025-{m:02}' for m in range(1,10)]}
    assert tables['brokerage_monthly_counts'].reported_record_count.tolist()==[857,1147,819,880,1207,816,1277,1141,1222]
    coverage=tables['coverage_matrix_2020_2026']
    assert coverage.loc[coverage.availability_status!='observed','reported_record_count'].isna().all()
    assert len(tables['coverage_observed'])==42


def test_category_labels_preserved_and_shaping_is_presentation_only(inputs,tables):
    broker=inputs['facts']['brokerage_2025']
    assert set(broker.property_use_ar)==set(tables['dim_property_use'].property_use_ar)
    assert set(broker.property_description_ar)==set(tables['dim_property_description'].property_description_ar)
    assert 'مسكن أجتماعي' in set(tables['dim_property_description'].property_description_ar)
    assert tables['brokerage_property_use_by_wilayat'].reported_record_count.sum()==9366


def test_real_figures_and_artifact_manifest(tmp_path):
    result=run(execute_notebook=False,output_root=tmp_path)
    folder=tmp_path/result['tables_directory']
    manifest=json.loads((folder/'analysis_manifest.json').read_text())
    assert len(manifest['csv_sha256'])==31
    for name,sha in manifest['csv_sha256'].items():
        assert digest((folder/name).read_bytes())==sha
    figures=tmp_path/result['figures_directory']
    assert len(manifest['figure_names'])==14
    assert len(manifest['figure_sha256'])==28
    for name,sha in manifest['figure_sha256'].items():
        assert digest((figures/name).read_bytes())==sha
        if name.endswith('.png'):
            with Image.open(figures/name) as img:
                assert img.width>=1800 and img.height>=900
                img.verify()
    assert manifest['source_occurrences']==28558
    assert manifest['monetary_analysis'] is False
    before=(folder/'analysis_manifest.json').read_bytes()
    again=run(execute_notebook=False,output_root=tmp_path)
    assert result['run_id']==again['run_id'] and (folder/'analysis_manifest.json').read_bytes()==before


def test_immutable_output_refuses_changed_derived_file(tmp_path):
    source=ROOT/'docs/eda_config.json'
    payload=source.read_bytes()
    persist_immutable(tmp_path/'run',{'config.json':payload})
    (tmp_path/'run/config.json').write_bytes(b'changed')
    with pytest.raises(ValueError,match='refusing to overwrite'):
        persist_immutable(tmp_path/'run',{'config.json':payload})


def test_executed_notebook_is_valid_and_complete():
    notebook=nbformat.read(ROOT/'notebooks/01_scoped_real_estate_eda.ipynb',as_version=4)
    nbformat.validate(notebook)
    code=[c for c in notebook.cells if c.cell_type=='code']
    assert len(code)==7
    assert all(c.execution_count is not None for c in code)
    assert not any(o.output_type=='error' for c in code for o in c.outputs)
    images=[o for c in code for o in c.outputs if 'image/png' in o.get('data',{})]
    assert len(images)==14
    run_id=notebook.metadata.oman_eda.run_id
    manifest=json.loads((ROOT/f'data/processed/eda/{run_id}/analysis_manifest.json').read_text())
    assert manifest['source_occurrences']==28558
