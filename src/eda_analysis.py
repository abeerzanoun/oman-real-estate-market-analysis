"""Scoped EDA transformations of hash-verified audit outputs; no imputation."""
from pathlib import Path
import hashlib
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT/'docs/eda_config.json'
FACT_FILES = {'land_2022':'land_records_2022.csv','land_2024':'land_records_2024.csv',
              'brokerage_2025':'muscat_brokerage_records_2025.csv'}
SCOPES = {'land_2022':'land_buy_sell_2022','land_2024':'land_service_coded_2024',
          'brokerage_2025':'muscat_brokerage_registration_2025'}


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def read_csv(path):
    # Monetary tokens are intentionally kept as strings, and never summarized.
    return pd.read_csv(path,encoding='utf-8-sig',dtype={'reported_re_value':'string','currency_unit':'string'})


def load_inputs(root=ROOT, config_path=CONFIG):
    root,config_path = Path(root),Path(config_path)
    config = json.loads(config_path.read_text())
    folder = root/config['audit_directory']
    manifest_bytes = (folder/'manifest.json').read_bytes()
    if digest(manifest_bytes) != config['audit_manifest_sha256']:
        raise ValueError('Pinned audit manifest has changed; review a new input version')
    manifest = json.loads(manifest_bytes)
    for name,expected in manifest['artifact_sha256'].items():
        if Path(name).name != name or digest((folder/name).read_bytes()) != expected:
            raise ValueError(f'Audit artifact checksum mismatch: {name}')
    for relative,expected in manifest['source_sha256'].items():
        if digest((root/relative).read_bytes()) != expected:
            raise ValueError(f'Original workbook checksum mismatch: {relative}')
    facts = {}
    for family,name in FACT_FILES.items():
        frame = read_csv(folder/name)
        if not frame.record_id.is_unique or set(frame.scope_id) != {SCOPES[family]}:
            raise ValueError(f'Invalid identity or mixed scope: {name}')
        parsed = pd.to_datetime(frame.transaction_date,format='%Y-%m-%d',errors='raise')
        if not (frame.year.eq(parsed.dt.year).all() and frame.month.eq(parsed.dt.month).all()):
            raise ValueError('Derived period columns disagree with source dates')
        frame['period_id'] = parsed.dt.strftime('%Y-%m')
        frame['in_repeated_group'] = frame.repeated_row_group_size.gt(1)
        if 'number_of_owners' in frame:
            frame['ownership_band'] = frame.number_of_owners.map(lambda n:f'{int(n)} owner'+('s' if n!=1 else '') if n<5 else '5+ owners')
        facts[family] = frame
    report = json.loads((folder/'audit_report.json').read_text())
    if sum(len(f) for f in facts.values()) != report['record_count']:
        raise ValueError('Audit reconciliation failed')
    dimensions = {name:read_csv(folder/f'{name}.csv') for name in ('dim_governorate','dim_wilayat','dim_dataset')}
    for key,table in [('governorate_id','dim_governorate'),('wilayat_key','dim_wilayat'),('dataset_id','dim_dataset')]:
        dim=dimensions[table]
        if not dim[key].is_unique or dim[key].isna().any():
            raise ValueError(f'Dimension key is not unique: {key}')
        for frame in facts.values():
            if not set(frame[key]) <= set(dim[key]):
                raise ValueError(f'Unmatched dimension key: {key}')
    dimensions['coverage_matrix'] = read_csv(folder/'coverage_matrix_2020_2026.csv')
    dimensions['source_column_quality'] = read_csv(folder/'source_column_quality.csv')
    return dict(config=config,manifest=manifest,audit_report=report,facts=facts,dimensions=dimensions)


def counted(frame,keys,denominator_keys):
    """Aggregate only observed groups; shares use the explicitly stated cohort."""
    result=frame.groupby(keys,dropna=False,observed=True).size().reset_index(name='reported_record_count')
    total=result.groupby(denominator_keys,dropna=False).reported_record_count.transform('sum') if denominator_keys else pd.Series(result.reported_record_count.sum(),index=result.index)
    result['cohort_record_count']=total
    result['share_pct']=100*result.reported_record_count/total
    return result.sort_values(keys).reset_index(drop=True)


def compare_2022(governorate_counts):
    data=governorate_counts[governorate_counts.scope_id.eq(SCOPES['land_2022'])]
    if set(data.period_id)!={'2022-11','2022-12'} or not data.groupby('period_id').governorate_id.nunique().eq(11).all():
        raise ValueError('November/December 2022 comparison requires both comparable supplied months and all 11 governorates')
    key=['governorate_id','governorate_en','governorate_ar']
    nov=data[data.period_id.eq('2022-11')][key+['reported_record_count','share_pct']].rename(columns={'reported_record_count':'november_records','share_pct':'november_share_pct'})
    dec=data[data.period_id.eq('2022-12')][key+['reported_record_count','share_pct']].rename(columns={'reported_record_count':'december_records','share_pct':'december_share_pct'})
    result=nov.merge(dec,on=key,validate='one_to_one')
    result['record_count_difference']=result.december_records-result.november_records
    result['record_count_change_pct']=100*result.record_count_difference/result.november_records
    result['share_change_percentage_points']=result.december_share_pct-result.november_share_pct
    result['comparison_scope']=SCOPES['land_2022']
    return result


def powerbi_fact(frame,keys):
    # No monetary fields are passed into these facts, even as an unverified sum.
    result=frame.groupby(keys,dropna=False,observed=True).agg(
        reported_record_count=('record_id','size'),
        records_in_repeated_groups=('in_repeated_group','sum')).reset_index()
    if result.reported_record_count.sum()!=len(frame):
        raise ValueError('Analytical fact count failed reconciliation')
    return result.sort_values(keys).reset_index(drop=True)


def summarize(inputs):
    tables={}
    facts,dim=inputs['facts'],inputs['dimensions']
    geographical=[];wilayat=[];dataset=[];quality=[]
    for family,frame in facts.items():
        g=counted(frame,['dataset_id','scope_id','period_id','governorate_id'],['dataset_id','period_id'])
        g['rank_within_dataset_period']=g.groupby(['dataset_id','period_id']).reported_record_count.rank(method='min',ascending=False).astype(int)
        geographical.append(g.merge(dim['dim_governorate'],on='governorate_id',validate='many_to_one'))
        w=counted(frame,['dataset_id','scope_id','period_id','governorate_id','wilayat_key','wilayat_ar','nonstandard_wilayat_label'],['dataset_id','period_id'])
        w['within_governorate_share_pct']=100*w.reported_record_count/w.groupby(['dataset_id','period_id','governorate_id']).reported_record_count.transform('sum')
        wilayat.append(w)
        for dataset_id,group in frame.groupby('dataset_id'):
            profile=next(p for p in inputs['audit_report']['datasets'] if p['dataset_id']==dataset_id)
            dataset.append(dict(dataset_id=dataset_id,scope_id=SCOPES[family],reported_record_count=len(group),
                first_record_date=group.transaction_date.min(),last_record_date=group.transaction_date.max(),
                observed_months=group.period_id.nunique(),observed_governorates=group.governorate_id.nunique(),
                observed_wilayat_labels=group.wilayat_key.nunique(),nonstandard_wilayat_rows=int(group.nonstandard_wilayat_label.sum())))
            quality.append(dict(dataset_id=dataset_id,reported_record_count=len(group),
                records_in_repeated_groups=int(group.in_repeated_group.sum()),
                repeated_occurrences_after_first=int(group.occurrence_rank.gt(1).sum()),
                repeated_group_share_pct=100*group.in_repeated_group.mean(),rows_removed=0,
                reported_amount_present_records=profile.get('numerical_profile',{}).get('present'),
                reported_amount_missing_records=profile.get('numerical_profile',{}).get('missing'),
                monetary_unit_verified=False))
    tables['dataset_summary']=pd.DataFrame(dataset)
    tables['data_quality_summary']=pd.DataFrame(quality)
    tables['governorate_counts']=pd.concat(geographical,ignore_index=True)
    tables['wilayat_counts']=pd.concat(wilayat,ignore_index=True)
    tables['governorate_nov_dec_2022']=compare_2022(tables['governorate_counts'])
    tables['buyer_type_counts']=pd.concat([counted(facts[family],['dataset_id','scope_id','period_id','buyer_type'],['dataset_id','period_id']) for family in ('land_2022','land_2024')],ignore_index=True)
    tables['ownership_counts']=pd.concat([counted(facts[family],['dataset_id','scope_id','period_id','ownership_band'],['dataset_id','period_id']) for family in ('land_2022','land_2024')],ignore_index=True)
    land=facts['land_2024'];broker=facts['brokerage_2025']
    tables['service_code_counts_2024']=counted(land,['dataset_id','period_id','service_sub_id'],['dataset_id','period_id'])
    tables['service_by_governorate_2024']=counted(land,['dataset_id','period_id','governorate_id','service_sub_id'],['dataset_id','period_id','governorate_id']).merge(dim['dim_governorate'],on='governorate_id',validate='many_to_one')
    tables['brokerage_monthly_counts']=counted(broker,['dataset_id','scope_id','period_id'],['dataset_id'])
    tables['brokerage_wilayat_counts']=counted(broker,['dataset_id','scope_id','governorate_id','wilayat_key','wilayat_ar'],['dataset_id'])
    tables['brokerage_wilayat_monthly_counts']=counted(broker,['dataset_id','scope_id','period_id','wilayat_key','wilayat_ar'],['dataset_id','period_id'])
    for field in ('property_use_ar','property_description_ar','transaction_category_ar'):
        tables['brokerage_'+field.removesuffix('_ar')]=counted(broker,['dataset_id','scope_id',field],['dataset_id'])
    tables['brokerage_property_use_by_wilayat']=counted(broker,['dataset_id','scope_id','wilayat_key','wilayat_ar','property_use_ar'],['dataset_id','wilayat_key'])
    # Prepared monthly Power BI facts have explicit family-specific grains.
    common=['dataset_id','period_id','governorate_id','wilayat_key','nonstandard_wilayat_label']
    for family in ('land_2022','land_2024'):
        keys=common+['buyer_type','ownership_band']
        if family=='land_2024':
            keys+=['service_sub_id','ownership_mode']
        tables['fact_'+family]=powerbi_fact(facts[family],keys)
    for field,label in [('property_use_key','property_use_ar'),('property_description_key','property_description_ar')]:
        category=broker[[field,label]].drop_duplicates().sort_values(field)
        if not category[field].is_unique:
            raise ValueError('Category normalization would merge distinct source labels')
        tables['dim_'+field.removesuffix('_key')]=category
    tables['fact_brokerage_2025']=powerbi_fact(broker,common+['property_use_key','property_description_key'])
    for name in ('dim_dataset','dim_governorate','dim_wilayat'):
        tables[name]=dim[name].copy()
    # These are observed month labels, not a fabricated complete calendar.
    periods=pd.concat([f[['period_id','year','month']] for f in facts.values()]).drop_duplicates().sort_values('period_id')
    periods['period_label']=pd.to_datetime(periods.period_id,format='%Y-%m').dt.strftime('%b %Y')
    tables['dim_period']=periods.reset_index(drop=True)
    tables['dim_buyer_type']=pd.DataFrame({'buyer_type':sorted(set(tables['buyer_type_counts'].buyer_type))})
    tables['dim_service_code']=pd.DataFrame({'service_sub_id':sorted(set(land.service_sub_id)),
        'definition_status':'meaning_unverified'})
    tables['dim_ownership_band']=pd.DataFrame({'ownership_band':sorted(set(tables['ownership_counts'].ownership_band),key=lambda s:int(s[0]))})
    tables['coverage_observed']=tables['governorate_counts'][['dataset_id','scope_id','period_id','governorate_id','reported_record_count']].copy()
    tables['coverage_matrix_2020_2026']=dim['coverage_matrix'].copy()
    tables['source_column_quality']=dim['source_column_quality'].copy()
    return tables
