# Power BI model for audited uploaded records

This documents the alternative **row-level** model. The [current reporting package](README.md) selects the EDA aggregate model instead, with SUM-weight measures. Do not import both as additive facts. The count rules below apply only to this row-level alternative.

Import CSVs from one `data/processed/audited/<run_id>/` folder. Use UTF-8 encoding (65001); exports include a UTF-8 BOM for Excel. Keep CSV quote handling enabled (Power Query QuoteStyle.Csv) for embedded line breaks in original location labels. Do not auto-detect dates/units without reviewing the dictionary.

Use separate fact tables for 2022 BuySell records, 2024 service-coded records and 2025 Muscat brokerage registrations. Do not append them into a national sales table. Each fact has a unique lineage record_id, not an official transaction ID. Use **Count Rows** labelled "Reported record occurrences"; distinct visible-row signatures are not a count of unique transactions.

One-to-many, single-direction relationships:

| Dimension | Key | Fact key | Type |
|---|---|---|---|
| dim_dataset | dataset_id | dataset_id | Text |
| dim_governorate | governorate_id | governorate_id | Text |
| dim_wilayat | wilayat_key | wilayat_key | Text |
| dim_date | transaction_date | transaction_date | Date, ISO yyyy-MM-dd |

Dimensions link directly to facts; avoid also linking governorate to wilayat, which creates multiple filter paths. `dim_date` includes only observed dates, has gaps and is **not a complete calendar**. Do not mark it as a date table for standard time-intelligence functions. No annual/YTD growth measure is valid over these partial files.

Set year, month, source_row, number_of_owners, group-size/rank and reported_record_count to whole numbers; flags to Boolean; IDs, names, service codes and checksums to Text. RE_VALUE has at most three source decimal places; Fixed decimal number (four places) preserves these, but its currency_unit is blank/unverified. Keep it out of financial KPI measures until an official unit and service definition are confirmed. Null values must remain null, not zero.

Load the coverage metadata tables separately for a coverage page; blank counts mean not supplied/outside scope/future, never zero activity. `monthly_reported_records` is an alternative summarized table, not an additional fact to double-count alongside raw records. There is no official price, area or index table. Birth date and gender are excluded from derived tables.

Ready uses: distributions of uploaded rows within each supplied month; Nov/Dec 2022 same-layout comparison with completeness caveat; Muscat brokerage monthly and property mix for Jan–Sep 2025. No dashboard or market conclusions have been created by this preparation phase.
