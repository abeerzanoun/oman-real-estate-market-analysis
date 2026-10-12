# Official data discovery and source register

Reviewed **2026-10-12**. Phase 2 research has inspected actual official NCSI tables online. Original-file acquisition is blocked by this environment's destination policy; no raw originals or analytical CSVs have been created. See [availability matrix](data_availability.md), [machine-readable catalogue](source_catalog.json) and [attempt register](acquisition_manifest.json).

## Providers and evidence levels

| Provider / resource | Evidence verified | Outstanding work |
|---|---|---|
| [NCSI publications](https://www.ncsi.gov.om/publications) | Official catalogue; footer links the Open Government Licence. | Exact release dates and historical versions must be read from publication records. |
| NCSI October 2025 and September 2026 PDFs — exact URLs in catalogue | Actual pages 32–33 inspected online: national activity and price-index categories; residential-land index by governorate. | Original download/hash, full-file integrity, Poppler extraction and reconciliation. Publication month on PDF cover is verified; exact publication date remains null. |
| [NCSI 2026 yearbook](https://api.ncsi.gov.om/uploads/pdfs/statistical_year_book_2026___issue_54_1777963604.pdf) | Official-host response detected by web tool, exceeding its 17 MB limit. | No historical table coverage inferred until inspected. |
| [NCSI Oman Data Portal housing dataset](https://data.gov.om/OMHSNG2016/housing?lang=en) | Official metadata: annual/monthly; land-use, plots and building permits; date range shown through January 2025. | Item-level indicator coverage, export/API paths, stale release metadata and actual files. These measures are not sales transactions. |
| [MOHUP real estate transaction page](https://mohup.gov.om/en/open-data/data/Realestate%20Transaction) | Official indexed monthly land-sale releases; indexed Arabic counterpart also provides period metadata. | Live page timed out; downloads, field schema, full coverage and exact licences not confirmed. |
| MOHUP Q1 2021/Q1 2022 regional bulletins and annual report 2021 | Exact official CMS URLs identified in catalogue; indexed regional tables. | Files not inspected; publication dates, reporting scope and licence remain pending. |
| [Oman National Open Data Portal](https://opendata.gov.om/en) | Official indexed MOHUP regional brokerage-registration resources for 2025. | Direct web fetch restricted; verify each page's own dataset versus related listings, downloadable URLs, geography, units and licence. |
| [Oman News Agency](https://omannews.gov.om/topics/en/79/show/107440/dark) | Official contextual ministry/market reporting identified. | News prose is not substituted for a statistical dataset. |
| [Central Bank of Oman Financial Stability Report 2022](https://cbo.gov.om/sites/assets/Documents/English/Publications/FSR/FinancialStabilityReport2022.pdf) | Official report identified as a price-market context lead. | Charts, methodology and reuse terms not inspected; not incorporated into analysis. |

Third-party inventories were used only to discover candidate official URLs for an XLSX release and a migrated historical PDF. Their claims, dates and rows are not accepted as government observations. Such URLs remain `secondary_discovery_unverified` until verified on the official host.

## Verified definitions and units

NCSI national activity tables distinguish total traded property value, sales, mortgages, barter, fees and issued deeds. Monetary measures use **million OMR**; counts are raw counts. Total traded value is not sales value. Issued deeds are not sales-contract counts. Six observation columns mix annual, monthly and year-to-date intervals; the final percent-change column must be excluded from observations.

Both inspected price tables use **base year 2018**, with category indices and governorate indices within residential land. Weights, index points and inflation percentages are different quantities. September 2026 has changed displayed weights; the same 2025 comparison quarter also differs between releases. September 2026 marks 2026 indices provisional. Preserve release vintages and verify revision methodology before combining indices. Transaction tables do not disaggregate property categories or geography.

## Licences and attribution

NCSI's [Open Government Licence document](https://www.ncsi.gov.om/assets/docs/gov_license.pdf) was read through the web tool. It permits reuse under stated conditions, requires original attribution and disclosure of modifications, excludes certain protected material and prohibits misleading endorsement claims. The NCSI publication site links it as its content licence. Record this as **provider-site licence verified**, rather than inventing a resource-level licence statement.

MOHUP and national-portal resource-specific licences remain unverified. A search-index reference to open data is not enough to assert the terms for every file. Such downloads, if access becomes available, stay local until terms are resolved. No institutional logos are included.

## Acquisition and provenance

`source_catalog.json` records exact discovered URLs, evidence status, publication-period labels, verified reporting slices, units, geography, licence evidence and reviewed extraction profiles. Null publication dates are intentional; filename timestamps and HTTP Last-Modified are not treated as publication dates.

`python -m src.collect_data` attempted eight URLs on 2026-10-12. Every request failed at **proxy CONNECT with 403**, before the source server could be evaluated. The attempt register keeps URLs, UTC attempt times and exact errors; `raw_path`, byte length and checksum remain null. Failed responses are never saved as original datasets. This is a network-policy block, not an automatic approval rejection or proof that the datasets are unavailable.

After access is enabled, originals retain their decoded source filename in `data/raw/<source_id>/`. Downloads check PDF/XLSX signatures, record SHA-256 and response metadata, and refuse to overwrite changed originals. Signature checks do not establish semantic integrity; processing additionally runs Poppler and verifies the recorded checksum.

## Limitations and next retrieval priorities

1. Permit official hosts through the managed environment configuration: `api.ncsi.gov.om`, `www.ncsi.gov.om`, `ncsi.gov.om`, `cms.mohup.gov.om`, `mohup.gov.om`, `www.housing.gov.om`, `webapps.housing.gov.om`, `data.gov.om`, `www.data.gov.om`, `opendata.gov.om` (and observed official redirect hosts if needed). No proxy bypass is used.
2. Retrieve the two inspected NCSI bulletins and verify layout/values against originals. Process only reviewed profiles; reconcile output before analysis.
3. Retrieve the yearbook to verify annual 2020–2025 coverage, then historical bulletins for missing monthly/quarterly slices. Legacy Elibrary paths returned 404 through web retrieval and need current official replacements.
4. Inspect MOHUP regional bulletins and each national-portal resource; distinguish brokerage subsets and land transactions from the entire market.
5. Confirm exact publication dates, resource terms, revisions and price-index comparability. Preserve missing values; never turn a discovery gap into a zero or fabricate a complete year.
