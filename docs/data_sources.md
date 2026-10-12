# Data source strategy and verification register

Reviewed: 2026-10-11. This stage verifies official provider/publication pages only. No datasets have been downloaded, profiled, or accepted for analysis. Search-index evidence is distinguished from validation of files and historical series.

## Verified source pages and publication leads

| Provider | Official link | Evidence observed | Still requires investigation |
|---|---|---|---|
| National Centre for Statistics and Information (NCSI) | https://ncsi.gov.om/ | Official publication listing includes Monthly Statistical Bulletin and Real Estate Price Inflation Report. | Archive completeness for 2020–2026, release dates, price index methodology, base year, revision policy and category/geographic detail. |
| NCSI publications | https://www.ncsi.gov.om/publications | Official publication catalogue. | Locate relevant historical editions; confirm download links and reusable formats. |
| NCSI Monthly Statistical Bulletin, October 2025 | https://www.ncsi.gov.om/Elibrary/LibraryContentDoc/bar_Monthly_Statistical_Bulletin_October2025_baad7d54-de99-4dd9-915d-4cce0d876d64.pdf | Search index identifies a real-estate activity section and traded-value measure in million OMR, attributed to MOHUP. PDF not downloaded or extracted. | Verify table definitions, transactions covered, monthly versus cumulative periods, values and counts; do not treat total traded value as sales value. |
| Ministry of Housing and Urban Planning (MOHUP) | https://mohup.gov.om/en/open-data/data/Realestate%20Transaction | Official real estate transaction landing page; Arabic counterpart lists monthly land sale/purchase datasets and download formats. | File schemas, geographic fields, transaction scope, licence, duplicate handling and complete historical coverage. No assumption that land transactions represent all property categories. |
| MOHUP open data policy/about | https://webapps.housing.gov.om/opendata/en/pages/about.aspx | Official page describes ministry commitment to open data. | Resource-specific reuse terms and availability of historical regional activity releases. |
| Oman National Open Data Portal | https://opendata.gov.om/en | Official national portal discovered. | Search ministry datasets; verify publisher, versions, regional coverage and definitions. |
| NCSI Oman Data Portal | https://data.gov.om/OMHSNG2016/housing?lang=en | Official housing topic page with real estate navigation. | Indicator availability, periods, dimensions, exports and metadata. This is a separate portal from the national open data portal above. |

## Proposed dataset targets — not yet acquired or validated

- Transaction counts and values: NCSI bulletins and MOHUP monthly releases. Confirm whether sales, mortgages, exchanges, fees, deeds or other registrations are separate series.
- Property price indicators: NCSI price inflation reports and bulletin index tables. Verify residential/category scope, index versus percentage change, base periods and geographic availability.
- Regional market activity: MOHUP and national portal resources. Governorate and wilayat detail is a target, not a confirmed common schema.
- Historical coverage: build an availability matrix by metric, geography and reporting frequency. No reliable full 2020–2026 panel has been established; 2026 must remain partial until a complete official year is published.

## Acceptance and acquisition protocol for the next phase

1. Record exact dataset title, publisher, landing/download URLs, release date, retrieval timestamp, licence and original filename before acquisition.
2. Record SHA-256 checksum, file format, language, units, frequency, spatial level, period start/end, cumulative status, revisions and index base where applicable.
3. Preserve immutable originals locally in `data/raw/`; review redistribution rights before committing any source files.
4. Reconcile official definitions and overlaps across portals; avoid counting republished records twice. Keep sale and mortgage measures separate.
5. Document missing periods and comparability breaks. Missing values are not zero; never manufacture observations or complete a partial year with invented values.
6. Approve the actual schema and update the data dictionary before processing. Use matching reporting periods for year-on-year comparisons.

Prefer machine-readable CSV/XLSX with documented definitions. PDF extraction, if necessary later, requires reconciliation against original tables. Provider authority alone does not establish dataset suitability or completeness.
