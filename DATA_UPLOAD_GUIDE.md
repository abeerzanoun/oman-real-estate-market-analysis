# Official Excel and CSV upload guide

The manual workflow is prepared; **no official XLSX/CSV has been imported**. No analytical dataset is ready. Use actual publisher downloads, not invented records, copied newspaper figures, screenshots converted to Excel, or the repository's test excerpt.

## What real files to provide

| Priority | Official data needed | Required content | Coverage requirement |
|---|---|---|---|
| 1 — market activity | MOHUP or NCSI aggregate real estate transaction tables in original XLSX or official CSV export | Governorate; year/month/quarter or exact interval; separately defined sales contract counts and sales values; mortgages/barter if provided; exact monetary scale | One table with all 11 governorates, or matching official files for each governorate, for each available reporting period |
| 2 — prices | NCSI official property-price index tables in XLSX or official CSV export | Governorate, property category, reporting quarter, index points, official base period, release/provisional status | All 11 governorates where the official series supports them. The inspected NCSI regional breakdown is **residential land**, not every property category |
| 3 — optional context | Official land-plot or building-permit exports | Governorate, period, land-use/property classification, count and publisher definitions | Keep these in separate scopes; they do not measure property sales |

Do not require a fabricated full 2020–2026 series. Provide only periods published by the authority; identify gaps. A national-only transaction table can document national activity but **cannot** satisfy the all-governorate requirement. Individual transaction files need a dedicated adapter; this workflow processes reviewed aggregate tables and will reject transaction-level declarations.

The governorates are Muscat (مسقط), Dhofar (ظفار), Musandam (مسندم), Al Buraimi (البريمي), Ad Dakhiliyah (الداخلية), North Al Batinah (شمال الباطنة), South Al Batinah (جنوب الباطنة), North Ash Sharqiyah (شمال الشرقية), South Ash Sharqiyah (جنوب الشرقية), Adh Dhahirah (الظاهرة), and Al Wusta (الوسطى). Legacy combined Batinah/Sharqiyah labels must not be split or guessed.

## Where to obtain official files

These are known official entry points from the existing source register; **no new download links or complete XLSX coverage are asserted**:

1. [NCSI publications](https://www.ncsi.gov.om/publications): locate Monthly Statistical Bulletin, Statistical Year Book, and Real Estate Price Inflation/Index publications for the needed periods. Choose the publisher's Excel download where offered. Inspect the actual worksheets: national activity is not regional activity, and price tables may mix weights, index points and percent changes.
2. [MOHUP real estate open-data page](https://mohup.gov.om/en/open-data/data/Realestate%20Transaction): look for official transaction exports and regional aggregate tables. Its indexed monthly land-sale resources do not establish all-property coverage or an aggregate table format. Use original files and include their definitions.
3. [Oman National Open Data Portal](https://opendata.gov.om/en): filter publisher Ministry of Housing and Urban Planning and search real estate/sale contract registrations. Regional brokerage-registration resources are leads for 2025, not confirmed complete-market data. Gather all available governorates for the same dataset definition and period; missing resources remain gaps.
4. [NCSI Oman Data Portal — Housing](https://data.gov.om/OMHSNG2016/housing?lang=en): official CSV/XLSX export options are listed for land-use, plots and building permits. Use these only as context unless the selected indicator explicitly measures transactions.

If an official Excel version is not offered, record that limitation; do not rename a PDF to `.xlsx` or construct a substitute workbook. The current registry does not confirm a single downloadable transaction workbook covering all 11 governorates for every year.

## Preserve the originals and record the source

Keep the downloaded bytes and filename unchanged. Separate different releases into subfolders under `data/raw/manual/` rather than replace an earlier file. Do not edit, clean, combine or resave the original in Excel.

For each upload, provide the actual dataset title, publisher, exact official landing/download URL, publication date if known, your download timestamp with timezone, reporting periods, units/scale, geographic scope, table definitions and licence URL. Unknown publication dates remain null. Include any provisional/revision notes.

You may upload these details as a plain source note beside each file, named `<original filename>.source.md`, or supply them in chat after uploading. I can inspect the actual workbook and prepare its machine-readable metadata; you do **not** need to guess column mappings. Upload only files whose verified licence permits redistribution in the repository. `.gitignore` exceptions permit XLSX/CSV, metadata and source notes in this dedicated folder; other raw collections remain unchanged.

## Upload through GitHub

1. Open [the repository](https://github.com/abeerzanoun/oman-real-estate-market-analysis) and select the `feature/manual-excel-ingestion` branch while this workflow is under review. After it is merged, create a separate data-upload branch from main.
2. Navigate to `data/raw/manual/`, select **Add file → Upload files**, and choose the original XLSX/CSV plus source notes.
3. Use a separate subfolder for each release if filenames repeat. Retain originals and add a new release rather than replace an existing upload.
4. Commit with a message identifying the real publisher and reporting period. Keep uploads on the feature/data-upload branch for review; do not commit directly to main.
5. Send the branch or pull-request link here. I will import the files from the connected repository and configure mappings from the actual tables.

GitHub browser uploads have a **25 MiB per-file** limit. Use Git/GitHub Desktop for larger originals or coordinate a separate transfer; do not split or modify source data solely to fit the browser limit. See [GitHub's file-upload documentation](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository).

## Configuration after actual files exist

From the repository root with the project's Python 3.12 environment:

```bash
python -m src.manual_ingestion inspect
python -m src.manual_ingestion init --file "data/raw/manual/<actual original filename>"
```

`init` creates `<original filename>.metadata.json` containing the actual SHA-256, null provenance fields, a pending review and **no data records**. It refuses to overwrite an existing sidecar. Complete the required fields using actual source evidence; see [metadata contract](docs/manual_ingestion.md). Do not mark a source reviewed or licence permitted merely because its filename sounds official.

Each selected table needs an exact sheet name for XLSX, a 1-based header row, semantic scope, declared aggregate grain, explicit units/metric definitions and period information. CSV encoding/delimiter and numeric separators can be configured. Header aliases cover common English/Arabic labels; explicit mappings handle other labels. Wide year/governorate columns can be unpivoted only when selected explicitly. Multiple sheets/files/datasets are supported.

## Run and review

```bash
python -m src.manual_ingestion run
python -m pytest
```

The workflow makes no network requests and currently accepts input files up to 50 MiB. Larger sources require an adjusted processing plan; preserve them unchanged. It validates metadata, original hashes, dates, numerical values, geography and table structure. It removes identical aggregate observations while retaining all original-cell provenance. Conflicting values or invalid rows stop publication; source blanks remain missing and are counted in the report.

Valid imports create a new immutable run folder under `data/processed/manual/` with `observations.csv`, `provenance.csv`, `coverage.csv` and `validation_report.json`. Reruns never overwrite changed results. Originals remain untouched.

Exit codes: **0** = actual imports passed the all-11 coverage gate; **1** = validation failed; **2** = no files or incomplete coverage. `docs/manual_ingestion_status.json` records the current result. The gate checks each governorate-level indicator/period/category/scope group, not just a union of names across unrelated datasets. Missing metric values also prevent a ready flag. It does not certify full 2020–2026 historical completeness or authenticate a file independently of its documented manual review.

For Power BI, load the actual run's CSVs only after reviewing the report. Use ISO dates, text geography IDs and `observation_id` to relate provenance to observations. Parse numeric values with the configured decimal convention; select count versus OMR versus index using `unit`. Never sum indices or overlapping monthly/cumulative/annual periods. The original decimal text is retained so precision is not silently rounded.
