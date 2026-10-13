# Exploratory analysis methodology

## Objective and admissible questions

Describe the geography and recorded attributes in the uploaded files, compare the two same-layout 2022 snapshots, and prepare transparent analytical outputs for Python/Power BI. The project title's 2020–2026 window is a research target; coverage comes from actual record dates. No missing period is filled, no national continuous series is constructed, and no monetary conclusion is calculated.

| Research question | Supported now | Important boundary |
|---|---|---|
| Where are reported records concentrated? | Governorate and observed-wilayat distributions within Nov/Dec 2022, Oct 2024; six Muscat wilayats in brokerage | Uploaded occurrences, not proven complete-market activity or unique sales |
| How do monthly counts differ? | Same BuySell layout: Nov versus Dec 2022; nine Muscat brokerage months described separately | No annual/YoY trend, long-run growth or seasonality inference |
| Which categories are recorded? | Original buyer type and owner-count bands; original brokerage registration category, use and description; literal 2024 service codes | RN13 meanings remain unknown; use and description are separate fields |
| How do financial values/prices differ? | Not supported | RE_VALUE unit/meaning unknown; no areas, price index or verified OMR field |
| What investment opportunities follow? | Identify priorities for verification and further investigation | No investment recommendation, return forecast or causal demand conclusion |

## Reproduce the project

Use Python 3.12, an isolated environment, and the repository root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
export MPLCONFIGDIR=/tmp/oman-mpl
export XDG_CACHE_HOME=/tmp/oman-cache
export IPYTHONDIR=/tmp/oman-ipy
python -m src.validate_environment
python -m pip check
python -m src.validate_uploads
python -m src.run_eda
python -m pytest
```

On Windows use the existing README's environment activation instructions and writable cache locations appropriate to Windows. Jupyter kernel execution needs permission to open local loopback connections. It does not download data; if a sandbox restricts kernel sockets, allow local notebook execution. `--no-notebook` generates tables/figures without launching a kernel, but the delivered notebook is actually executed and tested.

`run_eda` reads only the pinned audited run in `docs/eda_config.json`, not the most recently named folder. Its input manifest SHA, every listed artifact SHA and all four original workbook SHAs are checked before transformations. PR #4 was verified as an ancestor of latest main `2c4237a5ec24e01b3dde13f2b0ac518b92437db3` before branching. The input audit run is unchanged even though presentation dependencies were added; immutable historical manifests retain their original implementation/lock fingerprints. A current audit rerun may therefore have a new run ID, without changing the pinned input data.

## Scope, grain and provenance

| Family | Source IDs | Actual periods | Rows | Definition retained |
|---|---|---|---:|---|
| 2022 land | land_nov_2022, land_dec_2022 | 2022-11, 2022-12 | 13,168 | BuySell worksheet layout, service subtype not supplied |
| 2024 land | land_oct_2024 | 2024-10 | 6,024 | Service-coded layout, RN13A/RN13C meanings unverified |
| Muscat brokerage | muscat_brokerage_2025 | 2025-01–2025-09 | 9,366 | Brokerage-office sale-contract registrations, Muscat only |

The metric is **reported record occurrences**: every retained data row. Generated lineage IDs identify source file/sheet/row, not unique real estate transactions. All repeated visible rows remain. No owner sum, unique-signature count or summed cross-family total is used as a market KPI. The total 28,558 appears only as input/output reconciliation and project coverage.

The source registry records original filenames, SHA-256, uploaded commit and provider attribution. Muscat explicitly attributes MOHUP; the land files are user-attributed official uploads with exact resource URLs/licences pending. Local bytes/periods are validated, but authenticity, complete coverage and economic definitions are not independently established. `docs/data_sources.md` and `docs/uploaded_source_registry.json` distinguish verified source pages from exact-workbook provenance gaps. No blocked official download is retried by EDA.

## Transformations and analytical rules

1. Load immutable, hash-verified audit CSVs. Parse transaction_date strictly as ISO and validate year/month consistency. Add period_id from that date; only observed months become period dimension rows.
2. Use the audited governorate/wilayat mapping. Preserve documented legacy Sharqiyah resolution by actual wilayat, including Sinaw. Raw names remain in the audit crosswalk. The source label الساحل الشرقي is flagged; its two records remain in Dhofar totals/facts and are excluded only from standard-wilayat ranking figures. No geographic boundary, centroid, missing translation or administrative coverage is invented.
3. Group source occurrences with pandas `groupby(..., dropna=False, observed=True)`. Only observed groups become fact/summary rows. Missing source values are not guessed. Owner bands derive from actual positive integers: 1, 2, 3, 4, 5+; no owner count is used as a transaction multiplier.
4. Governorate shares use that dataset/month's row total as denominator. Wilayat tables provide both that denominator and within-governorate shares. Brokerage all-period category shares use the nine supplied months only; monthly shares use their own month. Each denominator is exported explicitly. Counts are integers; share fields are percentages on a 0–100 scale.
5. Governorate ranks use descending counts with tied counts sharing the minimum rank. Top-ten wilayat charts sort descending counts, then original label deterministically; all observed labels remain in the full table. The two same-layout 2022 count panels use common axes. No sample uncertainty interval, statistical significance or causal model is justified by these source files.
6. Compute the explicit 2022 comparison only when both supplied months and all eleven governorates are present. Row difference = December − November; row change (%) = difference / November × 100. Geographic share change is December share − November share, in **percentage points**. These describe file composition, not verified market contraction/appreciation. No comparison pairs 2022 with 2024 or either land family with brokerage.
7. Export three separate observed monthly fact tables. Grouping reduces their physical rows, not the number of reported source occurrences. Sum the exported count field; do not count physical fact rows. Repeated-group occurrence counts provide quality context and do not authorize deduplication.
8. Keep RE_VALUE as a string when reading audited facts; never aggregate it in EDA. Analytical facts exclude monetary fields entirely. Literal service codes are displayed without economic interpretation. Birth date/gender are excluded, as in the audit.
9. Plot with Matplotlib/Seaborn: ranked bars, share changes, attribute breakdowns, monthly brokerage bars, observed wilayat/month heatmaps and availability grids. Arabic reshaping/bidi processing affects display strings only. PNG and SVG figures use deterministic metadata/style; no mapping geometry is manufactured.
10. Generate findings from computed tables and execute the documented notebook in the same Python interpreter. No forecasts, synthetic rows, arbitrary outlier removal or year-end extrapolation is included.

## Coverage, outputs and reproducibility

Coverage matrix cells are **metadata**, not market observations. The 2,772-cell grid spans three scopes × seven years × twelve months × eleven governorates; only 42 cells have observed counts. Unavailable/out-of-scope/future counts remain blank, never zero market activity. Presence does not establish monthly completeness. The observed-period dimension contains only 12 distinct months; it is not a complete calendar for time intelligence.

The EDA run ID fingerprints its pinned input manifest, analysis/figure/notebook/orchestration code, configuration and locked dependencies. Summary/fact/dimension CSVs go to `data/processed/eda/<run_id>/`; PNG/SVG go to `reports/figures/eda/<run_id>/`; computed findings go to `reports/eda/<run_id>/insights.md`. `analysis_manifest.json` contains original/input/implementation/output hashes, table counts and fact reconciliation. Identical reruns must match bytes; changed existing derived outputs are rejected rather than overwritten.

The generated notebook is `notebooks/01_scoped_real_estate_eda.ipynb`, with seven actually executed code cells and fourteen embedded figures. Its generated marker permits refresh; a handwritten notebook is protected. The notebook regenerates/validates the same analytical bundle when run, so stale code/input fingerprints trigger a regeneration instruction. Commit the notebook, manifest, tables and figures together. A future reviewed code/source change creates a new immutable run; keep historical runs until a deliberate archival decision.

## Interpretation limits and next evidence

Counts may reflect registration/owner-record processes, not unique complete-market sales. Source URLs/licences, land publication dates, transaction identity, complete capture, service definitions and RE_VALUE units need official confirmation. Muscat's publication label precedes some records and its annual label does not establish a complete year. No uploaded 2020, 2021, 2023 or 2026 observations exist.

Population, property stock, comparable full monthly series, authoritative boundary data, areas and price indices are absent; no per-capita rates, price-per-area, liquidity, causality, returns or investment scores are calculated. Collect and reconcile those official inputs before expanding interpretation. Current findings support scoped descriptive reporting and identifying follow-up questions, not a full historical market/investment study.
