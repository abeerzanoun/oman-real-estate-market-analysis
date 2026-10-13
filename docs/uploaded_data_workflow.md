# Audit and preparation of the four uploaded workbooks

This offline workflow is the dedicated **row-level** adapter. The existing `src.manual_ingestion` is for separately registered aggregate indicator tables; its admission and deduplication rules do not apply to these uploads.

## Run and review

From the repository root using the locked Python 3.12 environment:

```bash
python -m src.audit_uploaded_data
python -m src.validate_uploads
python -m pytest
python -m src.validate_environment
python -m pip check
```

The availability review date defaults explicitly to 2026-10-13. Use `--as-of YYYY-MM-DD` for a later review; no future period is inferred as an observation. Every registered original must exist and match `docs/uploaded_source_registry.json`. The adapter fails on unreviewed schemas, source checksum changes, inconsistent bilingual geography, filename/date mismatches or invalid transaction dates/owner counts. Correct a source registration only after inspecting a genuine source revision. A failure produces no partial audit output.

`src.excel_reader` inspects the ZIP worksheet XML and actual workbook rows independently of declared dimensions. It resets all read-only worksheet dimensions before iterating; three sources falsely declare A1. Original workbooks are never saved. Numeric XML tokens preserve RE_VALUE decimals exactly. Source XML core properties are read directly to avoid library-generated modification dates.

## Immutable run outputs

A run ID fingerprints the original checksums, registry, geography evidence, implementation and availability date. Outputs appear in `data/processed/audited/<run_id>/`. Rerunning identical inputs checks byte-identical artifacts; a changed existing output raises an error instead of being overwritten. `manifest.json` lists original and output SHA-256 hashes. No network request occurs.

Separate source families:

- `land_records_2022.csv`: November and December BuySell-layout record occurrences, same observed schema, 13,168 rows. Completeness and exact service definition remain unverified.
- `land_records_2024.csv`: October service-coded records, 6,024 rows. Service labels RN13A/RN13C and reported RE_VALUE unit remain unknown.
- `muscat_brokerage_records_2025.csv`: 9,366 Muscat brokerage registrations, January–September only, with Arabic property-use and description fields.

Each row has a generated lineage `record_id`, source SHA, dataset ID, worksheet and Excel row. This is **not an official transaction ID**. All source occurrences remain. Exact visible-row repetitions are marked with raw-row signature, group size and occurrence rank; no record is deleted on that basis. Raw Arabic/English region, wilayat and village names remain available. Missing source cells stay blank. Embedded line breaks/trailing spaces in raw source labels remain quoted CSV content; CSV physical line counts are not record counts. Git attributes preserve exact CSV bytes across platforms. Birth dates/gender stay in originals and are excluded from market-facing exports; aggregate quality findings remain in the audit report.

`monthly_reported_records.csv` reports row occurrences by dataset, scope, governorate, observed wilayat and month. It does not certify unique sales. `coverage_observed.csv` contains only observed cells. `coverage_matrix_2020_2026.csv` is an explicit availability **metadata** grid: absent counts are blank, never imputed market observations. Reference governorate labels and observed-date dimensions are not synthetic real estate data. No missing-day/month expansion is performed.

`geography_source_crosswalk.csv` documents raw aliases and methods, including legacy Sharqiyah derived from actual wilayat. `docs/reference_geography.json` cites the official sources used; Sinaw uses the current North Sharqiyah government reference because older lists omit it. `source_column_quality.csv` and `audit_report.json` contain worksheet dimensions, types, headers, missingness, source metadata, repeats, categorical inventories and numerical checks. `data_quality_report.md` explains their implications.

## Verification versus analysis readiness

Local bytes and actual reporting dates are verified. Source authenticity is attributed from the user upload or embedded MOHUP attribution; exact official URLs, licences and land-file publication dates remain unresolved. Entry points are not direct evidence for the four exact workbook versions. Registry null fields stay null until supported by official evidence.

Meaningful descriptive analysis of **these uploaded rows within each scope** is possible. National 2020–2026 trends, unique transaction totals, OMR turnover, price/area comparisons, indices and investment recommendations are not supported. Source availability does not demonstrate complete market capture. Never union the three families into one sales fact table, infer service code meanings, or relabel RE_VALUE as an OMR price.

CI runs `src.validate_uploads`: registered row files use this adapter; every remaining XLSX/CSV is still admitted through the aggregate contract. Unknown uploads are not silently skipped. Historical aggregate status reports remain historical; this audit's report describes the current row-level uploads.
