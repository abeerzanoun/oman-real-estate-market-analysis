# Build the report in Power BI Desktop

## 1. Verify the local clone

Use a current supported 64-bit Power BI Desktop on Windows, a local checkout containing the committed data files (not only GitHub web previews), and the project's Python 3.12 environment. No Power BI Service connection or public deployment is needed.

From the repository root, run:

```powershell
python -m powerbi.prepare_package --check
python -m pytest tests powerbi/tests
```

Both commands must pass. The first checks the original workbook hashes, completed duplicate audit, parent audit artifacts and all EDA CSV hashes through the existing reviewed loaders. It then verifies all imported types, grains, keys, relationships, coverage reconciliation, measure bindings and generated artifacts. It does not refresh a PBIX.

Optional development syntax check (Node 22+):

```powershell
npm ci --prefix powerbi --ignore-scripts
npm --prefix powerbi run validate:m
```

This is a parser check, not a Power Query engine run. Do not change data files to make a check pass.

## 2. Start a blank Import report

In Desktop Options for the current file, disable **Auto date/time** and **automatic relationship detection/import** before loading tables. Start with an empty model; an existing dashboard model may contain automatic or alternative row-level relationships. Do not mark `dim_period` as a date table.

In Transform data → New source → Blank query → Advanced Editor:

1. Paste `m/pRepositoryRoot.pq` and name the query **pRepositoryRoot**. Edit its value to the absolute local repository path, for example `"C:\Projects\oman-real-estate-market-analysis"`. Backslashes in M are literal; do not double them. The source directory is appended by the reader. Disable load for this parameter if Desktop offers that option.
2. Create **fnAuditedCsv** from `m/fnAuditedCsv.pq`; it is a function and is not loaded as a table.
3. For each of the following 16 queries, create a blank query, paste the matching `.pq`, and set the query name exactly to its file stem. Enable load for all 16 tables. The query names are model names used by DAX.

| Role | Queries |
|---|---|
| Aggregate facts | fact_land_2022, fact_land_2024, fact_brokerage_2025 |
| Shared dimensions | dim_dataset, dim_period, dim_governorate, dim_wilayat |
| Land attributes | dim_buyer_type, dim_ownership_band, dim_service_code |
| Brokerage attributes | dim_property_use, dim_property_description |
| Disconnected metadata | coverage_matrix_2020_2026, dataset_summary, data_quality_summary, source_column_quality |

The reader pins the reviewed run directory, uses comma/UTF-8 65001/QuoteStyle.Csv, preserves Arabic and quoted line breaks, checks ordered headers, converts only reviewed types, fails on conversion errors, checks physical row counts and reconciles fact weights. Empty nullable cells remain null; integer tokens such as `5657.0` become exactly 5657, while fractional counts fail. Text values are not globally trimmed, translated or normalized again.

The M reader **does not verify SHA-256**. Always run the Python preflight immediately before refreshing an unchanged local folder; a same-shape/same-total data substitution might otherwise pass M checks. No automatic Replace errors, Fill down, Replace null with zero, Remove duplicates or automatic Changed Type steps should be added. Folder privacy can be set to Private; these queries read local files only.

Close & Apply. Check 361 / 257 / 403 rows in the three facts. Conversion, schema or reconciliation errors must be investigated, not suppressed. Check every type against [SCHEMA.md](SCHEMA.md), particularly text keys, Int64 counts, boolean flags, metadata dates and null monetary-unit fields.

## 3. Configure relationships and presentation metadata

In Model view, create **exactly 19** relationships from [RELATIONSHIPS.csv](RELATIONSHIPS.csv): `from_table[from_column]` is the **1** side, `to_table[to_column]` the **many** side; active, single-direction dimension → fact. Verify them after import; the CSV and Python do not install them in Desktop.

Never link `dim_governorate` to `dim_wilayat`, dimensions to each other, or facts to each other. Keep all four metadata tables disconnected. Do not add automatic links based on their matching `dataset_id`/`governorate_id` headers. No bidirectional/many-to-many relationships are needed.

Set default summarization to **Do not summarize** for columns, including numeric metadata. Only explicit DAX measures should aggregate fact weights. Hide all fact key columns, numeric metric columns and technical flags from report authors after setting up visual-level filters; leave dimension labels visible. Also hide `dim_wilayat[governorate_id]` and the metadata totals in `dim_dataset` to discourage accidental aggregations. Keep them for lineage checks.

Sort `dim_period[period_label]` by `dim_period[period_id]`. The five ownership labels already sort in the intended 1, 2, 3, 4, 5+ order. Leave service codes and source Arabic labels literal. Do not assign Currency/OMR or create a currency measure: monetary units are unknown and no monetary field exists in these facts.

## 4. Create the 17 measures

Use Modeling → New measure. Paste **one named definition at a time** from [EDA_MEASURES.dax](EDA_MEASURES.dax), including its `Name =` line. A `.dax` file with multiple definitions cannot be pasted into one measure editor. Create the three base count measures first, then remaining measures in file order; all dependencies appear earlier in the file.

Use [MEASURE_CATALOG.csv](MEASURE_CATALOG.csv) for exact home table and format. Count/difference formats are integers; share/change measures return fractions and use `0.00%`. The metadata column `repeated_group_share_pct` is already on a 0–100 scale: display it as Decimal Number with a “%” column label, **not** Power BI percentage format. Do not create a generic fact total or price measure.

The four fixed Nov/Dec comparison measures deliberately clear dataset and period filters; they keep geography, buyer and ownership filters. Use them only in the labelled 2022 section. They can still return 2022 values under a 2024/2025 dataset selection; this is documented behavior, not a cross-period comparison. Geographic shares clear both geographic dimensions while preserving the source/period/attribute cohort. Full details: [MEASURES.md](MEASURES.md).

## 5. Build and validate six pages

Import `report_theme.json` through View → Themes → Browse for themes. Create the pages and field bindings in [REPORT_SPECIFICATION.md](REPORT_SPECIFICATION.md). Use native visuals, no custom geography or fabricated coordinates. Add persistent subtitles describing the actual supplied windows and count semantics. Build navigation buttons and a reset bookmark per page; save it with the specified default selections.

Executive Overview intentionally has no shared dataset/period slicers. Coverage and quality use **their own metadata fields** because the tables are disconnected. The Land Transactions page has two separately scoped panels, not a union fact or common period trend. Review Edit interactions as specified so service filters never appear to affect the 2022 panel.

In DAX query view, open each of the nine `validation/desktop_*.dax` files, run **one file at a time**, and require every `Pass` to be TRUE. These queries test all 17 measures under representative default, scope, missing-period, blank and conflicting-geography contexts. Results expected to be blank must remain blank; zero is a different result. The larger Python reference CSV covers all 131 tested contexts; it is QA evidence, not an import table.

Also inspect `USERELATIONSHIP`/unexpected active paths if Desktop results differ; do not change the expected values to hide a relationship error. Complete [DESKTOP_ACCEPTANCE.md](DESKTOP_ACCEPTANCE.md) with actual Desktop version, date, refresh result and exported acceptance query results. Inspect Arabic rendering, totals, titles, filters and blank cells manually.

Only after those checks pass, save the actual report locally as `powerbi/Oman_Real_Estate_Audited.pbix`. This name is a proposed future artifact, not an existing file. A working PBIX, theme rendering and Power BI engine execution have **not** been validated by this package. Do not publish automatically.

## 6. Refresh or change input versions

For the existing version, repeat preflight → Desktop refresh → acceptance queries → visual checklist. Keep originals unchanged. The coverage snapshot is fixed at 2026-10-13 and does not change when Desktop refreshes.

New uploads require provenance/licence review, the existing audit/duplicate/EDA pipeline, reconciliation, a new reviewed pin in the project configuration and `model_contract.json`, and an intentional matching reader-path update. Regenerate/check the package and M syntax report, review every diff, rerun tests, then rerun Desktop acceptance. Never silently select the newest folder, append a second run, or overwrite an immutable processed run.
