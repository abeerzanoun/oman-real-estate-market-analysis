# Data provenance and completeness audit

**Reviewed:** October 15, 2026 (Asia/Muscat).

**Baseline:** `main` at `d664f7f3ae4c3517ce4fb833a3038d31f2fe994c` (including merged PR #9).

**Scope:** the four original XLSX files currently feeding the audited records, EDA and dashboard. This is a documentation-only review; no original, processed dataset or dashboard is changed.

## Findings

**None of the four exact official dataset-page/download URLs is verified by the available evidence. None has a documented, file-applicable redistribution licence.** Muscat has verifiable **embedded Ministry attribution**; the other three files have **user-declared attribution**. Embedded attribution is stronger documentary evidence than a declaration alone, but neither independently authenticates an official download.

The four files contain **28,558 source record occurrences**. This is an inventory total across different administrative populations, **not** a national market total or a verified unique-transaction count. Every current checksum matches both the registry and its original Git upload blob.

| Local workbook | Exact official source URL | Attribution evidence | Redistribution licence | Actual dated records | Occurrences |
|---|---|---|---|---|---:|
| [muscat_brokerage_sales_2025.xlsx](data/raw/manual/muscat_brokerage_sales_2025.xlsx) | Unverified; registry URL fields are null | Ministry platform named in embedded metadata; contact domain `housing.gov.om` | Not documented/verified | 2025-01-02–2025-09-30 | 9,366 |
| [oman_land_transactions_nov_2022.xlsx](data/raw/manual/oman_land_transactions_nov_2022.xlsx) | Unverified; registry URL fields are null | User-declared Ministry attribution; no embedded publisher/source URL | Not documented/verified | 2022-11-01–2022-11-29 | 7,501 |
| [oman_land_transactions_dec_2022.xlsx](data/raw/manual/oman_land_transactions_dec_2022.xlsx) | Unverified; registry URL fields are null | User-declared Ministry attribution; no embedded publisher/source URL | Not documented/verified | 2022-12-04–2022-12-29 | 5,667 |
| [oman_land_transactions_oct_2024.xlsx](data/raw/manual/oman_land_transactions_oct_2024.xlsx) | Unverified; registry URL fields are null | User-declared Ministry attribution; no embedded publisher/source URL | Not documented/verified | 2024-10-01–2024-10-31 | 6,024 |

“Unverified” does not mean that the publisher or source does not exist. “Licence not documented” does not establish either permission or prohibition; it means permission cannot be confirmed from the evidence reviewed.

## Evidence and review method

1. Read the original files through the existing [read-only Excel reader](src/excel_reader.py). Inspect all six worksheets, source headers, embedded metadata, ZIP core properties and external relationship targets. The three land sheets incorrectly declare `A1`; iteration bounds are reset **in memory**, without saving a workbook.
2. Count nonempty data rows after each actual header and read the transaction/procedure dates from the contents, not filenames. Recompute per-month occurrence counts and dates with/without rows.
3. Recompute each original SHA-256 and compare it with [the upload registry](docs/uploaded_source_registry.json) and the same file in upload commit `6a461443f3522349ec9b827c8761e2672c605816`.
4. Reconcile scope, geography and counts through the checksum-verified [audited bundle](data/processed/audited/71008482abd46aa7f0bc/manifest.json), [EDA manifest](data/processed/eda/168665c92a8a2ff91598/analysis_manifest.json) and [duplicate audit](reports/DUPLICATE_AUDIT.md). The dashboard's pinned input loader verifies the originals and derivative inputs before returning tables.
5. Review [source documentation](docs/data_sources.md), [the discovery catalogue](docs/source_catalog.json) and [the acquisition register](docs/acquisition_manifest.json). Catalogue leads and earlier failed retrieval attempts are not download receipts for these four uploads.

**Online verification limit:** the current environment's enforced network policy does not allow the relevant Omani government hosts. Earlier official-source acquisition returned proxy HTTP 403. Those blocked URLs were **not retried**. A new official-domain search attempt returned a tool error, so it provided no new source evidence. No current HTTP response, licence text or official-file match is claimed in this report. This access limitation does not prove a source is unavailable publicly.

No dataset-specific publisher URL was found in the workbook metadata or external relationships. The Muscat workbook contains a Ministry-domain contact email, not a dataset URL. The land workbooks have no additional metadata sheets or external source links. Technical metadata and hashes establish local integrity and traceability, not publisher authentication or complete market coverage.

### Existing official-source investigation leads

These are **previously recorded provider entry points**, not verified original URLs for any of these four files:

| Existing lead | What the evidence supports | What it does not establish |
|---|---|---|
| [MOHUP real estate transaction catalogue](https://mohup.gov.om/en/open-data/data/Realestate%20Transaction) | Registry/discovery lead for Ministry transaction resources | The exact November/December 2022 or October 2024 export, its revision, checksum, publication date or licence |
| [National Open Data Portal](https://opendata.gov.om/en) | Registry lead for regional brokerage resources | The Muscat workbook's exact dataset page or original binary |
| [MOHUP terms-of-use lead](https://webapps.housing.gov.om/opendata/en/pages/TermsofUse.aspx) | A terms URL recorded in the earlier discovery catalogue; its resource applicability remains pending | A verified licence grant covering any current upload |

The previously documented **NCSI** site licence cannot automatically be assigned to these **MOHUP-attributed** files. Likewise, a quarterly Ministry PDF, a January 2026 NCSI XLSX, or a portal's related-resource listing does not identify the source of these particular row-level uploads. No new URL has been constructed or guessed.

## File-by-file findings

### 1. Muscat brokerage registrations, 2025

- **Local file / dataset ID:** `muscat_brokerage_sales_2025.xlsx` / `muscat_brokerage_2025`.
- **Evidence:** worksheet `البيانات الوصفية ` names the group `تسجيل عقد بيع من خلال مكاتب الوساطة العقارية-محافظة مسقط 2025`; its source field says `منصة وزارة الإسكان والتخطيط العمراني`. A contact address uses `housing.gov.om`. Worksheet `المتغيرات ` explains the procedure date, wilayat, property use and property description. These statements are verified **inside the uploaded file**; official-host origin remains unverified.
- **Original official URL / licence:** neither is documented or independently verified. The portal homepage is only a discovery lead.
- **Actual data sheet:** `تسجيل عقد بيع - مسقط`, five columns, header row 3, **9,366** nonempty data rows from Excel row 4 onward. The metadata's total of 9,366 reconciles with the rows, but does not prove annual completeness.
- **Observed period:** January–September 2025, dated **January 2 through September 30**. There are **181 distinct procedure dates**. All nine supplied months contain rows; October–December 2025 are absent from this file.
- **Geography:** Muscat governorate only, with six observed wilayat labels: السيب, العامرات, بوشر, قريات, مسقط, مطرح. No observations for the other ten governorates are supplied by this workbook; they are outside its declared scope, not national zeros.
- **Definition:** sale-contract registrations through brokerage offices. These are a separate administrative population from the Ministry land files. No reliable official record/transaction ID, price, property area, financial amount or price index is supplied.
- **Metadata inconsistency:** periodicity is labelled annual and reference year 2025, but the rows stop in September. The publication field says **2025-07-12**, before some recorded procedures. The metadata modification field is blank. The ZIP core creation date is 2015-06-05 and modification date is 2025-12-04; these are file/template properties, not verified release dates. Neither the annual label nor the local filename establishes a complete year.
- **Repetition limit:** 6,778 occurrences repeat after the first under full-original-row equality; 8,174 occur in repeated groups. With no reliable transaction identifier, this does not confirm duplicate economic transactions. All rows remain included.

| Supplied month | Source occurrences | Distinct dates with rows |
|---|---:|---:|
| 2025-01 | 857 | 19 |
| 2025-02 | 1,147 | 20 |
| 2025-03 | 819 | 19 |
| 2025-04 | 880 | 19 |
| 2025-05 | 1,207 | 21 |
| 2025-06 | 816 | 18 |
| 2025-07 | 1,277 | 23 |
| 2025-08 | 1,141 | 21 |
| 2025-09 | 1,222 | 21 |
| **Total** | **9,366** | **181** |

These are supplied-record counts, not an annual sales series. Dates without rows, including January 1, cannot be classified as zero activity or export omissions without the publisher's reporting calendar and completeness statement.

### 2. Land BuySell records, November 2022

- **Local file / dataset ID:** `oman_land_transactions_nov_2022.xlsx` / `land_nov_2022`.
- **Provenance:** user-declared Ministry upload. The `BuySell` sheet and field layout are consistent with the recorded transaction-resource lead, but schema similarity is not official provenance. No embedded publisher statement, dataset URL or resource licence was found.
- **Actual sheet:** `BuySell`, eleven columns, header row 1; **7,501** data rows. Declared worksheet size `A1` recovers to **7,502 × 11**, including the header, in memory.
- **Observed period:** **2022-11-01–2022-11-29**, with **22 distinct dates**. November days **4, 5, 12, 18, 19, 25, 26, 30** have no supplied rows. This is a monthly extract, not evidence of complete daily capture. Other 2022 months are not in this file; December is supplied separately, leaving January–October absent from the comparable 2022 collection.
- **Geography:** all eleven modern governorates represented after the documented legacy Sharqiyah mapping; **62 observed wilayat keys/labels**, including one nonstandard الساحل الشرقي occurrence in Dhofar. This is not proof of a complete official wilayat inventory.
- **Available attributes:** source date, buyer type, region, wilayat, village, gender fields and number of owners. No property-use/type, financial amount, area, price index or reliable transaction ID is provided. Owner count is not transaction volume.
- **Publication:** no verified publication date. ZIP core creation time `2023-01-03T09:03:28Z` and creator `Apache POI` describe the export/software, not an authenticated publisher or release date.
- **Other limits:** 38 English wilayat labels and 65 English village labels are missing. Full-row equality flags 2,629 repetitions after first and 3,675 occurrences in repeated groups; no automatic deletion is justified by attribute equality alone.

### 3. Land BuySell records, December 2022

- **Local file / dataset ID:** `oman_land_transactions_dec_2022.xlsx` / `land_dec_2022`.
- **Provenance / licence:** user-declared Ministry attribution only; exact official source and applicable licence remain unverified. No embedded publisher statement or resource URL was found.
- **Actual sheet:** `BuySell`, the same eleven-column layout as November, header row 1; **5,667** data rows. `A1` recovers to **5,668 × 11**, including the header, without saving the original.
- **Observed period:** **2022-12-04–2022-12-29**, with **20 distinct dates**. December days **1, 2, 3, 9, 10, 16, 17, 23, 24, 30, 31** have no supplied rows. No other month is contained in this file. Together with November, the supplied comparable 2022 collection covers only two months.
- **Geography:** eleven modern governorates after the documented mapping; **61 observed wilayat keys/labels**, including one nonstandard الساحل الشرقي occurrence in Dhofar. Regional representation does not establish complete transaction capture within every region or wilayat.
- **Attributes / definitions:** same limitations as November: no property-use/type, monetary amount, area, index or reliable transaction ID. Shared schema permits limited November/December comparisons; source completeness and event identity remain unverified.
- **Publication:** no verified publication date; ZIP creation time `2023-01-03T09:10:40Z` / `Apache POI` is export metadata only.
- **Other limits:** 28 English wilayat labels and 27 English village labels are missing. Full-row equality flags 1,843 repetitions after first and 2,600 occurrences in repeated groups. All are retained.

### 4. Service-coded land records, October 2024

- **Local file / dataset ID:** `oman_land_transactions_oct_2024.xlsx` / `land_oct_2024`.
- **Provenance / licence:** user-declared Ministry attribution only; exact official dataset page, download URL and applicable licence remain unverified. There is no embedded publisher statement or resource URL.
- **Actual sheet:** `Sheet1`, fifteen columns, header row 1; **6,024** data rows. `A1` recovers to **6,025 × 15**, including the header, in memory.
- **Observed period:** **2024-10-01–2024-10-31**, with **23 distinct dates**. October days **4, 5, 11, 12, 18, 19, 25, 26** have no supplied rows. Matching the first and last calendar day does not prove a complete monthly export. January–September and November–December 2024 are absent from the collection.
- **Geography:** eleven modern governorates after the documented mapping; **63 observed wilayat keys/labels**. No nonstandard wilayat-label occurrence is flagged in this file; this still does not establish administrative or market completeness.
- **Definitions:** `SERVICE_SUB_ID` contains **RN13A: 599** and **RN13C: 5,425** occurrences. Their official meanings are unknown. Do not relabel them as sales, mortgages or other categories, or merge their totals with the 2022 BuySell population as one trend.
- **Amounts:** `RE_VALUE` is present in **5,657** rows and missing in **367**. Its unit and economic meaning are unverified. It is not established as OMR, a property price, turnover or a price index. No monetary conclusion or missing amount is generated.
- **Publication:** no verified publication date; ZIP creation time `2024-11-18T07:17:08Z` / `Apache POI` is export metadata only.
- **Other limits:** no reliable transaction ID or property area; 34 English wilayat and 77 English village labels are missing. There are no full-original-row repetitions, but 510 occurrences participate in exported-attribute projection-collision groups after private/source fields are omitted. This is not evidence of 510 duplicate transactions; absence of exact original repetitions is not proof of unique events. Birth-date/gender quality flags are documented in the existing audit; those private fields are not used to create financial findings.

## Geographic scope reconciled to the four files

The three land workbooks contain **ten original legacy region labels**, including combined Sharqiyah. The audited modern eleven-governorate view resolves North/South Ash Sharqiyah using observed wilayats and [the documented administrative references](docs/reference_geography.json). Administrative references establish the mapping, not the provenance or completeness of transaction records.

| Governorate | November 2022 land | December 2022 land | October 2024 land | Jan–Sep 2025 brokerage |
|---|---:|---:|---:|---:|
| Ad Dakhiliyah | 1,301 | 1,075 | 721 | — |
| Adh Dhahirah | 309 | 208 | 294 | — |
| Al Buraimi | 212 | 196 | 183 | — |
| Al Wusta | 105 | 294 | 109 | — |
| Dhofar | 871 | 432 | 513 | — |
| Musandam | 34 | 23 | 69 | — |
| Muscat | 960 | 734 | 1,099 | 9,366 |
| North Al Batinah | 954 | 760 | 1,143 | — |
| North Ash Sharqiyah | 1,300 | 706 | 379 | — |
| South Al Batinah | 1,053 | 909 | 1,083 | — |
| South Ash Sharqiyah | 402 | 330 | 431 | — |
| **File totals** | **7,501** | **5,667** | **6,024** | **9,366** |

“—” means outside this brokerage workbook's geographic scope, **not zero national activity**. Counts include retained repetitions and nonstandard labels. No row is added to achieve eleven-governorate coverage.

## Missing periods within the research window

| Year | What these four files supply | Missing/unavailable coverage in this collection |
|---|---|---|
| 2020 | None | All months; no historical market inference supported |
| 2021 | None | All months |
| 2022 | November and December BuySell records; eleven governorates observed | January–October of that comparable land scope |
| 2023 | None | All months |
| 2024 | October service-coded land records; eleven governorates observed | January–September, November–December of that scope |
| 2025 | January–September brokerage registrations; Muscat only | October–December brokerage; no other-governorate or nationwide land-transaction series supplied for 2025 |
| 2026 | None | January–September not supplied; October is an incomplete current month as of this review; November–December are future periods |

The years/months in this table are **coverage metadata**, not additional observations. Absent data do not mean zero transactions. Unobserved daily dates cannot be distinguished from weekends, office closures, no qualifying records or incomplete exports with the available evidence; no explanation is assumed. All 2025 months are historical by this review, so the absent final quarter is a genuine collection gap, not a future-period placeholder.

## Integrity, authority and analytical use

| Question | Conclusion |
|---|---|
| Are the current originals unchanged since the recorded upload? | **Yes:** all four match registry SHA-256 and original Git blobs. |
| Are the record dates, counts and represented locations inspectable? | **Yes:** independently re-read and reconciled with pinned derivatives. |
| Is an exact government-host download authenticated for these bytes? | **No:** no verified resource URL, retrieval receipt or official-file match is available. |
| Is Ministry attribution present inside a file? | **Yes, Muscat only.** The three land-file attributions are user-declared. |
| Is redistribution permission documented for these four files? | **Not established.** No applicable resource licence is verified. |
| Do all eleven governorates appear in each supplied land month? | **Yes in the documented modern mapping.** This does not prove complete regional capture. |
| Are source occurrences verified unique transactions? | **No.** Reliable official record/event IDs are absent. |
| Are continuous 2020–2026 market trends or property prices supported? | **No.** Coverage, definitions and verified monetary/price indicators are insufficient. |

Limited descriptive analysis remains supported **within each supplied, consistently defined cohort/period**. The 2022 BuySell layout, 2024 service-coded layout and Muscat brokerage population must remain separate. A checksum-validated, correctly parsed dataset can still have unresolved provenance, licensing and completeness.

### Source SHA-256 inventory

| Dataset ID | SHA-256 |
|---|---|
| `muscat_brokerage_2025` | `f00cabf8a4084644321dda07061167e69030091300ba8fadf3ab5eccc7c857ca` |
| `land_nov_2022` | `80b8c39857e6379b72960342574feb721b55007e1d95bcd37db7f473768edf8a` |
| `land_dec_2022` | `fd52d06d8a678597f1cb437cea8510777ac379886e9aa640c955cf0ee0389202` |
| `land_oct_2024` | `df278f485f7d66bab0376c38c468d4f2fad2f88a4923fd9aaa7d2e0f2af1848c` |

## Evidence still needed

For **each** workbook, obtain its exact official dataset page and downloadable resource identifier, publication/revision metadata, access date, original filename and applicable licence/terms with the scope of reuse. When official access is available, compare the retrieved original to the recorded checksum; if the publisher has repackaged or revised it, document the version/content relationship rather than assuming either a match or a forgery. No such retrieval is claimed here.

Separately confirm the publisher's completeness/reporting calendar, transaction/event grain, unique identifier, the annual-versus-partial Muscat metadata, RN13A/RN13C definitions and `RE_VALUE` unit/meaning. Obtain complete comparable monthly series and actual official price-index/area data before attempting historical or pricing analysis. An official source page alone would not resolve every one of these independent gaps.

## Validation and preservation

Fresh read-only verification re-read all four originals and all six worksheets, recovered the three dimension errors in memory, reconciled the dates/counts/geography, verified the pinned dashboard inputs, and matched all four original Git-upload blobs. No workbook was saved and no data or dashboard implementation was changed.

Relevant automated checks:

```bash
python -m pytest tests/test_uploaded_audit.py tests/test_duplicate_audit.py tests/test_eda.py tests/test_dashboard.py -q
```

**Result: 57 passed**, with 14 existing Matplotlib/Pyparsing deprecation warnings; no failed or skipped tests. The selected modules cover the original workbooks and dimension recovery, lineage and record counts, duplicate interpretation, EDA reconciliation and dashboard views. All four original checksums were verified again after the tests.

`git diff` against the baseline is empty for the data, source code, entry point, notebook, reports, existing documentation, requirements and Streamlit/CI configuration. **Only this new report is added.** Technical validation does not resolve the external source/licence gaps identified above.
