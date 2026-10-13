"""Reproduce scoped EDA tables, figures, findings, and executed notebook offline."""
import argparse
import json
import os
from pathlib import Path
import tempfile

from src.eda_analysis import ROOT, CONFIG, SCOPES, digest, load_inputs, summarize


def text_json(value):
    return json.dumps(value,ensure_ascii=False,indent=2,default=str)+'\n'


def markdown_table(frame,columns,formatters=None):
    # No optional tabulate dependency; only computed source-backed rows are rendered.
    formatters=formatters or {}
    lines=['| '+' | '.join(columns)+' |','| '+' | '.join(['---']*len(columns))+' |']
    for row in frame[columns].to_dict('records'):
        lines.append('| '+' | '.join(formatters.get(c,str)(row[c]).replace('|',' / ').replace('\n',' ') for c in columns)+' |')
    return '\n'.join(lines)


def findings(tables,run_id):
    summary=tables['dataset_summary'];g=tables['governorate_counts'];w=tables['wilayat_counts']
    comparison=tables['governorate_nov_dec_2022'];broker=tables['brokerage_wilayat_counts'].sort_values('reported_record_count',ascending=False)
    monthly=tables['brokerage_monthly_counts'];land2024=g[g.period_id.eq('2024-10')].sort_values('reported_record_count',ascending=False)
    november=int(summary.loc[summary.dataset_id.eq('land_nov_2022'),'reported_record_count'].iloc[0])
    december=int(summary.loc[summary.dataset_id.eq('land_dec_2022'),'reported_record_count'].iloc[0])
    total_broker=int(broker.reported_record_count.sum());peak=monthly.loc[monthly.reported_record_count.idxmax()];low=monthly.loc[monthly.reported_record_count.idxmin()]
    top_broker=broker.head(2);topthree=land2024.head(3);residential=tables['brokerage_property_use'].query('property_use_ar == "سكني"').iloc[0]
    vacant=tables['brokerage_property_description'].query('property_description_ar == "أرض فضاء"').iloc[0]
    november_top=g[g.period_id.eq('2022-11')].sort_values(['reported_record_count','governorate_id'],ascending=[False,True]).head(2)
    lead1,lead2=november_top.iloc[0],november_top.iloc[1]
    q2024=tables['data_quality_summary'].query('dataset_id == "land_oct_2024"').iloc[0]
    govlead=[]
    for period in ['2022-11','2022-12']:
        data=g[g.period_id.eq(period)].sort_values(['reported_record_count','governorate_id'],ascending=[False,True]);leader=data.iloc[0]
        govlead.append(f"- {period}: **{leader.governorate_en}** has {leader.reported_record_count:,} rows ({leader.share_pct:.2f}% of that file).")
    lines=['# Exploratory findings — supplied record occurrences', '',f'Analysis run `{run_id}`; input audit `71008482abd46aa7f0bc`; base main `2c4237a` (merged PR #4).', '',
        '**Interpretation:** counts describe uploaded source record occurrences. Completeness and unique transaction identity are unverified; repeated visible rows remain. The three scopes are never pooled into a national sales series. No monetary or price conclusion is calculated.', '',
        '## Data used', '',markdown_table(summary,['dataset_id','reported_record_count','first_record_date','last_record_date','observed_governorates','observed_wilayat_labels']), '',
        'All four originals and every audited artifact match their pinned checksums. The land months represent all eleven modern governorates; the 2025 dataset covers Muscat only. Its nine months are not full-year coverage. Wilayat-label totals include nonstandard source labels, not a certified administrative inventory.', '',
        '## 2022 land: two same-layout monthly snapshots', '',
        f'November has **{november:,}** reported rows and December **{december:,}**: a difference of **{december-november:+,}** ({100*(december-november)/november:+.2f}% relative to the November file). This is a supplied-file comparison, not verified market contraction or an annual trend.', '',
        *govlead, '',
        f'November’s top two are {lead1.governorate_en} ({int(lead1.reported_record_count):,}) and {lead2.governorate_en} ({int(lead2.reported_record_count):,}), separated by {int(lead1.reported_record_count-lead2.reported_record_count):,} row(s); the rank alone does not establish a substantive market distinction. December’s geographic composition differs from November:', '',
        markdown_table(comparison.sort_values('share_change_percentage_points',ascending=False),['governorate_en','november_records','december_records','november_share_pct','december_share_pct','share_change_percentage_points'],
            {c:(lambda v:f'{v:.2f}') for c in ['november_share_pct','december_share_pct','share_change_percentage_points']}), '',
        'Share shifts are percentage points, not property appreciation. Different source coverage or record-generation processes could affect these patterns. Two Dhofar rows labelled الساحل الشرقي are excluded only from wilayat rankings; all source rows remain in governorate totals. The complete observed wilayat table accompanies the top-ten charts.', '',
        '## October 2024 land: separate service-coded snapshot', '',
        f'**{land2024.iloc[0].governorate_en}** has the highest supplied count ({int(land2024.iloc[0].reported_record_count):,}; {land2024.iloc[0].share_pct:.2f}%). The top three are '+', '.join(topthree.governorate_en)+f', with {int(topthree.reported_record_count.sum()):,} rows ({topthree.share_pct.sum():.2f}% of the October file). This is a within-file concentration measure, not a cross-year trend or investment ranking.', '',
        markdown_table(tables['service_code_counts_2024'],['service_sub_id','reported_record_count','share_pct'],{'share_pct':lambda v:f'{v:.2f}'}), '',
        f'RN13A/RN13C are literal service codes with unverified meanings; neither is classified as sales, mortgages or another economic category. RE_VALUE contains {int(q2024.reported_amount_present_records):,} reported numbers and {int(q2024.reported_amount_missing_records):,} blanks. Units and meanings are unresolved, so amounts are excluded from analytical facts and DAX calculations.', '',
        '## Muscat brokerage: January–September 2025', '',
        f'**{total_broker:,}** brokerage-office registrations are present. The highest supplied month is **{peak.period_id}**, with **{int(peak.reported_record_count):,}** rows, and the lowest is **{low.period_id}**, with **{int(low.reported_record_count):,}**. No missing month or year-end projection is created. Seasonality is not established by one partial year.', '',
        f'Wilayats **'+ ' and '.join(top_broker.wilayat_ar)+f'** together account for **{int(top_broker.reported_record_count.sum()):,}** rows (**{top_broker.share_pct.sum():.2f}%**). This describes geographic distribution inside the brokerage scope; it does not establish national demand or investment returns.', '',
        f'The original residential-use label **سكني** appears on **{int(residential.reported_record_count):,}** rows (**{residential.share_pct:.2f}%**). The separate vacant-land description **أرض فضاء** appears on **{int(vacant.reported_record_count):,}** (**{vacant.share_pct:.2f}%**). Use and description are different fields and must not be added together as categories of one classification.', '',
        f"{len(tables['brokerage_property_use'])} property-use labels, {len(tables['brokerage_property_description'])} property-description labels and {len(tables['brokerage_transaction_category'])} registration-category label(s) are supplied. Raw Arabic labels are preserved. Category distributions describe registered records, not the stock, supply or prices of all properties.", '',
        '## Buyer and ownership attributes', '',
        markdown_table(tables['buyer_type_counts'],['period_id','buyer_type','reported_record_count','share_pct'],{'share_pct':lambda v:f'{v:.2f}'}), '',
        'Individual is the predominant reported buyer label in each file. Owner-count bands measure ownership multiplicity; they are not independent buyers, transaction counts or property prices. Five or more owners are grouped explicitly for readable distributions.', '',
        '## Reliability and recommended decisions', '',
        '1. Use regional and category distributions to prioritize further official data verification and investigation within each supplied scope. These files alone do not support investment recommendations.',
        '2. Obtain complete comparable monthly series before trend, seasonality or annual-growth analysis. No 2020, 2021, 2023 or 2026 uploads exist; 2022 and 2024 are isolated land snapshots; 2025 brokerage is Muscat-only and partial year.',
        '3. Confirm source URLs/licences, land-file publication dates, source completeness, transaction identity, service definitions and financial units before broader or monetary conclusions. Muscat’s embedded publication label predates some records.',
        '4. Keep Power BI pages and measures separate by dataset definition. Count occurrences with SUM of the prepared count field; do not count aggregated fact rows or sum owner numbers as transactions.', '',
        'Figures are generated by pandas/Matplotlib/Seaborn, and their chart-data tables are committed beside the Power BI facts. Methodology, transformations and provenance are documented in `docs/eda_methodology.md` and the source registry. All counts/shares reconcile; no originals are modified.', '']
    return '\n'.join(lines)


def persist_immutable(target,artifacts):
    target=Path(target)
    if target.exists():
        existing={p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file()}
        if existing!=set(artifacts) or any((target/name).read_bytes()!=data for name,data in artifacts.items()):
            raise ValueError(f'Existing analysis output differs; refusing to overwrite {target}')
        return
    target.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.pending-',dir=target.parent) as staging:
        for name,data in artifacts.items():
            path=Path(staging)/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        Path(staging).rename(target)


def run(execute_notebook=True,output_root=ROOT):
    # The configured inputs always come from the repository; tests may redirect derived outputs.
    output_root=Path(output_root)
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'work/mpl-cache'))
    os.environ.setdefault('XDG_CACHE_HOME',str(ROOT/'work/cache'))
    from src.eda_figures import generate_figures
    inputs=load_inputs();tables=summarize(inputs)
    components=[ROOT/'src'/name for name in ['eda_analysis.py','eda_figures.py','eda_notebook.py','run_eda.py']]+[CONFIG,ROOT/'requirements-lock.txt']
    implementation={p.relative_to(ROOT).as_posix():digest(p.read_bytes()) for p in components}
    run_id=digest(text_json(dict(input_manifest=inputs['config']['audit_manifest_sha256'],implementation=implementation)).encode())[:20]
    table_dir=Path('data/processed/eda')/run_id
    figures_dir=Path('reports/figures/eda')/run_id
    report_dir=Path('reports/eda')/run_id
    csv_artifacts={name+'.csv':frame.to_csv(index=False,lineterminator='\n').encode('utf-8-sig') for name,frame in tables.items()}
    csv_hashes={name:digest(data) for name,data in csv_artifacts.items()}
    with tempfile.TemporaryDirectory(prefix='oman-eda-') as temporary:
        generated=Path(temporary)/'figures';figure_names=generate_figures(tables,generated,run_id)
        figure_artifacts={p.name:p.read_bytes() for p in generated.iterdir()}
    insight_bytes=findings(tables,run_id).encode()
    manifest=dict(run_id=run_id,base_main_commit=inputs['config']['base_main_commit'],merged_audit_pr=4,
        input_audit_directory=inputs['config']['audit_directory'],input_manifest_sha256=inputs['config']['audit_manifest_sha256'],
        input_artifact_sha256=inputs['manifest']['artifact_sha256'],original_sha256=inputs['manifest']['source_sha256'],
        implementation_sha256=implementation,metric='reported_record_occurrences',monetary_analysis=False,
        source_occurrences=inputs['audit_report']['record_count'],table_rows={name:len(table) for name,table in tables.items()},
        fact_reconciliation={family:dict(aggregated_rows=len(tables['fact_'+family]),reported_record_count=int(tables['fact_'+family].reported_record_count.sum()),source_rows=len(frame)) for family,frame in inputs['facts'].items()},
        csv_sha256=csv_hashes,figure_sha256={name:digest(data) for name,data in figure_artifacts.items()},
        insights_sha256=digest(insight_bytes),figure_names=figure_names,
        counts_are_not_unique_transactions=True,ready_for_continuous_2020_2026_or_monetary_analysis=False)
    csv_artifacts['analysis_manifest.json']=text_json(manifest).encode()
    # Every bundle is checked before any existing output is accepted; originals are read-only.
    persist_immutable(output_root/table_dir,csv_artifacts)
    persist_immutable(output_root/figures_dir,figure_artifacts)
    persist_immutable(output_root/report_dir,{'insights.md':insight_bytes})
    result=dict(run_id=run_id,tables_directory=table_dir.as_posix(),figures_directory=figures_dir.as_posix(),
                report_directory=report_dir.as_posix(),csv_tables=len(tables),figures=len(figure_names),
                source_record_occurrences=inputs['audit_report']['record_count'],fact_reconciliation=manifest['fact_reconciliation'])
    if execute_notebook:
        if output_root.resolve()!=ROOT.resolve():
            raise ValueError('Executed notebook requires repository-root outputs')
        from src.eda_notebook import notebook_source,execute
        import nbformat
        notebook=execute(notebook_source(run_id),ROOT)
        target=ROOT/'notebooks/01_scoped_real_estate_eda.ipynb'
        payload=nbformat.writes(notebook).encode()+b'\n'
        # This is a generated presentation artifact; any handwritten notebook is protected.
        if target.exists():
            existing=nbformat.read(target,as_version=4)
            if existing.metadata.get('oman_eda',{}).get('generated_by')!='src.eda_notebook':
                raise ValueError('Refusing to replace a handwritten notebook')
        target.write_bytes(payload)
        result['executed_notebook']=target.relative_to(ROOT).as_posix()
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-notebook',action='store_true',help='Produce tables/figures only (normal run executes notebook)')
    args=parser.parse_args()
    print(text_json(run(execute_notebook=not args.no_notebook)))


if __name__=='__main__':
    main()
