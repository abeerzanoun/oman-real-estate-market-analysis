# Uploaded workbook data quality report

Audit date: 2026-10-13. **28,558 source record occurrences retained; zero rows removed.**

All original SHA-256 checksums match the upload registry. Three worksheet A1 dimensions are reset in memory; no original is saved or renamed. Six worksheets are inspected, including embedded metadata and variable definitions.

| Dataset | Actual records | First date | Last date | Repeats after first | Filename |
|---|---:|---|---|---:|---|
| muscat_brokerage_2025 | 9366 | 2025-01-02 | 2025-09-30 | 6778 | consistent; partial year |
| land_nov_2022 | 7501 | 2022-11-01 | 2022-11-29 | 2629 | consistent; monthly |
| land_dec_2022 | 5667 | 2022-12-04 | 2022-12-29 | 1843 | consistent; monthly |
| land_oct_2024 | 6024 | 2024-10-01 | 2024-10-31 | 0 | consistent; monthly |

## Parsing, types and missingness

Detailed worksheet names, declared/recovered dimensions, headers, column types, missing counts, embedded metadata and actual XML core properties are in `audit_report.json`. `source_column_quality.csv` provides a machine-readable column audit. Creation timestamps describe files/templates, not reporting periods or publication dates. Zero invalid transaction dates or unresolved governorates were found; these checks fail closed on future schema, checksum, period, numeric-type or geography inconsistencies.

Muscat metadata labels the period annual and gives 2025-07-12 as publication, while actual records end 2025-09-30. Treat the release date as inconsistent/stale metadata requiring confirmation; the file is a partial year. No incorrectly named file was found.

## Dataset findings

### muscat_brokerage_2025

8,174 records participate in exact visible-row repeated groups. All occurrences are retained: no official transaction identifier is supplied. These are reported rows, not established unique sales.

Missing source cells: none.

Nonstandard wilayat-label rows: 0. Quality flags: `{}`.

### land_nov_2022

3,675 records participate in exact visible-row repeated groups. All occurrences are retained: no official transaction identifier is supplied. These are reported rows, not established unique sales.

Missing source cells: WILAYAT_EN: 38; VILLAGE_EN: 65; GENDER_NAME_AR: 473; GENDER_NAME_EN: 473.

Nonstandard wilayat-label rows: 1. Quality flags: `{}`.

### land_dec_2022

2,600 records participate in exact visible-row repeated groups. All occurrences are retained: no official transaction identifier is supplied. These are reported rows, not established unique sales.

Missing source cells: WILAYAT_EN: 28; VILLAGE_EN: 27; GENDER_NAME_AR: 286; GENDER_NAME_EN: 286.

Nonstandard wilayat-label rows: 1. Quality flags: `{}`.

### land_oct_2024

0 records participate in exact visible-row repeated groups. All occurrences are retained: no official transaction identifier is supplied. These are reported rows, not established unique sales.

Missing source cells: WILAYAT_EN: 34; VILLAGE_EN: 77; RE_VALUE: 367; DATE_OF_BIRTH: 375; GENDER_NAME_AR: 375; GENDER_NAME_EN: 375.

Nonstandard wilayat-label rows: 0. Quality flags: `{"birth_date_1900_sentinel": 617, "birth_date_after_transaction": 1, "birth_date_missing": 375, "birth_date_under_18": 27}`.

RE_VALUE audit (unverified source units): `{"by_service_code": {"RN13A": {"missing": 366, "present": 233, "records": 599}, "RN13C": {"missing": 1, "present": 5424, "records": 5425}}, "max": "2500000.0", "median": "5383.0", "min": "31.2", "missing": 367, "note": "Empirical tails are review flags, not errors; no clipping. RE_VALUE is not a verified price or OMR amount.", "p01": 919.9, "p99": 150000.0, "present": 5657, "raw_unit_sum": "89547462.666", "tail_flagged": 112, "unit_verified": false}`.

RN13A and RN13C are retained as raw service codes with unknown meanings. Missing amounts stay blank. Low/high values are flagged using the observed 1st/99th percentiles and retained. Owner counts are positive integers; birth-date sentinels, future dates and minors are review flags, not grounds for deleting a market record.

## Geography and coverage

The land files contain ten legacy region labels. Their combined Sharqiyah label is mapped to modern North/South Ash Sharqiyah only using the actual wilayat and the cited official administrative references in `docs/reference_geography.json`. All eleven governorates are represented in each supplied land month. Muscat brokerage covers Muscat only and six wilayats. Normalization preserves raw Arabic/English names, missing translations, tatweel variants and spelling aliases in `geography_source_crosswalk.csv`.

Nizwa’s Barakat Al Mawz parenthetical label is mapped explicitly to parent Nizwa with source retained. الساحل الشرقي appears twice in 2022 under Dhofar; it is retained and flagged as a nonstandard wilayat label. The administrative reference is used only for documented Sharqiyah membership, not as a complete current wilayat inventory.

`coverage_observed.csv` has 42 actual governorate/month cells, and `monthly_reported_records.csv` adds observed wilayat detail. `coverage_matrix_2020_2026.csv` is an availability grid, not generated market observations: absent months have blank counts and explicit statuses. Observed date dimensions contain only actual record dates. Missing days/months do not imply zero activity or completeness.

## Provenance and definitions

The source registry records original paths/checksums and the Git upload commit. Muscat explicitly attributes MOHUP inside the workbook. The other three files are user-attributed official uploads without embedded download URLs. Provider entry points are discovery leads, not verified links to these exact bytes. Exact publication dates for the land files, download URLs, licences, service-code definitions and RE_VALUE unit remain pending. SHA-256 establishes unchanged local bytes, not independent government authenticity. No network data retrieval is performed.

The 2022 BuySell schema, 2024 service-coded schema and Muscat brokerage-only registrations remain separate fact tables. They must not be summed into a common national sales series. Number of owners is not transaction count. Property use/description exist only in brokerage. RE_VALUE is a reported numeric field, not a verified price, turnover or price index. No area measurement exists.

## Supported analysis and remaining requirements

**Ready for limited descriptive analysis of supplied record occurrences**: November versus December 2022 within the same BuySell layout (subject to unverified completeness/definitions); regional and observed wilayat distributions within each supplied land month; Muscat brokerage monthly registrations and property-use/description mix for January–September 2025; missingness, ownership and buyer-type profiles. Power BI can load the separate facts and observed dimensions with these restrictions.

**Not ready for a 2020–2026 market trend or investment study**: no 2020, 2021, 2023 or 2026 uploads; sparse 2022/2024; no national 2025 coverage; no verified monetary units, service definitions, prices, areas or indices; source transaction identity/completeness is unconfirmed. Rankings describe uploaded records only. No unsupported market findings, price estimates or missing-period values are created.

Next obtain exact official dataset URLs/licences and schema notes for these files, RN13A/RN13C meanings and RE_VALUE unit; request complete comparable monthly land/registration series and official NCSI transaction-value/price-index tables. Keep different scopes separate until definitions and reconciliation are verified.
