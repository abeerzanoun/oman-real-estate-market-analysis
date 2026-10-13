# Analytical table dictionary

The [uploaded-source dictionary](uploaded_data_dictionary.md) remains authoritative for raw/audited fields. This document describes EDA transformations and monthly Power BI aggregates. CSVs are UTF-8 BOM, null = blank, dates = ISO. Category codes/labels are Text; counts/ranks are whole numbers; percentages are numeric on **0–100** scale. Facts contain no monetary fields.

## Reused keys and fields

`dataset_id`, `scope_id`, `governorate_id`, `wilayat_key`, `wilayat_ar`, `buyer_type`, `property_use_key`, `property_description_key`, `service_sub_id`, `ownership_mode` and `nonstandard_wilayat_label` retain audited definitions. Wilayat keys are observed labels, not official administrative codes. Category display labels stay in original Arabic, including source spelling. Exact official URLs/licences and financial/code definitions remain unresolved in dim_dataset.

## New derived variables

| Field | Type / unit | Definition |
|---|---|---|
| period_id | Text YYYY-MM | Derived from actual transaction_date; only observed months |
| period_label | Text | English abbreviated month/year presentation label, not a new reporting period |
| ownership_band | Text | Derived from actual number_of_owners: 1 owner, 2 owners, 3 owners, 4 owners, 5+ owners |
| reported_record_count | Whole number / source occurrences | Number of retained source rows in the stated group; not physical fact rows or independently unique transactions |
| cohort_record_count | Whole number / source occurrences | Explicit denominator for the share in that summary table |
| share_pct | Decimal / percent 0–100 | reported_record_count / cohort_record_count × 100 |
| within_governorate_share_pct | Decimal / percent 0–100 | Wilayat count / that dataset-month-governorate count × 100 |
| rank_within_dataset_period | Whole number | Governorate count rank, descending; ties share minimum rank |
| records_in_repeated_groups | Whole number / source occurrences | Count of rows whose audited visible-row group size exceeds one; identity not established |
| repeated_occurrences_after_first | Whole number / source occurrences | Source rows after the first identical visible-row occurrence; these rows are retained |
| repeated_group_share_pct | Decimal / percent 0–100 | records_in_repeated_groups / source cohort count × 100 |
| reported_amount_present_records / reported_amount_missing_records | Whole number, nullable | Audit-derived amount presence only in 2024; null for schemas without an amount field |
| monetary_unit_verified | Boolean | False for these inputs; no OMR unit assumed |
| november_records / december_records | Whole number | Two same-layout 2022 observed-month governorate counts |
| november_share_pct / december_share_pct | Decimal / percent 0–100 | Governorate shares within each respective source file |
| record_count_difference | Whole number / source occurrences | December − November |
| record_count_change_pct | Decimal / percent | (December − November) / November × 100; supplied-file comparison, not annual market growth |
| share_change_percentage_points | Decimal / percentage points | December share − November share |
| comparison_scope | Text | land_buy_sell_2022 only |
| definition_status | Text | meaning_unverified for the observed 2024 service codes |
| first_record_date / last_record_date | ISO Date | Actual source-record bounds, not proof of complete capture |
| observed_months / observed_governorates / observed_wilayat_labels | Whole number | Distinct observed values, not administrative inventory completeness |
| nonstandard_wilayat_rows | Whole number | Occurrences with a nonstandard source wilayat label, preserved |
| rows_removed | Whole number | Zero; no record-level deduplication or clipping |

## Table grains and denominators

| Table | Grain | Denominator / role |
|---|---|---|
| dataset_summary | One row per source dataset | Source bounds, coverage and row total |
| data_quality_summary | One row per source dataset | Repeat/missingness metadata, not another activity fact |
| governorate_counts | Dataset, scope, month, governorate | Same dataset/month count |
| wilayat_counts | Dataset, scope, month, governorate, wilayat, nonstandard flag | Dataset/month; additional within-governorate share |
| governorate_nov_dec_2022 | Governorate | Explicit Nov and Dec 2022 file totals |
| buyer_type_counts | Dataset, scope, month, buyer type | Same dataset/month |
| ownership_counts | Dataset, scope, month, owner band | Same dataset/month |
| service_code_counts_2024 | Dataset, month, raw service code | October file total |
| service_by_governorate_2024 | Dataset, month, governorate, raw service code | Same governorate's October count |
| brokerage_monthly_counts | Dataset, scope, month | Nine supplied-month total |
| brokerage_wilayat_counts | Dataset, scope, governorate, wilayat | Nine supplied-month total |
| brokerage_wilayat_monthly_counts | Dataset, scope, month, wilayat | Same month's brokerage count |
| brokerage_property_use / brokerage_property_description / brokerage_transaction_category | Dataset, scope, literal category | Nine supplied-month total; three distinct classification fields |
| brokerage_property_use_by_wilayat | Dataset, scope, wilayat, literal use | That wilayat's nine supplied-month count |
| fact_land_2022 | Dataset, month, governorate, wilayat, nonstandard flag, buyer, owner band | Monthly additive count; no money |
| fact_land_2024 | Same plus raw service code, ownership mode | Separate service-coded monthly additive count; no money |
| fact_brokerage_2025 | Dataset, month, governorate, wilayat, nonstandard flag, use key, description key | Separate brokerage monthly additive count; no money |
| dim_dataset | Source dataset ID | Reused audited registry/coverage metadata |
| dim_governorate | Canonical governorate ID | Eleven reference labels, not generated observations |
| dim_wilayat | Observed wilayat key | Reused audited labels, nonstandard labels documented |
| dim_period | Observed month | Twelve rows; year/month/label; no missing months generated |
| dim_buyer_type / dim_service_code / dim_ownership_band | Actual observed category | Dimension keys; service meaning flagged unknown |
| dim_property_use / dim_property_description | Actual audited normalized category key | Original Arabic labels; no invented category rows |
| coverage_observed | Dataset, scope, month, governorate | 42 supplied cells; not additive to facts |
| coverage_matrix_2020_2026 | Scope, governorate, year, month | Availability metadata, blank missing counts; inherited audit statuses |
| source_column_quality | Source dataset, original column | Inherited missing/type audit, not observations |

`analysis_manifest.json` records input audit manifest SHA, all input/output hashes, base-main commit, original hashes, implementation/lock hashes, rendering-environment versions/font hashes, verified canonical analytical-CSV baseline, table rows, per-family source/fact reconciliation and the figure inventory. `insights.md` is generated from summary tables. Arabic shaping is confined to figures; neither the tables nor keys contain presentation-form substitutions.


## Duplicate interpretation reviewed before import

The completed [duplicate audit](../reports/DUPLICATE_AUDIT.md) separates full-source patterns from projected business-attribute collisions. `records_in_repeated_groups` inherits all-original-column matching, including non-exported demographics; it is not a confirmed duplicate count. Generated record IDs track original occurrences. No source occurrences were removed and current fact/summary files remain unchanged.
