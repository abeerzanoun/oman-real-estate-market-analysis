# Six-page report specification

This is a build specification, not a rendered/validated Power BI report. All fields below exist in [SCHEMA.md](SCHEMA.md); measures are in [EDA_MEASURES.dax](EDA_MEASURES.dax). Use the relationship model and explicit SUM-weight measures from this package only.

## Shared design and interactions

Use a 1280 × 720 landscape canvas, 24 px margins, a 64 px header, 48 px footer, and a two-column content grid. Reserve the top row for page title, observed window and navigation. Use `report_theme.json`: navy text, teal observations, amber unresolved/missing data, gray outside scope. Use Segoe UI, 18–22 pt headings, 11–13 pt table labels, readable Arabic labels and tooltips. Test text direction and avoid clipping long source labels. Use horizontal bars rather than pie charts for categories. Titles must say “reported occurrences” or “brokerage registrations”; never simply “sales” or “transactions” without the definition caveat.

Add six native page-navigation buttons, a methodology link, a local reset bookmark per page, and tooltips explaining source occurrences, coverage and retained repeats. Disable slicer synchronization across pages. Shared dimensions can filter all three facts, but that is not evidence that the populations are comparable. No grand-total card, mixed-population bar stack, inferred price map, continuous 2020–2026 line, annual growth or monetary visual is allowed. Native charts require no new geographic data. All report data comes from the 16 imported tables.

For every chart use explicit measures, not implicit Count/Sum of physical rows. Keep “Show items with no data” off on observed-activity charts and leave measure blanks blank. Use categorical month axes sorted by `period_id`, not continuous date axes or interpolation. Where a top-ten is used, disclose that shares still use the full applicable cohort. Default filters below must be captured in each reset bookmark. Chart selection interactions should **filter**, not ambiguously highlight; exceptions are specified for unrelated panels/metadata.

Persistent footer: **“Uploaded source occurrences; unique transactions unverified. Partial periods; exact source URLs/licences pending. No verified monetary analysis.”** Add page-specific caveats below.

## 1. Executive Overview

**Purpose:** summarize the three available populations separately. **Default:** no page filters or slicers; disable incoming synced slicers. There is no combined count KPI.

| Position | Visual / exact binding | Label / behavior |
|---|---|---|
| Top content row, three equal cards | `[Land 2022 Reported Records]`, `[Land Oct 2024 Reported Records]`, `[Muscat Brokerage Registrations]` | Separate cards: “Land BuySell · Nov–Dec 2022”, “Land service-coded · Oct 2024”, “Muscat brokerage · Jan–Sep 2025”; defaults 13,168 / 6,024 / 9,366 |
| Middle left | Table from `dataset_summary`: dataset_id, first_record_date, last_record_date, observed_months, observed_governorates, observed_wilayat_labels | No field summarization, no totals; four files, no date extrapolation |
| Middle right | Separate small cards: `[Land 2022 Supplied Governorates]`, `[Land Oct 2024 Supplied Governorates]`, `[Muscat Brokerage Supplied Months]` | “11 represented governorates”, “11 represented governorates”, “9 supplied brokerage months”. These are different metrics, not comparable completeness scores |
| Bottom content | Three labelled text callouts and buttons to Land, Brokerage and Coverage pages | Explicitly state different service definitions, Muscat-only scope and missing research years |

Do not cross-filter the metadata table from cards. Do not put fixed Nov/Dec change measures here. Optional bilingual card subtitles: “Reported occurrences / تكرارات السجلات”; “Governorate / المحافظة”; “Wilayat / الولاية”.

**Acceptance:** three cards reconcile separately; metadata has four rows; no global period slicer that blanks unrelated cards; target period 2020–2026 is labelled research scope rather than observed coverage.

## 2. Geographic Coverage

**Purpose:** show supplied vs unavailable month/governorate cells. All visuals use **disconnected coverage metadata**, not fact measures. **Default:** `coverage_matrix_2020_2026[scope_id]` single-select `land_buy_sell_2022`; same table `[year]` single-select 2022. Use only these metadata slicers on this page; dim_period/dim_governorate slicers have no effect here.

| Position | Visual / exact binding | Label / behavior |
|---|---|---|
| Left filter rail | coverage_matrix_2020_2026.scope_id, year | Single-select each, require one scope/year; no unsupported all-population total |
| Main area | Matrix: rows `governorate_id`; columns `month`; values `availability_status` with **First** text aggregation | Each scope/year/governorate/month has exactly one cell; use all 12 numeric months, no count aggregation. Governorate IDs are technical English labels; the Methodology page provides the bilingual lookup |
| Tooltip / optional second matrix | Same row/column context, `reported_record_count` using **First**, not sum | Null cells stay blank. These are explanatory metadata counts, not a second fact or market-total KPI |
| Bottom | Static legend: observed / not_provided / outside_source_scope / future_period | Conditional formatting rules on First availability_status: teal / amber / gray / pale blue. Show text as well as color |

Use native text-value matrix aggregation. If a Desktop version cannot conditionally format text, retain the status text and legend rather than substituting fabricated numerical scores. Do not replace blanks with “0”. Display “Coverage snapshot: 2026-10-13; presence does not certify complete reporting.”

**Acceptance:** land Nov/Dec 2022 and Oct 2024 have 11 observed governorate cells per month. Brokerage Jan–Sep 2025 has only Muscat observed and ten governorates outside scope per month. Changing year to 2023 reveals no observed cells. No map/coordinate data is invented. The full imported metadata has 42 observed / 1,844 not_provided / 840 outside_source_scope / 46 future cells; these are **not market coverage percentages**.

## 3. Land Transactions

**Purpose:** within-population geographic and attribute distributions, keeping 2022 and 2024 separate. Use two clearly bordered panels, not a common trend chart. Shared slicers: `dim_governorate[governorate_en]`, `dim_wilayat[wilayat_ar]`, `dim_buyer_type[buyer_type]`, `dim_ownership_band[ownership_band]`; default All. There is **no common period or dataset slicer**. No page-level dataset filter, because the panels intentionally use different facts.

Every **2022** chart uses visual filter `dim_dataset[scope_id] = land_buy_sell_2022`; every **2024** chart uses `dim_dataset[scope_id] = land_service_coded_2024`. Shared slicers retain their dimension context. Hide incompatible empty combinations; a selected wilayat under a different governorate must produce blank, not silently reset the governorate or invent coverage. Since dimensions do not filter each other, slicer lists may include irrelevant members: do not introduce bidirectional relationships to hide them.

| Panel | Visual / exact binding | Definition and interaction |
|---|---|---|
| 2022 top | Two cards `[Land 2022 November Rows]`, `[Land 2022 December Rows]` | Label 2022 explicitly; filters on dataset/period are deliberately cleared by these measures; shared geography/buyer/owner filters remain |
| 2022 main | Clustered horizontal bars: axis `dim_governorate[governorate_en]`, legend `dim_period[period_label]`, value `[Land 2022 Reported Records]`; visual period filter Nov/Dec 2022 | Show same-scale side-by-side counts, sorted by total source occurrences; 11 governorates unfiltered. Tooltip `[Land 2022 Geographic Share]` |
| 2022 detail | Ranked bar: `dim_wilayat[wilayat_ar]` vs `[Land 2022 Reported Records]`, top 10; tooltip `dim_wilayat[wilayat_key]` where supported | Preserve nonstandard labels by default; any optional visual exclusion of `fact_land_2022[nonstandard_wilayat_label] = false` must be labelled as an exclusion and must not affect total cards |
| 2022 lower | Matrix: rows `dim_buyer_type[buyer_type]`, columns `dim_ownership_band[ownership_band]`, value `[Land 2022 Reported Records]` | Source buyer/ownership distribution, not number of owners summed |
| 2022 optional comparison tooltip/table | `[Land 2022 Nov Dec Row Difference]`, `[Land 2022 Nov Dec Row Change]` | Caption “Change between uploaded file counts; monthly completeness unverified”. Not annual growth or a market-price conclusion |
| 2024 top | Card `[Land Oct 2024 Reported Records]` | Caption “Oct 2024 service-coded occurrences” |
| 2024 main | Horizontal bars: `dim_governorate[governorate_en]` vs `[Land Oct 2024 Reported Records]`; tooltip `[Land Oct 2024 Geographic Share]` | One supplied month only; no growth comparison with 2022 |
| 2024 detail | Bar `dim_service_code[service_sub_id]` vs `[Land Oct 2024 Reported Records]` | Show RN13A/RN13C unchanged; definition_status tooltip says meaning_unverified |
| 2024 lower | Matrix: `dim_wilayat[wilayat_ar]` rows, `dim_buyer_type[buyer_type]` columns, `[Land Oct 2024 Reported Records]` values; optional `fact_land_2024[ownership_mode]` legend in a separate bar | ownership_mode is a fact attribute for this visual only, not a shared slicer |

Edit interactions: selections within either panel filter that panel only; set **None** for all visuals in the other panel, especially service-code and period selections. Shared geographic/buyer/owner slicers filter both panels by design. No panel title or legend should suggest service-code equivalence to BuySell. Use a smaller detail font or native visual scroll if needed; never compress Arabic into unreadable tiny bars.

**Acceptance:** default Nov 7,501 / Dec 5,667 / Oct 6,024. October service counts RN13A 599 / RN13C 5,425. Choosing Muscat gives Nov 960 / Dec 734 / Oct 1,099. No monetary or national-growth visual. All optional exclusions are disclosed and raw totals remain preserved.

## 4. Muscat Brokerage

**Purpose:** registration/property-mix analysis within the brokerage file. **Page filters:** `dim_dataset[scope_id] = muscat_brokerage_registration_2025` and `dim_governorate[governorate_id] = muscat`, locked. Slicers: `dim_period[period_label]` restricted to Jan–Sep 2025, `dim_wilayat[wilayat_ar]` restricted to the six Muscat keys, `dim_property_use[property_use_ar]`, `dim_property_description[property_description_ar]`; default all supplied values. No buyer/service/owner slicers.

| Position | Visual / exact binding | Label / behavior |
|---|---|---|
| Top | Cards `[Muscat Brokerage Registrations]`, `[Muscat Brokerage Supplied Months]` | Default 9,366 / 9; “registrations” means retained reported source occurrences |
| Main left | Columns `dim_period[period_label]` vs `[Muscat Brokerage Registrations]` | Categorical Jan–Sep axis; no Oct–Dec zero placeholders, interpolation, YTD/YoY or annualization |
| Main right | Horizontal bars `dim_wilayat[wilayat_ar]` vs `[Muscat Brokerage Registrations]` | Six observed wilayats; tooltip `[Muscat Brokerage Geographic Share]` |
| Bottom left | Bar `dim_property_use[property_use_ar]` vs `[Muscat Brokerage Registrations]` | Eight observed uses unfiltered; tooltip `[Brokerage Property Use Share]` within current wilayat/month/description cohort |
| Bottom right | Bar `dim_property_description[property_description_ar]` vs `[Muscat Brokerage Registrations]`, native scroll if needed | Thirteen observed descriptions; preserve source spellings; no money implied by property category |

Source-category caption: `تسجيل عقد بيع من خلال مكاتب الوساطة العقارية`. Optional wilayat × month matrix uses the same explicit brokerage measure, not physical aggregate row counts. Native selection filters other brokerage charts; blank intersections remain blank.

**Acceptance:** default monthly counts 857, 1,147, 819, 880, 1,207, 816, 1,277, 1,141, 1,222 sum to 9,366. No non-Muscat records or full-year claim. Full-source repeated membership share (if used in a tooltip) is not a confirmed duplicate rate.

## 5. Data Quality

**Purpose:** transparent audit evidence, without presenting unavailable quantities as zeros. The metadata tables are disconnected. Use separate native tables showing all four datasets by default; no shared dimension slicer and no automatic relationships. If adding a dataset filter, make it **table-specific** using that table's dataset_id and label its scope. Do not imply a slicer on one disconnected table filters another.

| Position | Visual / exact binding | Label / behavior |
|---|---|---|
| Top | Text “All source occurrences retained; confirmed duplicate ingestion removals: 0. Unique economic event count: unknown.” | Backed by completed duplicate audit; do not say “0 duplicate transactions” |
| Main left | Table `data_quality_summary`: dataset_id, reported_record_count, records_in_repeated_groups, repeated_occurrences_after_first, repeated_group_share_pct, rows_removed | Do not summarize; disable totals. Shares already 0–100. Membership includes first group occurrence, not a removal recommendation |
| Main right | Table `data_quality_summary`: dataset_id, reported_amount_present_records, reported_amount_missing_records, monetary_unit_verified | October 2024 has 5,657 / 367 / false; the other amount counts are blank. No financial sum or OMR label |
| Bottom left | Table `source_column_quality`: dataset_id, column, missing, observed_types | No totals; optional per-table dataset_id slicer. Field names/types only, no demographic record values |
| Bottom right | Table `dataset_summary`: dataset_id, nonstandard_wilayat_rows, observed_wilayat_labels | Show retained nonstandard locations and explain 2022 source labels |

Do not add a generic “data quality score” or repeat-count percentage across different populations. Selection interactions between disconnected tables are None; place corresponding source IDs visibly in every table.

**Acceptance:** zero rows_removed for each source; full-source repeated membership 3,675 Nov / 2,600 Dec / 0 Oct / 8,174 brokerage. Two nonstandard wilayat occurrences remain in the 2022 totals. Projection-level visible repeats are not conflated with full-source repeat membership.

## 6. Methodology

**Purpose:** make provenance, scope, transformations and pending verification accessible within the report. No activity slicers or financial KPIs.

| Position | Visual / exact binding | Content |
|---|---|---|
| Top / main left | Native table from `dim_dataset`: dataset_id, file, sheet, min_date, max_date, provider, provider_evidence, source_verification_status | Four source files and evidence classification; no count total |
| Main right | Second table `dim_dataset`: dataset_id, official_download_url, official_landing_url, licence, licence_url, currency_unit | Preserve blanks, caption “Not yet independently verified”; do not substitute provider entry points as exact dataset URLs |
| Bottom left | Text / process diagram | Original XLSX unchanged → in-memory dimension recovery → reviewed location normalization → retained-occurrence duplicate audit → observed aggregate facts → explicit SUM-weight measures. Cite exact pinned paths and full manifests from BUILD_INSTRUCTIONS / model contract |
| Bottom right | Table `dim_governorate`: governorate_id, governorate_en, governorate_ar | Bilingual lookup for geographic IDs; no fact relationships added |

Add text links to repository `DATA_PROVENANCE_AUDIT.md`, `reports/DUPLICATE_AUDIT.md`, `docs/data_dictionary.md` and this package. Show discovery leads only if labelled unverified resource leads. State: “2020–2026 research target; uploaded snapshots only. Desktop acceptance status must be recorded separately.” Do not use static text that says PBIX validated before completing the checklist.

**Acceptance:** unresolved URL/licence fields remain visibly unresolved; brokerage embedded attribution distinguished from three user-attributed land files; no privacy fields or unverified prices; lineage, interpretation and refresh instructions reachable from every page.
