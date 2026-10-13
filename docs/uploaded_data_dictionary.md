# Data dictionary: actual uploaded row-level datasets

This dictionary describes real source fields and derived lineage/reference fields. It supersedes proposed-field assumptions **only for these four uploads**. CSV encoding is UTF-8 BOM, nulls are empty cells, dates ISO YYYY-MM-DD. Source scopes remain separate. There are no source transaction IDs, transaction-count aggregates, verified OMR fields, prices per square metre, areas or property price indices.

## Source schemas and mappings

| Source field | Standard field | Type / interpretation | Available scope |
|---|---|---|---|
| TRANSACTION_DATE / تاريخ الإجراء | transaction_date | Date of reported procedure/transaction; ISO; year/month derived from contents | All |
| REGION_AR / REGION_EN | source_region_ar / source_region_en | Exact original region labels, including legacy combined Sharqiyah | Land |
| الولاية / WILAYAT_AR | source_wilayat_ar | Original Arabic wilayat label; office/subunit labels can occur | All |
| WILAYAT_EN | source_wilayat_en | Original English name, missing values preserved, translations not invented | Land |
| VILLAGE_AR / VILLAGE_EN | source_village_ar / source_village_en | Original village/location labels, not standardized administrative IDs | Land |
| BUYER_TYPE | buyer_type | Original Individual or Company, no inferred investor classification | Land |
| NO_OF_OWNERS | number_of_owners | Positive integral number of owners, **not transaction count** | Land |
| SERVICE_SUB_ID | service_sub_id | RN13A/RN13C; meanings require official schema notes | October 2024 only |
| RE_VALUE | reported_re_value | Source numeric amount, exact Decimal from worksheet XML; 367 blank; unit unknown | October 2024 only |
| SINGLE_MULTIPLE | ownership_mode | Source Single/Multiple; checked against number_of_owners | October 2024 only |
| DATE_OF_BIRTH | No market export | Source birth date; missing/sentinel/future/age issues counted in audit only | October 2024 only |
| GENDER_NAME_AR / GENDER_NAME_EN | No market export | Original gender labels; missingness audited; originals retained | Land |
| اسم المعاملة | transaction_category_ar | Brokerage-office sale-contract registration; exact Arabic text | Muscat brokerage only |
| نوع الإستعمال | property_use_ar | Eight observed Arabic uses; not substituted for property descriptions | Muscat brokerage only |
| وصف العقار | property_description_ar | Thirteen observed Arabic descriptions; not a property price or area | Muscat brokerage only |

Actual periods: 2022-11-01–2022-11-29 (7,501 rows), 2022-12-04–2022-12-29 (5,667), 2024-10-01–2024-10-31 (6,024), 2025-01-02–2025-09-30 (9,366). Min/max dates describe observed records, not proof of complete monthly capture. Brokerage metadata says annual, but actual coverage is partial.

## Derived fact fields

| Field | Type | Definition / validation |
|---|---|---|
| record_id | Text, SHA-256 | Generated from original SHA, worksheet and Excel row; unique lineage, not an official transaction identifier |
| dataset_id | Text | One of four registered source IDs; references dim_dataset |
| scope_id | Text | Three different definition families; never silently combined |
| source_sha256 | Text, SHA-256 | Original bytes verified before/after parsing |
| source_sheet | Text | Actual worksheet name, including original language |
| source_row | Whole number | Original 1-based Excel data row; unaffected by dimension reset |
| year / month | Whole number | Actual transaction_date year/month, month 1–12 |
| governorate_id | Text | Canonical slug for one of eleven governorates; source regions or documented legacy-region mapping |
| wilayat_ar | Text | Cleaned Arabic label, documented spelling aliases/parent mapping; nonstandard labels still flagged |
| wilayat_key | Text | governorate_id plus normalized Arabic wilayat label; observed label key, not official government code |
| wilayat_normalization_method | Text | Unicode cleanup or explicit observed spelling/parent alias |
| governorate_mapping_method | Text | Source bilingual region, embedded Muscat scope, or legacy Sharqiyah resolved by verified wilayat |
| nonstandard_wilayat_label | Boolean | Flags الساحل الشرقي, retained under source Dhofar without inventing a wilayat |
| raw_row_signature | Text, SHA-256 | Hash of original selected data-row values, including non-exported demographics; compare only within source dataset |
| repeated_row_group_size | Whole number | Number of exact visible-row matches within source file; greater than one is not proof of duplicate transaction |
| occurrence_rank | Whole number | Source-order rank within repeated group; no deletion based on rank |
| property_use_key / property_description_key | Text | Normalized Arabic comparison keys, raw source labels retained; brokerage only |
| currency_unit | Text, nullable | Unverified, currently blank; not set to OMR without evidence |
| reported_value_tail_flag | Boolean | Observed RE_VALUE below p01 or above p99; review flag, all original values retained |

## Reference, summary and quality tables

- `dim_dataset`: registered metadata (see JSON registry for field-level definitions), original filename/hash, user upload commit, attributed provider/evidence, official URLs/licences nullable, unit/code definitions unresolved, observed min/max dates and actual row counts. Provider entry point is a lead, not the exact workbook source URL. No publication date is inferred from ZIP creation timestamps.
- `dim_governorate`: eleven reference slugs and Arabic/English labels. Reference names are not generated market observations.
- `dim_wilayat`: observed keys, governorate and cleaned Arabic labels. Nonstandard labels remain documented; this is not a complete administrative inventory.
- `dim_date`: unique actual transaction dates, year/month. No manufactured missing dates.
- `monthly_reported_records`: dataset_id, scope_id, governorate_id, wilayat_key, year, month, reported_record_count. Count = retained source row occurrences, not verified distinct sales.
- `coverage_observed`: scope_id, governorate_id, year, month, reported_record_count; 42 actual governorate-month cells.
- `coverage_matrix_2020_2026`: same keys plus availability_status. 2,772 metadata cells over three scopes; statuses observed/not_provided/outside_source_scope/future_period/no_rows_in_supplied_file. Blank counts mean unavailable/out of scope; zero could only mean no rows in a supplied scope-period, never proven zero market activity. Current uploads have no such zero cells.
- `source_column_quality`: dataset_id, original column, missing source cells, observed Python types and their counts. Zero missing source columns does not demonstrate completeness.
- `geography_source_crosswalk`: original region/wilayat language pairs, canonical IDs/label/key, mapping methods, nonstandard-label flag, reported_record_count per source alias combination. Missing English labels remain blank.
- `audit_report.json`: all worksheets/dimensions, source headers/types, embedded metadata, source XML properties, reporting periods, per-source repeated groups, categorical inventories, numerical/profile flags and provenance limits.
- `manifest.json`: run_id, input, implementation/reference/lock hashes, and artifact hashes. Original workbook bytes are preserved.

`reported_re_value` can support data-quality profiling of reported numbers. Monetary aggregation, code-specific market classification and price analysis require official field definitions first. The 2022 and 2024 land layouts and Muscat brokerage registrations are not interchangeable definitions of sales.
