"""Publication-style figures with original Arabic labels shaped for display only."""
from pathlib import Path
import calendar

import arabic_reshaper
from bidi.algorithm import get_display
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import numpy as np
import seaborn as sns

from src.eda_analysis import SCOPES

NAVY='#17324D'; TEAL='#007F82'; GOLD='#D28A36'; GREY='#E8EDF1'
SCOPE_TITLES={SCOPES['land_2022']:'2022 land • BuySell layout',SCOPES['land_2024']:'2024 land • service-coded layout',SCOPES['brokerage_2025']:'2025 Muscat • brokerage registrations'}
FIGURE_TITLES={
 'coverage_calendar':'Reporting coverage • 2020–2026',
 'coverage_governorates':'Governorate coverage • supplied datasets only',
 'land_2022_governorates':'2022 land records • governorate distribution',
 'land_2022_share_change':'2022 land records • change in geographic share',
 'land_2022_wilayats':'2022 land records • ten highest wilayat counts per month',
 'land_2024_governorates':'October 2024 land records • governorate distribution',
 'land_2024_wilayats':'October 2024 land records • ten highest wilayat counts',
 'land_2024_service_codes':'October 2024 • observed service-code mix',
 'land_buyer_types':'Land records • reported buyer types within each file',
 'land_ownership_bands':'Land records • number of owners within each file',
 'muscat_monthly':'Muscat brokerage • nine supplied months of 2025',
 'muscat_wilayats':'Muscat brokerage • wilayat distribution, Jan–Sep 2025',
 'muscat_property_categories':'Muscat brokerage • observed property classifications',
 'muscat_wilayat_monthly':'Muscat brokerage • supplied wilayat/month distribution',
}


def arabic(text):
    """Presentation-only shaping; never used for data grouping or join keys."""
    return get_display(arabic_reshaper.reshape(str(text)))


def bars(ax,data,label,value='reported_record_count',color=TEAL,limit=None,rtl=False):
    data=data.sort_values([value,label],ascending=[False,True])
    if limit:
        data=data.head(limit)
    labels=[arabic(v) if rtl else str(v) for v in data[label]]
    positions=np.arange(len(data));values=data[value].to_numpy()
    ax.barh(positions,values,color=color,height=.68)
    ax.set_yticks(positions,labels);ax.invert_yaxis()
    ax.set_xlim(0,max(values)*1.22)
    for y,v in zip(positions,values):
        ax.text(v+max(values)*.014,y,f'{v:,.0f}',va='center',fontsize=9,color=NAVY)
    ax.set_xlabel('Reported record occurrences');ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    ax.grid(axis='y',visible=False);sns.despine(ax=ax,left=True)


def generate_figures(tables,output_dir,run_id):
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    sns.set_theme(style='whitegrid',font='DejaVu Sans',font_scale=.95,rc={
        'axes.edgecolor':'#D2DBE3','grid.color':'#E8EDF1','axes.labelcolor':NAVY,
        'text.color':NAVY,'xtick.color':NAVY,'ytick.color':NAVY,'svg.hashsalt':run_id})
    names=[]
    def save(name,fig,note):
        fig.suptitle(FIGURE_TITLES[name],x=.02,y=.98,ha='left',fontsize=16,fontweight='bold',color=NAVY)
        fig.text(.02,.025,'Source: four uploaded workbooks; SHA-256 verified audit. '+note,
                 fontsize=8.3,va='bottom',color='#526777')
        fig.tight_layout(rect=(0,.10,1,.91))
        for ext in ('png','svg'):
            metadata={'Date':None,'Creator':'Oman real estate scoped EDA'} if ext=='svg' else {'Software':'Oman real estate scoped EDA'}
            fig.savefig(output_dir/f'{name}.{ext}',dpi=180,facecolor='white',metadata=metadata)
        plt.close(fig);names.append(name)
    coverage=tables['coverage_matrix_2020_2026'];govs=tables['dim_governorate'].sort_values('governorate_en')
    fig,axes=plt.subplots(1,3,figsize=(15,6))
    for ax,(scope,title) in zip(axes,SCOPE_TITLES.items()):
        supplied=coverage[(coverage.scope_id==scope)&(coverage.availability_status=='observed')].groupby(['year','month']).size().unstack('month')
        grid=supplied.reindex(index=range(2020,2027),columns=range(1,13))
        ax.set_facecolor(GREY)
        sns.heatmap(grid,mask=grid.isna(),annot=True,fmt='.0f',cmap=sns.light_palette(TEAL,as_cmap=True),
                    vmin=0,vmax=11,cbar=False,linewidths=1,linecolor='white',ax=ax,
                    xticklabels=list(calendar.month_abbr)[1:])
        ax.set_title(title,fontsize=11,pad=14);ax.set_xlabel('Month');ax.set_ylabel('Reporting year')
        ax.tick_params(axis='x',labelrotation=90)
    save('coverage_calendar',fig,'Cells show governorates represented, not transaction values.\nGrey = no supplied observations; no months are imputed. 2026 has no uploaded data.')
    observed=tables['coverage_observed'];periods=tables['dim_period'].period_id.tolist()
    labels=['Land\n'+p for p in periods[:3]]+['Brokerage\n'+p for p in periods[3:]]
    matrix=observed.assign(available=1).pivot(index='governorate_id',columns='period_id',values='available').reindex(index=govs.governorate_id,columns=periods)
    fig,ax=plt.subplots(figsize=(13,7));ax.set_facecolor(GREY)
    sns.heatmap(matrix,mask=matrix.isna(),vmin=0,vmax=1,cmap=[GREY,TEAL],cbar=False,linewidths=1,linecolor='white',
        xticklabels=labels,yticklabels=govs.governorate_en,ax=ax)
    ax.tick_params(axis='x',labelrotation=45);ax.set_ylabel('');ax.set_xlabel('Actual supplied periods • different dataset definitions')
    save('coverage_governorates',fig,'Green = rows available. Grey = outside source scope/not supplied, never zero market activity.')
    g=tables['governorate_counts'];w=tables['wilayat_counts']
    fig,axes=plt.subplots(1,2,figsize=(14,7))
    for ax,period,color in zip(axes,['2022-11','2022-12'],[NAVY,TEAL]):
        subset=g[g.period_id.eq(period)];bars(ax,subset,'governorate_en',color=color)
        ax.set_title(f'{period} | {subset.reported_record_count.sum():,} rows',fontweight='bold')
    common_max=g[g.period_id.isin(['2022-11','2022-12'])].reported_record_count.max()*1.22
    for ax in axes: ax.set_xlim(0,common_max)
    save('land_2022_governorates',fig,'Ranks are within each monthly BuySell file. Source completeness/unique transactions unconfirmed.')
    change=tables['governorate_nov_dec_2022'].sort_values('share_change_percentage_points')
    fig,ax=plt.subplots(figsize=(11,7));values=change.share_change_percentage_points
    ax.barh(change.governorate_en,values,color=[TEAL if v>0 else GOLD for v in values])
    ax.axvline(0,color=NAVY,linewidth=1);ax.set_xlabel('December share minus November share (percentage points)')
    ax.set_xlim(values.min()-1,values.max()+1)
    for y,v in enumerate(values):
        ax.text(v+(.08 if v>=0 else -.08),y,f'{v:+.2f} pp',ha='left' if v>=0 else 'right',va='center',fontsize=9)
    sns.despine(ax=ax,left=True);ax.grid(axis='y',visible=False)
    save('land_2022_share_change',fig,'Same-layout two-month composition comparison only; not an annual trend, price change or market growth estimate.')
    fig,axes=plt.subplots(1,2,figsize=(13,7))
    for ax,period,color in zip(axes,['2022-11','2022-12'],[NAVY,TEAL]):
        subset=w[w.period_id.eq(period)&~w.nonstandard_wilayat_label]
        bars(ax,subset,'wilayat_ar',limit=10,rtl=True,color=color);ax.set_title(period,fontweight='bold')
    common_max=w[w.period_id.isin(['2022-11','2022-12'])&~w.nonstandard_wilayat_label].reported_record_count.max()*1.22
    for ax in axes: ax.set_xlim(0,common_max)
    save('land_2022_wilayats',fig,'Original Arabic labels; two nonstandard Dhofar label rows excluded from wilayat ranks only.\nAll source rows remain in governorate totals and summary tables.')
    fig,ax=plt.subplots(figsize=(11,7));bars(ax,g[g.period_id.eq('2024-10')],'governorate_en')
    save('land_2024_governorates',fig,'Service-coded October snapshot; do not pool with 2022 BuySell or Muscat brokerage records.')
    fig,ax=plt.subplots(figsize=(11,7));bars(ax,w[w.period_id.eq('2024-10')&~w.nonstandard_wilayat_label],'wilayat_ar',limit=10,rtl=True)
    save('land_2024_wilayats',fig,'Original Arabic wilayat labels; ranking describes uploaded October records only.')
    service=tables['service_by_governorate_2024'].pivot(index='governorate_en',columns='service_sub_id',values='share_pct').fillna(0).sort_index()
    fig,ax=plt.subplots(figsize=(11,7));service.plot.barh(stacked=True,color=[GOLD,TEAL],ax=ax,width=.65)
    ax.set_xlim(0,100);ax.set_xlabel('Share of reported rows within each governorate (%)');ax.set_ylabel('')
    ax.legend(title='Original service code',loc='lower right');ax.grid(axis='y',visible=False)
    save('land_2024_service_codes',fig,'RN13A/RN13C meanings unverified: these are raw code distributions, not sales/mortgage classifications.')
    fig,axes=plt.subplots(1,3,figsize=(13,5))
    for ax,period in zip(axes,['2022-11','2022-12','2024-10']):
        subset=tables['buyer_type_counts'].query('period_id == @period').sort_values('buyer_type',ascending=False)
        bars(ax,subset,'buyer_type');ax.set_title(period,fontweight='bold')
    save('land_buyer_types',fig,'Individual/Company as supplied; not investor identities. Each panel uses its own source file.')
    fig,axes=plt.subplots(1,3,figsize=(13,6))
    for ax,period in zip(axes,['2022-11','2022-12','2024-10']):
        subset=tables['ownership_counts'].query('period_id == @period').sort_values('ownership_band')
        bars(ax,subset,'ownership_band');ax.set_title(period,fontweight='bold')
    save('land_ownership_bands',fig,'Bands derived from positive integer NO_OF_OWNERS. Five or more owners grouped; owners are not transactions.')
    monthly=tables['brokerage_monthly_counts'].sort_values('period_id')
    fig,ax=plt.subplots(figsize=(11,5.5));counts=monthly.reported_record_count
    ax.bar(monthly.period_id,counts,color=[TEAL if v==counts.max() else NAVY for v in counts],width=.68)
    for i,value in enumerate(counts):ax.text(i,value+22,f'{value:,}',ha='center',fontsize=10)
    ax.set_ylim(0,counts.max()*1.2);ax.set_xlabel('Supplied month (2025)');ax.set_ylabel('Reported brokerage registrations')
    ax.xaxis.grid(False);ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'));sns.despine(ax=ax)
    save('muscat_monthly',fig,'Muscat-only brokerage registration scope; Jan–Sep observations do not establish a full-year or national trend.')
    fig,ax=plt.subplots(figsize=(10,6));bars(ax,tables['brokerage_wilayat_counts'],'wilayat_ar',rtl=True)
    save('muscat_wilayats',fig,'Six observed Muscat wilayats; original Arabic labels. No national market-activity inference.')
    fig,axes=plt.subplots(1,2,figsize=(14,9))
    bars(axes[0],tables['brokerage_property_use'],'property_use_ar',rtl=True)
    bars(axes[1],tables['brokerage_property_description'],'property_description_ar',rtl=True)
    axes[0].set_title('Land / property-use labels',fontweight='bold');axes[1].set_title('Property descriptions',fontweight='bold')
    save('muscat_property_categories',fig,'Distinct source classification fields; categories reproduced literally, without price or land-stock inference.')
    counts=tables['brokerage_wilayat_monthly_counts'].pivot(index='wilayat_ar',columns='period_id',values='reported_record_count')
    fig,ax=plt.subplots(figsize=(12,6));sns.heatmap(counts,annot=True,fmt='g',cmap=sns.light_palette(TEAL,as_cmap=True),
        linewidths=1,linecolor='white',ax=ax,yticklabels=[arabic(v) for v in counts.index],cbar_kws={'label':'Reported rows'})
    ax.set_xlabel('Supplied month (2025)');ax.set_ylabel('Observed Muscat wilayat')
    save('muscat_wilayat_monthly',fig,'Counts are within one brokerage scope. No missing periods or other governorates added.')
    return names
