# Data dictionary

The four supplied workbooks, audited record schemas and reviewed EDA facts are documented in the later sections of this file. The initial candidate dictionary below is retained as a research proposal: it does not establish the availability of monetary values, price indices or continuous 2020–2026 coverage. The dashboard uses only the actual audited/EDA schemas and the view semantics documented at the end.

Potential observation grain: one source-defined metric for one reporting period, geographic level, property category and transaction scope. Transaction measures and price indices may need separate fact tables when their grains differ. A unique key cannot be finalized yet.

| Proposed field | Proposed type | Meaning / unit | Proposed validation and caveats | Status |
|---|---|---|---|---|
| year | nullable integer | Reporting year | 2020–2026 only where verified; not publication year | Proposed |
| month | nullable integer | Reporting month | 1–12 for monthly observations; null for annual/quarterly records | Proposed |
| governorate | nullable string | Source-defined governorate | Preserve original label; map verified codes; distinguish national totals | Proposed |
| wilayat | nullable string | Source-defined wilayat | Validate hierarchy; null if unavailable or more aggregated | Proposed |
| property_category | nullable string | Source property classification | Preserve definitions; do not infer categories or equate land with all property | Proposed |
| transaction_count | nullable integer | Count of defined transactions | Nonnegative; distinguish sales, mortgages, deeds and other registrations | Proposed |
| transaction_value_omr | nullable decimal | Value in Omani rial | Nonnegative if source definition supports it; retain original scale and convert million OMR explicitly; preserve decimal precision | Proposed |
| property_price_index | nullable decimal | Index points | Retain base year/value; do not store inflation percentages as an index | Proposed |
| data_source | string | Publisher and resource identifier | Traceable to provenance register and original file | Proposed |
| reporting_period | string | Source reporting interval | Explicit start/end and monthly, quarterly, annual or cumulative status | Proposed |
| period_start / period_end | date | Inclusive reporting boundaries | Confirm dates and consistency with frequency | Proposed |
| reporting_frequency | string | Monthly / quarterly / annual | Source-defined; never sum overlapping cumulative records | Proposed |
| transaction_type | nullable string | Sales / mortgages / other source-defined type | Keep scopes separate | Proposed |
| geographic_level | string | National / governorate / wilayat | Prevent totals being added to component geographies | Proposed |
| index_base_period | nullable string | Official index reference period | Required for interpreting/comparing index series | Proposed |
| source_url / source_file | string | Exact resource and local original | Capture during acquisition | Proposed |
| retrieved_at / published_at | timestamp / nullable date | Provenance dates | Retrieval uses explicit timezone; publication differs from reporting period | Proposed |
| is_provisional | nullable boolean | Source provisional/revised status | Unknown is distinct from false | Proposed |

## Cross-tool conventions to confirm

Use UTF-8 and stable snake_case names for future CSV exports; preserve Arabic labels and reviewed English mappings. Use ISO dates, explicit OMR units and documented decimals for Excel/Power BI. Export nulls consistently and avoid mixing missing observations with zero. Power BI relationships require verified date/geography/category keys; no dashboard or model is created in this phase.

Changes to coverage, definitions, units and index bases must be recorded before aggregations or comparisons. An average transaction value is not a property price index and is sensitive to transaction mix.

## Phase 2: verified source semantics and processing contract (2026-10-12)

The preliminary wide fields above remain proposed. Online inspection verified NCSI national tables, but no original has been acquired. The following long-format schema is implemented as a **processing contract**, not yet a published dataset:

| Field | Type | Contract |
|---|---|---|
| indicator | string | `sales_value_omr`, `mortgage_value_omr`, `barter_value_omr`, or corresponding `*_contract_count`; six separate metrics |
| value | decimal text | Exact decimal conversion; source million OMR multiplied by 1,000,000, counts unchanged; no floating-point rounding |
| unit | string | `OMR` or `count`; nonnegative finite observations, counts integral |
| period_start / period_end | ISO date | Explicit interval from the reviewed source column; includes annual, monthly and year-to-date intervals |
| frequency | enum | `annual`, `monthly`, `year_to_date`; cumulative records must not be added to monthly records |
| geographic_level | string | `national` for these profiles |
| governorate / wilayat | nullable string | Blank because the transaction tables lack this breakdown; never guessed |
| property_category | string | `not_disaggregated`, because no category split is available in the activity table |
| source_id / source_url | string | Exact catalogue identifier and official URL |
| source_page | integer | 1-based PDF page locator |
| raw_sha256 | string | SHA-256 of the actual downloaded original; mandatory for processed rows |

The combined observation key is indicator + period_start + period_end + frequency. The processor rejects duplicate observation keys across releases rather than silently choose a revision. No processed rows are currently present.

Verified online but **not implemented in processing**: total traded property value, fees, issued title deeds/GCC title deeds, index categories, index weights and residential-land indices by governorate. Publication dates, exact index revision policy (2026 indices are marked provisional and historical comparison values differ by release), and record-level MOHUP property types/wilayats remain unresolved. Price indices will require a separate fact table including category, geography, base period and weight/revision metadata. Nulls and source blanks remain distinct from zero.


## Manual XLSX/CSV output contract

This schema is implemented but **no official files are imported**. Every production value must come from an original input cell.

| Field | Meaning |
|---|---|
| observation_id | SHA-256 of the semantic observation key, project-generated identifier |
| scope_id / indicator | Reviewer-declared comparable dataset definition and metric; never inferred from values |
| value / unit | Exact decimal text and canonical count, OMR or index_points; no imputation |
| period_start / period_end / frequency | Explicit ISO interval and monthly/quarterly/annual/year_to_date status |
| geographic_level | National, governorate or wilayat; not silently aggregated |
| governorate_id / governorate / governorate_ar | Internal project slug and canonical English/Arabic label for the 11 governorates; slugs are not official statistical codes |
| wilayat | Source label preserved; hierarchy not automatically certified |
| property_category / transaction_type | Source labels or documented table constants; unavailable dimensions remain blank |
| index_base_period | Official source base period for index metrics; mandatory for indices |

`provenance.csv` joins on observation_id and preserves dataset_id, original filename, SHA-256, sheet/row/column coordinates, publisher, title, source URL, publication/retrieval dates, review status, licence attribution and the original unit/multiplier. Multiple source cells may support one deduplicated observation. `coverage.csv` lists present/missing governorate slugs for each comparable group; no missing observations are generated. `validation_report.json` includes missing values, excluded totals, errors, counts and readiness flags.

Business key: scope_id + indicator + unit + interval + frequency + geographic level + governorate + wilayat + category + transaction type + index base. Equal duplicates retain all provenance; conflicting values fail review. For raw row-level transactions, a dedicated ID/grain adapter is required. Readiness means valid actual imports and complete governorate aggregate groups with no missing metric cells; it does not imply complete 2020–2026 coverage, external authentication or certified Power BI measures.


## Actual uploaded-record schema

The proposed variables above remain candidate indicators. The four actual XLSX uploads now have a separate [source-backed row dictionary](uploaded_data_dictionary.md). No transaction_count, OMR amount, property price index or area is inferred from these records. Owner counts, record occurrences and unverified RE_VALUE have distinct definitions.


The executed EDA adds a separate [analytical dictionary](eda_data_dictionary.md) for actual grouped counts, observed periods, ownership bands, shares and comparison variables. No proposed prices or indices are filled.

## Dashboard view semantics

The Streamlit dashboard reads the existing pinned EDA facts and dimensions;
it does not create replacement processed datasets. Its counts sum
`reported_record_count`, which means **source record occurrences**, not verified
unique transactions. `share_of_selection_pct` is calculated after filtering as
100 × grouped occurrences / all filtered occurrences. No unobserved categories
or periods are added to count tables.

Selected CSV downloads retain aggregate fields and add `scope_id`,
`count_semantics=source_record_occurrences_not_verified_unique_transactions`,
and `eda_run_id=168665c92a8a2ff91598`. `records_in_repeated_groups` retains its
full-original-row equality meaning from the original cohort; it is not recalculated
after filtering, a verified duplicate count, or a deletion recommendation.
Financial and private demographic fields are not present in these downloads.
See [dashboard documentation](DASHBOARD.md) for filter/denominator rules.
