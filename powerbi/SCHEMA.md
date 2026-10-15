# Verified import schema

Generated from `model_contract.json`; no inferred Desktop types. All columns use Do not summarize unless an explicit measure aggregates them. Dates are metadata only.

| Table | Role | CSV rows | Source occurrences (SUM weights) |
|---|---|---:|---:|
| fact_land_2022 | fact | 361 | 13168 |
| fact_land_2024 | fact | 257 | 6024 |
| fact_brokerage_2025 | fact | 403 | 9366 |
| dim_dataset | dimension | 4 | — |
| dim_period | dimension | 12 | — |
| dim_governorate | dimension | 11 | — |
| dim_wilayat | dimension | 65 | — |
| dim_buyer_type | dimension | 2 | — |
| dim_ownership_band | dimension | 5 | — |
| dim_service_code | dimension | 2 | — |
| dim_property_use | dimension | 8 | — |
| dim_property_description | dimension | 13 | — |
| coverage_matrix_2020_2026 | disconnected_metadata | 2772 | — |
| dataset_summary | disconnected_metadata | 4 | — |
| data_quality_summary | disconnected_metadata | 4 | — |
| source_column_quality | disconnected_metadata | 42 | — |

## fact_land_2022

Unique aggregate grain: `dataset_id`, `period_id`, `governorate_id`, `wilayat_key`, `nonstandard_wilayat_label`, `buyer_type`, `ownership_band`.

| Column | Power Query / Desktop type | Nullable |
|---|---|---|
| dataset_id | Text | no |
| period_id | Text | no |
| governorate_id | Text | no |
| wilayat_key | Text | no |
| nonstandard_wilayat_label | True/False | no |
| buyer_type | Text | no |
| ownership_band | Text | no |
| reported_record_count | Int64 / Whole number | no |
| records_in_repeated_groups | Int64 / Whole number | no |

## fact_land_2024

Unique aggregate grain: `dataset_id`, `period_id`, `governorate_id`, `wilayat_key`, `nonstandard_wilayat_label`, `buyer_type`, `ownership_band`, `service_sub_id`, `ownership_mode`.

| Column | Power Query / Desktop type | Nullable |
|---|---|---|
| dataset_id | Text | no |
| period_id | Text | no |
| governorate_id | Text | no |
| wilayat_key | Text | no |
| nonstandard_wilayat_label | True/False | no |
| buyer_type | Text | no |
| ownership_band | Text | no |
| service_sub_id | Text | no |
| ownership_mode | Text | no |
| reported_record_count | Int64 / Whole number | no |
| records_in_repeated_groups | Int64 / Whole number | no |

## fact_brokerage_2025

Unique aggregate grain: `dataset_id`, `period_id`, `governorate_id`, `wilayat_key`, `nonstandard_wilayat_label`, `property_use_key`, `property_description_key`.

| Column | Power Query / Desktop type | Nullable |
|---|---|---|
| dataset_id | Text | no |
| period_id | Text | no |
| governorate_id | Text | no |
| wilayat_key | Text | no |
| nonstandard_wilayat_label | True/False | no |
| property_use_key | Text | no |
| property_description_key | Text | no |
| reported_record_count | Int64 / Whole number | no |
| records_in_repeated_groups | Int64 / Whole number | no |

## dim_dataset

Unique non-null key: `dataset_id`.

| Column | Power Query / Desktop type | Nullable |
|---|---|---|
| dataset_id | Text | no |
| scope_id | Text | no |
| file | Text | no |
| sha256 | Text | no |
| sheet | Text | no |
| header_row | Int64 / Whole number | no |
| audited_row_count | Int64 / Whole number | no |
| filename_period_label | Text | no |
| provider | Text | no |
| provider_evidence | Text | no |
| official_download_url | Text | yes |
| official_landing_url | Text | yes |
| provider_entry_point | Text | no |
| source_verification_status | Text | no |
| licence | Text | yes |
| licence_url | Text | yes |
| currency_unit | Text | yes |
| service_code_definitions | Text | no |
| uploaded_commit | Text | no |
| min_date | Date (ISO yyyy-MM-dd) | no |
| max_date | Date (ISO yyyy-MM-dd) | no |
| reported_record_count | Int64 / Whole number | no |

## dim_period

Unique non-null key: `period_id`.

| Column | Power Query / Desktop type | Nullable |
|---|---|---|
| period_id | Text | no |
| year | Int64 / Whole number | no |
| month | Int64 / Whole number | no |
| period_label | Text | no |

## dim_governorate

Unique non-null key: `governorate_id`.

| Column | Power Query / Desktop type | Nullable |
|---|---|---|
| governorate_id | Text | no |
| governorate_en | Text | no |
| governorate_ar | Text | no |

## dim_wilayat

Unique non-null key: `wilayat_key`.

| Column | Power Query / Desktop type | Nullable |
|---|---|---|
| wilayat_key | Text | no |
| governorate_id | Text | no |
| wilayat_ar | Text | no |

## dim_buyer_type

Unique non-null key: `buyer_type`.

| Column | Power Query / Desktop type | Nullable |
|---|---|---|
| buyer_type | Text | no |

## dim_ownership_band

Unique non-null key: `ownership_band`.

| Column | Power Query / Desktop type | Nullable |
|---|---|---|
| ownership_band | Text | no |

## dim_service_code

Unique non-null key: `service_sub_id`.

| Column | Power Query / Desktop type | Nullable |
|---|---|---|
| service_sub_id | Text | no |
| definition_status | Text | no |

## dim_property_use

Unique non-null key: `property_use_key`.

| Column | Power Query / Desktop type | Nullable |
|---|---|---|
| property_use_key | Text | no |
| property_use_ar | Text | no |

## dim_property_description

Unique non-null key: `property_description_key`.

| Column | Power Query / Desktop type | Nullable |
|---|---|---|
| property_description_key | Text | no |
| property_description_ar | Text | no |

## coverage_matrix_2020_2026

| Column | Power Query / Desktop type | Nullable |
|---|---|---|
| scope_id | Text | no |
| governorate_id | Text | no |
| year | Int64 / Whole number | no |
| month | Int64 / Whole number | no |
| availability_status | Text | no |
| reported_record_count | Int64 / Whole number | yes |

## dataset_summary

| Column | Power Query / Desktop type | Nullable |
|---|---|---|
| dataset_id | Text | no |
| scope_id | Text | no |
| reported_record_count | Int64 / Whole number | no |
| first_record_date | Date (ISO yyyy-MM-dd) | no |
| last_record_date | Date (ISO yyyy-MM-dd) | no |
| observed_months | Int64 / Whole number | no |
| observed_governorates | Int64 / Whole number | no |
| observed_wilayat_labels | Int64 / Whole number | no |
| nonstandard_wilayat_rows | Int64 / Whole number | no |

## data_quality_summary

| Column | Power Query / Desktop type | Nullable |
|---|---|---|
| dataset_id | Text | no |
| reported_record_count | Int64 / Whole number | no |
| records_in_repeated_groups | Int64 / Whole number | no |
| repeated_occurrences_after_first | Int64 / Whole number | no |
| repeated_group_share_pct | Decimal number | no |
| rows_removed | Int64 / Whole number | no |
| reported_amount_present_records | Int64 / Whole number | yes |
| reported_amount_missing_records | Int64 / Whole number | yes |
| monetary_unit_verified | True/False | no |

## source_column_quality

| Column | Power Query / Desktop type | Nullable |
|---|---|---|
| dataset_id | Text | no |
| column | Text | no |
| missing | Int64 / Whole number | no |
| observed_types | Text | no |
