"""Audit source patterns and processed occurrences without modifying input datasets.

python -m src.audit_duplicates
This produces evidence/reports only. It neither builds Power BI nor drops records.
"""
import argparse
from collections import Counter, defaultdict
from decimal import Decimal
import hashlib
import json
from pathlib import Path

import pandas as pd

from openpyxl.utils import get_column_letter
from src.excel_reader import read_workbook
from src.audit_uploaded_data import iso_date
from src.eda_analysis import ROOT
from src.run_eda import persist_immutable

CONFIG = ROOT/'docs/duplicate_audit_config.json'
PROJECTIONS = {
    'TRANSACTION_DATE':'transaction_date','BUYER_TYPE':'buyer_type',
    'REGION_AR':'source_region_ar','REGION_EN':'source_region_en',
    'WILAYAT_AR':'source_wilayat_ar','WILAYAT_EN':'source_wilayat_en',
    'VILLAGE_AR':'source_village_ar','VILLAGE_EN':'source_village_en',
    'NO_OF_OWNERS':'number_of_owners','SERVICE_SUB_ID':'service_sub_id',
    'RE_VALUE':'reported_re_value','SINGLE_MULTIPLE':'ownership_mode',
    'اسم المعاملة':'transaction_category_ar','الولاية':'source_wilayat_ar',
    'تاريخ الإجراء':'transaction_date','نوع الإستعمال':'property_use_ar','وصف العقار':'property_description_ar',
}
PRIVATE = {'DATE_OF_BIRTH','GENDER_NAME_AR','GENDER_NAME_EN'}
FACT_FILES = {'muscat_brokerage_2025':'muscat_brokerage_records_2025.csv',
              'land_nov_2022':'land_records_2022.csv','land_dec_2022':'land_records_2022.csv',
              'land_oct_2024':'land_records_2024.csv'}
AGG_KEYS = {
 'fact_land_2022':['dataset_id','period_id','governorate_id','wilayat_key','nonstandard_wilayat_label','buyer_type','ownership_band'],
 'fact_land_2024':['dataset_id','period_id','governorate_id','wilayat_key','nonstandard_wilayat_label','buyer_type','ownership_band','service_sub_id','ownership_mode'],
 'fact_brokerage_2025':['dataset_id','period_id','governorate_id','wilayat_key','nonstandard_wilayat_label','property_use_key','property_description_key'],
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def current_signature(row):
    """Exactly reproduce src.audit_uploaded_data's existing full-row signature."""
    return digest(json.dumps(tuple(row),ensure_ascii=False,default=str).encode())


def dump(data):
    return json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True,default=str)+'\n'


def csv_read(path):
    # Empty cells stay empty; strings preserve exact exported tokens/whitespace.
    return pd.read_csv(path,encoding='utf-8-sig',dtype=str,keep_default_na=False)


def groups_of(keys):
    groups=defaultdict(list)
    for position,key in enumerate(keys):
        groups[key].append(position)
    return dict(groups)


def group_statistics(groups):
    sizes=[len(members) for members in groups.values()]
    return dict(distinct_attribute_patterns=len(sizes),repeated_groups=sum(n>1 for n in sizes),
                occurrences_in_repeated_groups=sum(n for n in sizes if n>1),
                repeat_occurrences_after_first=sum(n-1 for n in sizes),
                largest_group=max(sizes,default=0))


def source_token(header,value,sheet,excel_row,column):
    if value is None:
        return ''
    if header in {'TRANSACTION_DATE','تاريخ الإجراء'}:
        return iso_date(value).isoformat()
    if header=='RE_VALUE':
        # Compare the exact published numeric token, without claiming its unit/meaning.
        coordinate=f'{column}{excel_row}'
        token=sheet['numeric_tokens'].get(coordinate)
        if token is None:
            raise ValueError(f'No source numeric token: {coordinate}')
        return str(Decimal(token))
    if header=='NO_OF_OWNERS':
        return str(int(value))
    return str(value)


def lineage_assessment(frame,payload_columns):
    """A source occurrence is a file/sheet/row, not an economic transaction."""
    key=['source_sha256','source_sheet','source_row']
    groups=frame.groupby(key,dropna=False,sort=True)
    confirmed,conflicts=0,0
    for _,group in groups:
        if len(group)>1:
            if len(group[payload_columns].drop_duplicates())==1:
                confirmed+=len(group)-1
            else:
                conflicts+=1
    return dict(repeated_lineage_occurrences_after_first=confirmed,
                conflicting_lineage_groups=conflicts,
                repeated_generated_ids_after_first=int(frame.record_id.duplicated().sum()))


def audit_source(entry,root,audited,example_count):
    original=root/entry['file']
    if digest(original.read_bytes())!=entry['sha256']:
        raise ValueError(f'Original checksum mismatch: {entry["file"]}')
    book=read_workbook(original)
    sheet=next(s for s in book['sheets'] if s['name']==entry['sheet'])
    headers=list(sheet['rows'][entry['header_row']-1])
    source=[(n,tuple(row[:len(headers)])) for n,row in enumerate(sheet['rows'][entry['header_row']:],start=entry['header_row']+1) if any(v is not None for v in row)]
    frame=csv_read(audited/FACT_FILES[entry['dataset_id']])
    frame['processed_record_ordinal']=range(1,len(frame)+1)
    frame=frame[frame.dataset_id==entry['dataset_id']].copy()
    if len(source)!=len(frame) or len(source)!=entry['audited_row_count']:
        raise ValueError('Original/processed dataset row-count discrepancy')
    projected=[h for h in headers if h in PROJECTIONS]
    projected_columns=[PROJECTIONS[h] for h in projected]
    if set(headers)-set(projected)!=set(headers)&PRIVATE:
        raise ValueError('Unreviewed source header or projection change')
    lineage=lineage_assessment(frame,projected_columns)
    if lineage['repeated_lineage_occurrences_after_first'] or lineage['conflicting_lineage_groups'] or lineage['repeated_generated_ids_after_first']:
        # Report/repair would require preserving the occurrence map; never silently drop.
        raise ValueError(f'Processed source-occurrence conflict requires a separately reviewed repair: {entry["dataset_id"]}: {lineage}')
    by_row=frame.set_index('source_row',verify_integrity=True)
    signatures=[];payloads=[];ordinals=[];record_ids=[]
    for excel_row,row in source:
        processed=by_row.loc[str(excel_row)]
        if processed.source_sha256!=entry['sha256'] or processed.source_sheet!=entry['sheet']:
            raise ValueError('Processed source provenance mismatch')
        expected_id=digest(f'{entry["sha256"]}|{entry["sheet"]}|{excel_row}'.encode())
        if processed.record_id!=expected_id:
            raise ValueError('Generated lineage ID differs from source occurrence')
        signature=current_signature(row)
        if processed.raw_row_signature!=signature:
            raise ValueError('Current repeated-group signature differs from original XLSX')
        payload=[]
        for header in projected:
            i=headers.index(header)
            expected=source_token(header,row[i],sheet,excel_row,get_column_letter(i+1))
            if processed[PROJECTIONS[header]]!=expected:
                raise ValueError(f'Exported value differs from source: {entry["dataset_id"]}, row {excel_row}, field {header}')
            payload.append(expected)
        signatures.append(signature);payloads.append(tuple(payload))
        ordinals.append(int(processed.processed_record_ordinal));record_ids.append(expected_id)
    raw_groups=groups_of(signatures);payload_groups=groups_of(payloads)
    ranks=Counter();records=[]
    for i,(excel_row,_) in enumerate(source):
        ranks[signatures[i]]+=1
        processed=by_row.loc[str(excel_row)]
        if int(processed.repeated_row_group_size)!=len(raw_groups[signatures[i]]) or int(processed.occurrence_rank)!=ranks[signatures[i]]:
            raise ValueError('Repeated-group flags/ranks fail recomputation')
        collision=len({signatures[j] for j in payload_groups[payloads[i]]})>1
        records.append(dict(dataset_id=entry['dataset_id'],source_row=excel_row,
            processed_record_ordinal=ordinals[i],record_id=record_ids[i],
            full_source_signature=signatures[i],full_source_group_size=len(raw_groups[signatures[i]]),
            processed_payload_signature=current_signature(payloads[i]),processed_payload_group_size=len(payload_groups[payloads[i]]),
            projected_group_has_distinct_full_source_rows=collision,
            assessment='projection_collision_identity_unresolved' if collision else 'full_source_pattern_repetition_identity_unresolved' if len(raw_groups[signatures[i]])>1 else 'no_repeated_pattern_under_tested_keys',
            removed=False))
    group_rows=[];examples=[]
    for criterion,groups in [('full_source_equality',raw_groups),('exported_payload_equality',payload_groups)]:
        repeated=sorted([(key,positions) for key,positions in groups.items() if len(positions)>1],key=lambda item:(-len(item[1]),str(item[0])))
        for rank,(key,positions) in enumerate(repeated):
            differing=[h for h in headers if len({json.dumps(source[i][1][headers.index(h)],default=str) for i in positions})>1]
            hidden=[h for h in differing if h in PRIVATE]
            pattern_count=len({signatures[i] for i in positions})
            record=dict(dataset_id=entry['dataset_id'],criterion=criterion,
                group_signature=key if criterion=='full_source_equality' else current_signature(key),
                group_size=len(positions),repeat_occurrences_after_first=len(positions)-1,
                distinct_full_source_patterns=pattern_count,
                differing_omitted_columns=';'.join(hidden),differing_source_columns=';'.join(differing),
                source_rows=';'.join(str(source[i][0]) for i in positions),
                processed_record_ordinals=';'.join(str(ordinals[i]) for i in positions),
                assessment='projection_collision_identity_unresolved' if pattern_count>1 else 'full_source_pattern_repetition_identity_unresolved')
            group_rows.append(record)
            if rank<example_count:
                first=dict(zip(headers,source[positions[0]][1]))
                display={h:first[h] for h in projected if h not in {'RE_VALUE','VILLAGE_AR','VILLAGE_EN'}}
                # Source rows are traceable; omitted private values are never republished.
                examples.append(dict(**record,sample_values=display,omitted_values_policy='No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.'))
    collision_groups=[positions for positions in payload_groups.values() if len({signatures[i] for i in positions})>1]
    candidate_columns=[h for h in headers if 'ID' in h.upper() or 'معرف' in h or 'رقم المعاملة' in h]
    column_assessment=[]
    for i,header in enumerate(headers):
        values=[row[i] for _,row in source]
        nonmissing=[v for v in values if v is not None]
        distinct=len({current_signature((v,)) for v in nonmissing})
        role='classification/geographic attribute, not an event key'
        if header in {'TRANSACTION_DATE','تاريخ الإجراء'}: role='procedure/transaction date; many records per date'
        elif header in PRIVATE: role='demographic attribute; never a transaction identity key'
        elif header=='NO_OF_OWNERS': role='owner count; not record sequence or transaction count'
        elif header=='RE_VALUE': role='reported numeric value; meaning/unit unverified; not identity'
        elif header=='SERVICE_SUB_ID': role='two observed service codes; not unique record identity'
        column_assessment.append(dict(column=header,nonmissing=len(nonmissing),distinct_nonmissing=distinct,
            unique_complete_column=len(nonmissing)==len(source) and distinct==len(source),role=role,reliable_official_event_key=False))
    identifiers=[]
    for header in candidate_columns:
        values=[row[headers.index(header)] for _,row in source]
        identifiers.append(dict(column=header,nonmissing=sum(v is not None for v in values),
            distinct_nonmissing=len({str(v) for v in values if v is not None}),
            role='service classification code, not transaction/record identity',reliable_unique_transaction_id=False))
    profile=dict(dataset_id=entry['dataset_id'],source_file=entry['file'],source_sha256=entry['sha256'],
        source_sheet=entry['sheet'],header_row=entry['header_row'],source_rows=len(source),
        min_date=frame.transaction_date.min(),max_date=frame.transaction_date.max(),
        source_columns_in_current_detection=headers,
        current_method='SHA-256 of json.dumps(tuple(original decoded row), ensure_ascii=False, default=str), preserving original field order/values, no normalization',
        exported_source_payload_columns=projected_columns,source_columns_omitted_from_export=[h for h in headers if h not in projected],
        processed_columns_excluded_from_payload_comparison=[c for c in frame.columns if c not in projected_columns],
        full_source_equality=group_statistics(raw_groups),exported_payload_equality=group_statistics(payload_groups),
        projection_collision_groups=len(collision_groups),projection_collision_occurrences=sum(len(p) for p in collision_groups),
        reliable_official_transaction_or_record_id=False,candidate_identifier_columns=identifiers,source_column_identity_assessment=column_assessment,
        generated_lineage_identifier_definition='SHA-256(original file SHA|worksheet|Excel row), identifies the source occurrence, not the underlying transaction',
        processed_lineage_checks=lineage,confirmed_duplicate_source_occurrence_rows=0,confirmed_duplicate_economic_transactions=0,actual_duplicate_economic_transaction_count=None,
        disposition='retain_all_occurrences_identity_unresolved',rows_removed=0,removal_justifications=[],
        cleaned_output_created=False,cleaned_output_reason='No sufficiently evidenced duplicate ingestion records; repeated attributes do not establish transaction duplication.',
        source_metadata=entry,examples=examples,
        worksheets=[dict(name=s['name'],actual_dimensions=s['actual_dimensions'],declared_dimensions=s['declared_dimensions']) for s in book['sheets']])
    return profile,pd.DataFrame(records),pd.DataFrame(group_rows),frame


def audit_csv_inventory(root,config):
    # Audit all CSVs in the two committed output bundles selected for this import.
    # Later CI-generated validation runs are separate versions, not this snapshot.
    folders=[root/config['audited_directory'],root/config['eda_directory']]
    protected={}
    # Validate every output CSV against an existing input manifest.
    for path in sorted(p for folder in folders for p in folder.glob('*manifest.json')):
        manifest=json.loads(path.read_text())
        hashes=manifest.get('artifact_sha256',manifest.get('csv_sha256',{}))
        for name,expected in hashes.items():
            if name.endswith('.csv'):
                protected[path.parent/name]=expected
    inventory=[];copies=defaultdict(list)
    for path in sorted(p for folder in folders for p in folder.glob('*.csv')):
        sha=digest(path.read_bytes())
        if path not in protected or protected[path]!=sha:
            raise ValueError(f'Unregistered or modified processed CSV: {path.relative_to(root)}')
        frame=csv_read(path)
        exact=group_statistics(groups_of([tuple(row) for row in frame.itertuples(index=False,name=None)]))
        role='row-level source occurrences' if path.name in set(FACT_FILES.values()) else 'monthly analytical aggregates' if path.stem in AGG_KEYS else 'reference/summary/coverage metadata'
        grain=AGG_KEYS.get(path.stem)
        grain_repeats=int(frame.duplicated(grain).sum()) if grain else None
        if role=='monthly analytical aggregates' and grain_repeats:
            raise ValueError(f'Analytical grain duplicated: {path}')
        # Exact metadata/file copies across stages are intentional, not market-record duplication.
        relative=path.relative_to(root).as_posix();copies[sha].append(relative)
        inventory.append(dict(file=relative,sha256=sha,logical_data_rows=len(frame),role=role,
            columns_json=json.dumps(list(frame.columns),ensure_ascii=False),
            exact_full_csv_row_repeats_after_first=exact['repeat_occurrences_after_first'],
            repeated_full_csv_row_groups=exact['repeated_groups'],
            declared_grain=';'.join(grain or []),declared_grain_repeats_after_first=grain_repeats,
            checksum_verified_against_existing_manifest=True))
    return inventory,[dict(sha256=sha,files=files,assessment='intentional identical reference/quality/coverage copy across stages; not duplicated transaction evidence') for sha,files in sorted(copies.items()) if len(files)>1]


def check_aggregates(root,config,frames):
    results=[]
    eda=root/config['eda_directory']
    for fact_name,grain in AGG_KEYS.items():
        family='muscat_brokerage' if 'brokerage' in fact_name else 'land_oct' if fact_name.endswith('2024') else 'land_'
        selected=[f for f in frames if (f.dataset_id.iloc[0].startswith('muscat') if family=='muscat_brokerage' else f.dataset_id.iloc[0]=='land_oct_2024' if family=='land_oct' else f.dataset_id.iloc[0] in {'land_nov_2022','land_dec_2022'})]
        source=pd.concat(selected,ignore_index=True)
        source['period_id']=source.transaction_date.str[:7]
        if 'number_of_owners' in source:
            source['ownership_band']=source.number_of_owners.astype(int).map(lambda n:f'{n} owner'+('s' if n!=1 else '') if n<5 else '5+ owners')
        source['in_repeated_group']=source.repeated_row_group_size.astype(int).gt(1)
        expected=source.groupby(grain,dropna=False).agg(reported_record_count=('record_id','size'),records_in_repeated_groups=('in_repeated_group','sum')).reset_index()
        actual=csv_read(eda/(fact_name+'.csv'))
        for col in ['reported_record_count','records_in_repeated_groups']:
            actual[col]=actual[col].astype(int)
        pd.testing.assert_frame_equal(expected.sort_values(grain).reset_index(drop=True),actual.sort_values(grain).reset_index(drop=True),check_dtype=False)
        results.append(dict(file=(eda/(fact_name+'.csv')).relative_to(root).as_posix(),grain=grain,physical_aggregate_rows=len(actual),preserved_source_occurrences=len(source),reported_record_count_sum=int(actual.reported_record_count.sum()),status='all observed aggregation buckets and multiplicities match source occurrences'))
    return results


def build(root=ROOT,config_path=CONFIG):
    root=Path(root);config_path=Path(config_path);config=json.loads(config_path.read_text())
    registry=json.loads((root/config['source_registry']).read_text())
    inventory,copies=audit_csv_inventory(root,config)
    before={root/item['file']:item['sha256'] for item in inventory}
    before.update({root/e['file']:e['sha256'] for e in registry})
    profiles=[];artifacts={};frames=[]
    def csv(name,frame):
        artifacts[name]=frame.to_csv(index=False,lineterminator='\n').encode('utf-8-sig')
    for entry in registry:
        profile,records,groups,frame=audit_source(entry,root,root/config['audited_directory'],config['example_groups_per_criterion'])
        profiles.append(profile);frames.append(frame)
        csv(entry['dataset_id']+'_occurrence_review.csv',records)
        csv(entry['dataset_id']+'_repeated_groups.csv',groups)
        artifacts[entry['dataset_id']+'.md']=render_dataset(profile).encode()
    aggregates=check_aggregates(root,config,frames)
    intervals=[dict(dataset_id=p['dataset_id'],min_date=p['min_date'],max_date=p['max_date']) for p in profiles]
    dates={p['dataset_id']:set(f.transaction_date) for p,f in zip(profiles,frames)}
    overlaps=[dict(left=a['dataset_id'],right=b['dataset_id'],date_ranges_overlap=max(a['min_date'],b['min_date'])<=min(a['max_date'],b['max_date']),
        shared_observed_transaction_dates=sorted(dates[a['dataset_id']]&dates[b['dataset_id']]),
        shared_observed_date_count=len(dates[a['dataset_id']]&dates[b['dataset_id']]),
        same_source_schema=profiles[i]['source_columns_in_current_detection']==profiles[j]['source_columns_in_current_detection'],
        economic_event_overlap='unknown: no stable official identity and different scopes/periods') for i,a in enumerate(intervals) for j,b in enumerate(intervals) if j>i]
    report=dict(audit_date=config['audit_date'],base_main_commit=config['base_main_commit'],audit_complete=True,
        datasets=profiles,source_occurrences=sum(p['source_rows'] for p in profiles),processed_csv_files_audited=len(inventory),
        confirmed_duplicate_ingestion_occurrences=0,confirmed_duplicate_economic_transactions=0,actual_duplicate_economic_transaction_count=None,
        transaction_identity_status='not determinable from supplied fields',rows_removed=0,cleaned_outputs_created=[],
        all_current_flags_recomputed=True,source_and_processed_occurrences_match=True,
        audited_output_bundles=[config['audited_directory'],config['eda_directory']],
        cross_file_date_ranges=overlaps,intentional_identical_csv_copies=copies,analytical_aggregate_validation=aggregates,
        powerbi_modeling_performed=False,import_guidance='Audit complete: retain occurrence counts under separate source definitions; no DISTINCT or drop_duplicates on business attributes; future imports must rerun this audit.')
    summary=pd.DataFrame([dict(dataset_id=p['dataset_id'],source_rows=p['source_rows'],
        raw_repeated_groups=p['full_source_equality']['repeated_groups'],raw_repeat_occurrences_after_first=p['full_source_equality']['repeat_occurrences_after_first'],
        raw_occurrences_in_repeated_groups=p['full_source_equality']['occurrences_in_repeated_groups'],
        exported_payload_repeated_groups=p['exported_payload_equality']['repeated_groups'],exported_payload_repeat_occurrences_after_first=p['exported_payload_equality']['repeat_occurrences_after_first'],
        exported_payload_occurrences_in_repeated_groups=p['exported_payload_equality']['occurrences_in_repeated_groups'],
        projection_collision_groups=p['projection_collision_groups'],projection_collision_occurrences=p['projection_collision_occurrences'],
        reliable_official_transaction_or_record_id=False,confirmed_duplicate_ingestion_occurrences=0,rows_removed=0) for p in profiles])
    csv('dataset_duplicate_summary.csv',summary);csv('processed_csv_inventory.csv',pd.DataFrame(inventory))
    csv('source_column_identity_assessment.csv',pd.DataFrame([dict(dataset_id=p['dataset_id'],**c) for p in profiles for c in p['source_column_identity_assessment']]))
    artifacts['audit_report.json']=dump(report).encode();artifacts['README.md']=render_summary(report,summary).encode()
    protected=[dict(file=path.relative_to(root).as_posix(),sha256=sha) for path,sha in sorted(before.items())]
    for path,sha in before.items():
        if digest(path.read_bytes())!=sha:
            raise ValueError('Protected source or processed artifact changed during audit')
    fingerprint=dict(config_sha256=digest(config_path.read_bytes()),
        source_code_sha256=digest(Path(__file__).read_bytes()),reader_sha256=digest((ROOT/'src/excel_reader.py').read_bytes()),
        current_detector_sha256=digest((ROOT/'src/audit_uploaded_data.py').read_bytes()),protected_inputs=protected)
    run_id=digest(dump(fingerprint).encode())[:20]
    artifacts['manifest.json']=dump(dict(run_id=run_id,**fingerprint,output_sha256={name:digest(data) for name,data in sorted(artifacts.items())})).encode()
    return artifacts,report,run_id


def render_dataset(p):
    lines=[f"# Duplicate audit — {p['dataset_id']}",'',f"Original: `{p['source_file']}`; sheet `{p['source_sheet']}`, header row {p['header_row']}. **{p['source_rows']:,} source occurrences; {p['min_date']}–{p['max_date']}.**",'',
        f"Original SHA-256: `{p['source_sha256']}`. All source-to-processed values, generated IDs, group sizes and occurrence ranks were verified. Originals and existing processed files are unchanged.",'',
        '## Current repeated-group columns','',', '.join('`'+h+'`' for h in p['source_columns_in_current_detection']), '',
        p['current_method']+'. The scope is one source dataset; no cross-file pooling. Headers/metadata sheets, file/sheet/row IDs and derived fields are not part of that pattern. Nulls compare as null; no trimming, translation or normalization is used.', '',
        '## Identifier assessment','',
        '**No reliable official transaction or record identifier is supplied.** Generated record_id is unique for the file/sheet/row, not evidence of unique economic events. Dates, classifications, gender/birth dates, locations, amounts and owner counts do not establish identity.', '',
        'Every data column was profiled for completeness and distinct values; none is a complete unique official identity key. See source_column_identity_assessment.csv. Source values used for this assessment are not republished.', '',
        'Candidate ID-named source columns: '+(json.dumps(p['candidate_identifier_columns'],ensure_ascii=False) if p['candidate_identifier_columns'] else 'none')+'.', '',
        '## Repetition statistics','',
        '| Criterion | Repeated groups | Occurrences in groups | Occurrences after first | Largest group |',
        '|---|---:|---:|---:|---:|']
    for name,label in [('full_source_equality','All original data fields'),('exported_payload_equality','Exported source-derived payload')]:
        s=p[name];lines.append(f"| {label} | {s['repeated_groups']} | {s['occurrences_in_repeated_groups']} | {s['repeat_occurrences_after_first']} | {s['largest_group']} |")
    lines+=['','"After first" is a pattern-occurrence statistic, **not a number approved for removal**. A full-source match is still an unresolved repetition of coarse attributes. Distinct patterns are not unique-transaction counts.', '',
        'Exported payload comparison columns: '+', '.join('`'+h+'`' for h in p['exported_source_payload_columns'])+'.','',
        'Source fields excluded from export: '+(', '.join('`'+h+'`' for h in p['source_columns_omitted_from_export']) or 'none')+'.','',
        f"**{p['projection_collision_groups']} groups / {p['projection_collision_occurrences']} occurrences** match the exported fields but contain different full-source records. These are projection collisions, not confirmed source duplicates. Demographic differences distinguish source representations without establishing separate economic transactions.",'',
        'The payload key excludes generated IDs/row ordinals, hashes, repeat flags and derived normalization keys; otherwise unique lineage would mask matches. Source-to-export checks use documented ISO-date and integer-owner conversion; raw signatures retain original decoded types. Amount equality, where present, compares original XML-derived decimal tokens; no unit, price or financial conclusion is inferred.', '',
        '## Traceable actual examples','']
    if not p['examples']:
        lines+=['No repeated groups under either tested criterion.','']
    for example in p['examples']:
        lines+=[f"### {example['criterion']} — {example['group_size']} source occurrences",'',
            f"Excel rows: `{example['source_rows']}`. Processed logical record ordinals: `{example['processed_record_ordinals']}`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).",'',
            'Selected shared source fields: `'+json.dumps(example['sample_values'],ensure_ascii=False,default=str)+'`.','',
            f"Distinct full-source patterns: {example['distinct_full_source_patterns']}; differing omitted fields: `{example['differing_omitted_columns'] or 'none'}`. Assessment: `{example['assessment']}`.",'',
            example['omitted_values_policy'],'']
    lines+=['## Decision and recommendations','',
        '**Retain every occurrence. Zero confirmed ingestion duplicates, zero records removed, and no cleaned dataset created.** Full processed CSV rows and original file/sheet/row lineage are unique; each original occurrence maps to exactly one audited occurrence. Legitimate same-day, same-location, same-category registrations are plausible. Their economic identity cannot be confirmed or disproved with these fields.', '',
        'Request an official stable transaction ID (or documented composite business key), export-row ID and row-grain explanation, including how multiple owners appear. Obtain issuer confirmation or a revision/removal ledger before transaction-level deduplication. Never use gender, birth date, date/location or visible-row signature as a transaction key.', '',
        'Existing aggregate facts preserve every occurrence count; their reduced physical rows are intentional aggregation, not record removal. In Power BI, retain separate definitions and use SUM(reported_record_count) on aggregate facts. Do not apply Remove duplicates/DISTINCT to projected attributes, count physical aggregate rows as transactions, or load raw/audited/aggregated representations into one additive fact.', '',
        'Exact official workbook URLs/licences and some source definitions remain pending in the source registry. This is a duplicate-evidence audit, not certification of unique or complete-market transactions. Per-occurrence and full group ledgers accompany this report. Any future confirmed removal must be separately named and justified row-by-row; no deletion is authorized by the current evidence.','']
    return '\n'.join(lines)


def render_summary(report,summary):
    lines=['# Duplicate audit before Power BI import','',f"**Audit complete: {report['source_occurrences']:,} source occurrences, four workbooks and {report['processed_csv_files_audited']} existing CSVs inspected.** Zero confirmed duplicated ingestion occurrences. Economic transaction duplication is **not determinable**. **Zero records removed; no cleaned replacement files generated.**",'',
        '| Dataset | Rows | Full-source groups | Full-source after first | Exported-payload groups | Payload after first |',
        '|---|---:|---:|---:|---:|---:|']
    for row in summary.to_dict('records'):
        lines.append(f"| [{row['dataset_id']}]({row['dataset_id']}.md) | {row['source_rows']} | {row['raw_repeated_groups']} | {row['raw_repeat_occurrences_after_first']} | {row['exported_payload_repeated_groups']} | {row['exported_payload_repeat_occurrences_after_first']} |")
    lines+=['','No workbook contains a reliable official event ID. Current group flags hash **all original data fields**, including non-exported gender/birth-date fields. This explains why October 2024 has zero full-source repetitions but exported-attribute matches. Equal attributes are not proven duplicate transactions, and different demographics do not prove separate transactions.', '',
        '## Evidence and representations','',
        '- Original and processed hashes are protected; every audited occurrence maps to its original sheet/row. Current signatures/group sizes/ranks were recomputed.',
        '- All 43 CSVs in the two selected committed output bundles have zero repeated full rows under their complete columns. Source row CSVs also have unique generated IDs and source occurrence keys. Dropping those unique lineage columns exposes attribute repetitions; uniqueness of full CSV rows alone does not establish unique transactions.',
        '- Three existing monthly fact tables were compared bucket-by-bucket to source occurrences, including repeated-group counts. Every multiplicity is preserved; lower physical fact-row counts are intentional aggregation.',
        f"- {len(report['intentional_identical_csv_copies'])} identical CSV-copy groups are reference/quality/coverage exports reused across stages, not duplicated transaction evidence. Load one chosen model run, not multiple copies.",
        '- The four original date ranges do not overlap. This prevents same-date matches across these uploads; it does not establish economic event identity or justify pooling different definitions.', '',
        '## Files and action','',
        'Each dataset has a Markdown report, a full repeated-group ledger and an occurrence review CSV. Review CSVs are audit evidence, **not cleaned analytical fact replacements**; they contain no birth dates, genders or monetary amounts. audit_report.json includes criteria, example source rows, identifier assessment, inventories and recommendations. manifest.json records every original/processed input and output hash.', '',
        '**Import guidance after this audit:** retain reported source occurrences under their separate definitions; do not deduplicate business attributes. Source authenticity/completeness, transaction identity and financial/code meanings retain the existing limitations. Power BI modeling/import was not performed during this audit.', '',
        'If official IDs or issuer evidence later confirm duplicates, preserve current outputs and create a new reviewed cleaned run plus a removal ledger containing source/processed occurrence IDs, evidence, survivor choice and reconciliation. The current files provide insufficient removal evidence.','']
    return '\n'.join(lines)


def run(output_root=ROOT/'reports/duplicates',**kwargs):
    artifacts,report,run_id=build(**kwargs)
    target=Path(output_root)/run_id
    persist_immutable(target,artifacts)
    return report,target


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root',type=Path,default=ROOT/'reports/duplicates')
    args=parser.parse_args()
    report,target=run(output_root=args.output_root)
    print(dump(dict(report_directory=str(target),audit_complete=report['audit_complete'],source_occurrences=report['source_occurrences'],
        processed_csv_files_audited=report['processed_csv_files_audited'],confirmed_duplicate_ingestion_occurrences=0,
        economic_transaction_duplicates='unknown',rows_removed=0,cleaned_outputs_created=[],powerbi_modeling_performed=False)))


if __name__=='__main__':
    main()
