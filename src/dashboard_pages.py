"""Responsive views of the three explicitly separated analytical cohorts."""
import streamlit as st

from src.dashboard_charts import coverage_heatmap, period_bar, ranked_bar
from src.dashboard_data import COUNT, FAMILIES, SCOPES, export_csv, family_frame, filter_frame, summarize
from src.source_attribution import load_source_attribution

PAGES = {
    "Executive Overview": "Executive Overview | نظرة عامة",
    "Land Market Analysis": "Land Market Analysis | معاملات الأراضي",
    "Muscat Brokerage Analysis": "Muscat Brokerage Analysis | الوساطة في مسقط",
    "Governorate and Wilayat Comparisons": "Geographic Comparisons | المحافظات والولايات",
    "Data Coverage and Quality": "Coverage & Quality | التغطية والجودة",
    "Sources and Methodology": "Sources & Methodology | المصادر والمنهجية",
}
NOTES = {
    "land_2022": "BuySell worksheets · November and December 2022 only. Both supplied months share the source schema. No property-use or monetary fields are available.",
    "land_2024": "October 2024 snapshot · RN13A and RN13C are source service codes with unverified meanings. This definition differs from the 2022 BuySell files; no cross-year market-growth inference is supported.",
    "brokerage_2025": "Muscat only · January–September 2025 sale-contract registrations through brokerage offices. This is a partial year and a separate administrative population from the land files.",
}


def style():
    st.html("""<style>
      .stMainBlockContainer {max-width:1440px; padding-top:2rem; padding-bottom:2rem;}
      .oman-hero {background:linear-gradient(115deg,#153348,#175664);color:white;
        padding:1.7rem 2rem;border-radius:18px;margin-bottom:1.3rem;}
      .oman-hero h1 {color:white;font-size:clamp(1.6rem,3vw,2.4rem);padding:0;line-height:1.25;}
      .oman-hero p {color:#DCF1F2;margin-bottom:0;max-width:65ch;}
      .oman-kicker {font-size:.78rem;letter-spacing:.14em;color:#A3DADD;margin-bottom:.7rem;}
      [data-testid="stMetric"] {background:white;border:1px solid #E0EAEE;
        border-top:3px solid #087F8C;border-radius:12px;padding:1rem;}
      [data-testid="stMetricValue"] {font-variant-numeric:tabular-nums;}
      [data-testid="stPlotlyChart"] {background:white;border-radius:12px;padding:.4rem;}
      [data-testid="stSidebar"] {border-right:1px solid #DCE7EB;}
      button {min-height:44px;}
      @media(max-width:900px) {
        .stMainBlockContainer {padding:1rem;}
        .oman-hero {padding:1.2rem;}
        [data-testid="stHorizontalBlock"] {flex-wrap:wrap;}
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
          min-width:min(100%,280px);flex:1 1 280px;}
      }
    </style>""")


def heading(title, arabic, text):
    st.html(f'<section class="oman-hero"><div class="oman-kicker">OMAN REAL ESTATE / عُمان</div>'
            f'<h1>{title}</h1><p dir="auto">{arabic}</p><p>{text}</p></section>')


def plot(fig):
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False, "scrollZoom": False},
                    theme=None)


def governorate_label(frame, value):
    row = frame.loc[frame.governorate_id.eq(value)].iloc[0]
    return f"{row.governorate_en} | {row.governorate_ar}"


def filtered(bundle, family, prefix, single_period=False):
    source = family_frame(bundle, family)
    periods = sorted(source.period_id.unique())
    with st.expander("Filters | تصفية البيانات", expanded=False):
        left, right = st.columns(2)
        with left:
            if single_period:
                selected = [st.selectbox("Reporting month | شهر التقرير", periods, key=prefix+"period")]
            else:
                selected = st.multiselect("Supplied reporting months | الأشهر المتاحة", periods,
                                           default=periods, key=prefix+"periods")
        with right:
            govs = sorted(source.governorate_id.unique())
            selected_govs = st.multiselect("Governorates | المحافظات", govs, default=govs,
                format_func=lambda v: governorate_label(source, v), key=prefix+"govs")
        geography = filter_frame(source, {"period_id": selected, "governorate_id": selected_govs})
        wilayats = sorted(geography.wilayat_key.unique())
        # Prune old choices when a parent filter changes; new cohort gets its own keys.
        wkey = prefix + "wilayats"
        if wkey in st.session_state:
            st.session_state[wkey] = [v for v in st.session_state[wkey] if v in wilayats]
        chosen_w = st.multiselect("Wilayats | الولايات (optional restriction)", wilayats,
            format_func=lambda v: f"{source.loc[source.wilayat_key.eq(v), 'wilayat_ar'].iloc[0]} · "
                                  f"{governorate_label(source, source.loc[source.wilayat_key.eq(v), 'governorate_id'].iloc[0]).split(' | ')[0]}",
            key=wkey, help="Leave empty to include all wilayat labels in the selected governorates.")
        filters = {"period_id": selected, "governorate_id": selected_govs}
        if chosen_w:
            filters["wilayat_key"] = chosen_w
        fields = [("property_use_key", "Land use | نوع الاستعمال"),
                  ("property_description_key", "Property description | وصف العقار")] if family == "brokerage_2025" else [
                  ("buyer_type", "Buyer type | نوع المشتري"), ("ownership_band", "Owner-count band | عدد الملاك")]
        if family == "land_2024":
            fields += [("service_sub_id", "Service code (meaning unverified)"), ("ownership_mode", "Ownership mode")]
        for field, label in fields:
            options = sorted(source[field].unique())
            if field.endswith("_key"):
                lookup = dict(zip(source[field], source[field.removesuffix("_key")+"_ar"]))
                selected_values = st.multiselect(label, options, default=options,
                                                 format_func=lookup.get, key=prefix+field)
            else:
                selected_values = st.multiselect(label, options, default=options, key=prefix+field)
            filters[field] = selected_values
    result = filter_frame(source, filters)
    st.caption("Applied months: " + (", ".join(selected) or "none selected") + " · " + FAMILIES[family])
    st.caption(NOTES[family])
    if result.empty:
        st.info("No supplied records match these filters. Select a month, governorate and attribute values to continue.")
    return result


def metrics(frame):
    cols = st.columns(3)
    cols[0].metric("Source record occurrences | سجلات المصدر", f"{int(frame[COUNT].sum()):,}")
    cols[1].metric("Governorates in selection | المحافظات", frame.governorate_id.nunique())
    cols[2].metric("Observed wilayat labels | مسميات الولايات", frame.wilayat_key.nunique())
    st.caption("Counts are source occurrences, not verified unique transactions. All repeated attributes remain included.")


def geography_charts(frame):
    governors = summarize(frame, ["governorate_id", "governorate_en", "governorate_ar"])
    governors["label"] = governors.governorate_en + " | " + governors.governorate_ar
    plot(ranked_bar(governors, "label", "Governorate distribution | توزيع المحافظات"))
    wilayats = summarize(frame, ["wilayat_key", "wilayat_ar", "governorate_en", "nonstandard_wilayat_label"])
    wilayats["label"] = wilayats.wilayat_ar + " · " + wilayats.governorate_en
    plot(ranked_bar(wilayats, "label", "Leading observed wilayat labels | الولايات", top=15))
    st.caption("Top 15 labels shown; chart percentages use all filtered occurrences, including labels beyond the top 15. "
               "Observed labels are not a complete administrative inventory.")
    unusual = int(frame.loc[frame.nonstandard_wilayat_label, COUNT].sum())
    if unusual:
        st.warning(f"{unusual:,} occurrences use the nonstandard source label الساحل الشرقي. They remain in all totals and tables.")


def download(frame, family, key):
    with st.expander("Selected aggregate table & download | الجدول والتنزيل"):
        st.dataframe(frame, hide_index=True, width="stretch")
        st.download_button("Download selected CSV | تنزيل CSV", export_csv(frame, family),
                           file_name=f"oman_{family}_filtered_aggregates.csv", mime="text/csv", key=key)
        st.caption("UTF-8 with BOM for Excel/Power BI. Sum reported_record_count; CSV row count is not the occurrence count. "
                   "records_in_repeated_groups refers to full-source equality in the original cohort, not a duplicate-removal decision.")


def executive(bundle):
    heading("Real estate, with evidence", "نظرة عامة على البيانات العقارية", "Explore the supplied records, understand their definitions, and see exactly where coverage ends.")
    cols = st.columns(3)
    for col, family in zip(cols, FAMILIES):
        frame = family_frame(bundle, family)
        with col:
            st.metric(FAMILIES[family], f"{int(frame[COUNT].sum()):,}")
            st.caption(NOTES[family])
    st.info("These cards describe separate administrative cohorts. Their sum is not a national market total. "
            "Transaction identity is unresolved; no verified unique-transaction KPI or monetary KPI is available.")
    st.subheader("A geographic snapshot | لقطة جغرافية")
    family = st.selectbox("Choose one comparable cohort", list(FAMILIES), format_func=FAMILIES.get, key="overview_family")
    frame = filtered(bundle, family, "overview_"+family+"_", single_period=True)
    if not frame.empty:
        metrics(frame)
        governor = summarize(frame, ["governorate_en", "governorate_ar"])
        governor["label"] = governor.governorate_en + " | " + governor.governorate_ar
        plot(ranked_bar(governor, "label", "Supplied occurrences by governorate"))
        leader = governor.iloc[0]
        st.markdown(f"**Within this filtered snapshot**, {leader.governorate_en} has the most supplied occurrences "
                    f"({int(leader[COUNT]):,}; {leader.share_of_selection_pct:.1f}% of this selection). "
                    "This describes the uploaded population, not prices, investment returns or national demand.")


def land(bundle):
    heading("Land market records", "معاملات الأراضي", "Inspect a comparable cohort before comparing locations or attributes.")
    family = st.selectbox("Land dataset definition", ["land_2022", "land_2024"], format_func=FAMILIES.get, key="land_family")
    frame = filtered(bundle, family, "land_"+family+"_")
    if frame.empty:
        return
    metrics(frame)
    period = summarize(frame, ["period_id"])
    plot(period_bar(period, "Supplied land reporting months · no annual extrapolation"))
    st.caption("Multiple selected months are pooled only within this cohort. Geographic and category shares refer to the entire filtered selection.")
    geography_charts(frame)
    left, right = st.columns(2)
    with left:
        plot(ranked_bar(summarize(frame, ["buyer_type"]), "buyer_type", "Buyer type | نوع المشتري"))
    with right:
        plot(ranked_bar(summarize(frame, ["ownership_band"]), "ownership_band", "Owner-count bands | عدد الملاك"))
    if family == "land_2024":
        st.warning("RN13A/RN13C meanings and RE_VALUE units are unverified. Codes are shown literally; financial values are excluded.")
        plot(ranked_bar(summarize(frame, ["service_sub_id"]), "service_sub_id", "Source service codes · definitions pending"))
    download(frame, family, "download_land")


def brokerage(bundle):
    heading("Muscat brokerage registrations", "تسجيلات الوساطة العقارية في مسقط", "Sale-contract registrations through brokerage offices, January–September 2025 only.")
    family = "brokerage_2025"
    frame = filtered(bundle, family, "broker_")
    if frame.empty:
        return
    metrics(frame)
    st.info("Verified transaction label: تسجيل عقد بيع من خلال مكاتب الوساطة العقارية. "
            "Property descriptions and land use are recorded attributes; counts are not prices or verified unique sales.")
    plot(period_bar(summarize(frame, ["period_id"]), "2025 supplied months · partial-year registrations"))
    plot(ranked_bar(summarize(frame, ["wilayat_ar"]), "wilayat_ar", "Muscat wilayat distribution | ولايات مسقط"))
    plot(ranked_bar(summarize(frame, ["property_use_ar"]), "property_use_ar", "Land use | نوع الاستعمال"))
    plot(ranked_bar(summarize(frame, ["property_description_ar"]), "property_description_ar", "Property description | وصف العقار"))
    download(frame, family, "download_broker")


def comparisons(bundle):
    heading("Compare places within a period", "مقارنة المحافظات والولايات", "One dataset definition and one supplied month at a time; every ranking states its cohort.")
    family = st.selectbox("Comparable cohort", list(FAMILIES), format_func=FAMILIES.get, key="compare_family")
    frame = filtered(bundle, family, "compare_"+family+"_", single_period=True)
    if frame.empty:
        return
    metrics(frame)
    geography_charts(frame)
    st.subheader("Full geographic comparison table")
    table = summarize(frame, ["governorate_en", "governorate_ar", "wilayat_ar", "nonstandard_wilayat_label"])
    st.dataframe(table, hide_index=True, width="stretch")
    download(frame, family, "download_compare")


def quality(bundle):
    heading("Coverage is part of the result", "التغطية وجودة البيانات", "Missing source periods remain missing. Repeated attributes remain records pending reliable identity evidence.")
    tables = bundle["tables"]
    family = st.selectbox("Coverage population", list(FAMILIES), format_func=FAMILIES.get, key="coverage_family")
    year = st.selectbox("Coverage year (metadata only)", list(range(2020, 2027)), index=5, key="coverage_year")
    matrix = tables["coverage_matrix_2020_2026"]
    matrix = matrix[matrix.scope_id.eq(SCOPES[family])]
    plot(coverage_heatmap(matrix, tables["dim_governorate"], year))
    st.caption("Teal: supplied · Sand: not supplied · Grey: outside source scope · Lavender: after the audit reporting cutoff. "
               "Coverage metadata is fixed to the 2026-10-13 audit; these cells are not additional market observations.")
    st.caption(NOTES[family])
    cols = st.columns(3)
    cols[0].metric("Confirmed duplicate imports", bundle["duplicates"]["confirmed_duplicate_ingestion_occurrences"])
    cols[1].metric("Source occurrences removed", bundle["duplicates"]["rows_removed"])
    cols[2].metric("Unique transaction identity", "Unverified")
    st.subheader("Record repetition audit | تدقيق تكرار السجلات")
    st.warning("Identical source attributes do not confirm duplicate economic transactions. "
               "No reliable official transaction/record ID is present. Dropping private fields can make distinct source rows look identical.")
    columns = ["dataset_id", "source_rows", "raw_repeated_groups", "raw_repeat_occurrences_after_first",
               "raw_occurrences_in_repeated_groups", "projection_collision_occurrences", "rows_removed"]
    st.dataframe(tables["duplicate_summary"][columns], hide_index=True, width="stretch")
    st.caption("Raw repetition uses every original data column, including fields withheld from analytical exports. "
               "Projection collisions count occurrences in exported attribute groups that contain different full-source patterns. "
               "Neither criterion proves duplicate transactions. Zero raw repetitions in 2024 does not prove transaction uniqueness.")
    st.subheader("Actual source date ranges and coverage")
    st.dataframe(tables["dataset_summary"], hide_index=True, width="stretch")
    with st.expander("Missing values in original source columns"):
        st.dataframe(tables["source_column_quality"], hide_index=True, width="stretch")
    with st.expander("Coverage metadata table (blank counts mean unavailable)"):
        st.dataframe(matrix[matrix.year.eq(year)], hide_index=True, width="stretch")
    st.markdown("**Other limits:** three land worksheets have incorrect declared dimensions, recovered read-only; "
                "legacy Sharqiyah labels are resolved through the documented wilayat crosswalk; two nonstandard "
                "wilayat occurrences are retained. Brokerage publication metadata precedes its last recorded date. "
                "No continuous 2020–2026, monetary or investment-return conclusion is supported.")


def sources(bundle):
    heading("Every chart has a lineage", "المصادر والمنهجية", "Original uploaded workbooks → validated records → reviewed aggregate facts → read-only interactive views.")
    st.markdown("**Method:** verify SHA-256 hashes on every rerun, join dimensions with many-to-one validation, "
                "filter observed facts, and sum `reported_record_count`. Shares use all occurrences in the current filtered "
                "selection. No missing observations, financial values or transaction identities are inferred. "
                "Repeated occurrences are retained, and source populations remain separate.")
    attribution = load_source_attribution(bundle["tables"]["dim_dataset"])
    st.info("The owner confirmed the download portals on 2026-10-18. Portal landing pages are not exact "
            "dataset pages or file downloads; no independent official-file match or redistribution licence is verified. "
            "NCSI was recommended for future research and supplied none of the four analytical workbooks.")
    for row in bundle["tables"]["dim_dataset"].to_dict("records"):
        source = attribution[row['dataset_id']]
        portal_name = ("MOHUP Open Data" if source["download_portal"] ==
                       "MOHUP monthly Buy and Sell datasets portal" else source["download_portal"])
        with st.expander(row["file"].split("/")[-1], expanded=True):
            st.markdown(f"**Original data provider:** {source['original_data_provider']}")
            st.markdown(f"**Download portal:** {portal_name}  \n"
                        f"[{source['portal_landing_url']}]({source['portal_landing_url']})")
            st.markdown("**Verification status:** Download portal confirmed by the project owner; "
                        "exact dataset download URL and redistribution licence not yet independently verified.")
            st.caption("Portal landing page only, not an exact dataset page or file download. "
                       "Owner confirmation: " + source['confirmation_date'] + ".")
            st.write(f"Provider attribution evidence: {source['provider_evidence']}")
            st.write(f"Observed dates: {row['min_date']} → {row['max_date']}")
            st.write(f"Sheet: {row['sheet']} · Header row: {row['header_row']} · Source occurrences: {row['reported_record_count']:,}")
            st.code(row["sha256"], language=None)
            st.write("Exact dataset page, exact download URL, redistribution licence, verified publication date "
                     "and original download date: unverified. Portal confirmation does not verify service definitions or monetary units.")
            st.link_button("User-confirmed portal landing page (not an exact dataset URL)", source["portal_landing_url"])
    st.caption("Current attribution: docs/source_attribution.json. The ingestion registry and processed "
               "dim_dataset are preserved historical audit snapshots; no source rows or calculations are changed.")
    st.markdown("**Interpretation:** location rankings describe recorded activity in the supplied cohort. "
                "They cannot establish property prices, returns, annual growth or market completeness. "
                "The 2022 land and 2024 service-coded definitions are not interchangeable; brokerage is a separate population.")
    st.markdown("**Geography:** bilingual governorate labels come from the reviewed dimensions. Arabic wilayat labels "
                "are retained; no unverified English translations are added. Historical Sharqiyah resolution and nonstandard "
                "labels are documented in the audit. Property-use and description labels come from the brokerage workbook only.")
    repo = "https://github.com/abeerzanoun/oman-real-estate-market-analysis"
    for path, label in [("DATA_PROVENANCE_AUDIT.md", "Provenance audit"),
                        ("docs/source_attribution.json", "Current provider and portal register"),
                        ("docs/data_sources.md", "Source documentation"), ("docs/data_dictionary.md", "Data dictionary"),
                        ("reports/DUPLICATE_AUDIT.md", "Duplicate audit"), ("reports/EDA_INDEX.md", "EDA report"),
                        ("docs/DASHBOARD.md", "Dashboard setup and interpretation")]:
        st.markdown(f"[{label}]({repo}/blob/main/{path})")


def render_page(page, bundle):
    {"Executive Overview": executive, "Land Market Analysis": land,
     "Muscat Brokerage Analysis": brokerage, "Governorate and Wilayat Comparisons": comparisons,
     "Data Coverage and Quality": quality, "Sources and Methodology": sources}[page](bundle)
