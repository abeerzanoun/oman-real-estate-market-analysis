# Oman Real Estate Observatory — Streamlit dashboard

A read-only, six-page interface over the reviewed official-upload derivatives. The
dashboard uses merged PRs #4–#6 and is developed from main commit `82566ae`.
No original workbooks or existing processed outputs are changed. No public
deployment, hosting configuration, automatic deployment workflow or merge is performed.

## Start locally

From the repository root, using Python **3.12**:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m src.validate_environment
python -m pip check
python -m pytest -q
streamlit run streamlit_app.py --server.address 127.0.0.1
```

Windows PowerShell activation: `.venv\Scripts\Activate.ps1`. Open
`http://127.0.0.1:8501` in a desktop browser. The command above binds locally to
loopback; the shared configuration leaves the address to the hosting platform and
disables usage telemetry. There is no runtime source download,
API credential requirement, data upload, data editing or data regeneration.
`requirements.txt` pins the dashboard runtime for Community Cloud, including
`plotly[express]` and its validated Narwhals adapter. It selects the original
Pandas/NumPy pins on Python 3.12 and wheel-compatible pins on Python 3.14.
`requirements-analysis.txt` includes the runtime plus the original notebook,
analysis, Excel and test tools. `requirements-lock.txt` preserves the full validated
Python 3.12 environment for analysis and tests; its pins are unchanged.

To run only the dashboard in a clean Python 3.12 environment, install
`requirements.txt` instead of the full lock, then use the local Streamlit command
above. The full-project validator and Pytest require the analysis environment.

For a tablet on the **same trusted local network**, explicitly bind the local
machine's private LAN address:

```bash
streamlit run streamlit_app.py --server.address YOUR_PRIVATE_LAN_IP
```

Open `http://YOUR_PRIVATE_LAN_IP:8501` in Android Chrome. Replace the placeholder
with the host's actual private address; allow that port through the local firewall
if needed. This does not publish a public site. Use the top-left sidebar control
for navigation on smaller screens; rotate the tablet for wider comparison tables.
Charts support touch hover, and tables have their own horizontal scrolling.

## Streamlit Community Cloud deployment and recovery

For the owner's existing deployment, use repository
`abeerzanoun/oman-real-estate-market-analysis`, branch **`main`** and entry point
**`streamlit_app.py`**. Dashboard runtime checks now cover both Python **3.12.14**
and **3.14.8**. Full analysis/notebook reproduction still requires Python **3.12**;
the full lock and `.python-version` remain unchanged.

An existing Python 3.14.8 deployment can stay on that interpreter after merging
the conditional runtime dependency fix. Let Cloud rebuild requirements, then
reboot the app if it continues using a stale environment. Verify successful
dependency installation and all six pages. No deployment deletion is required
merely to use the new compatible requirements. See
[Plotly Express investigation and recovery](plotly_import_fix.md).

For a new deployment, select Python explicitly through **Advanced settings →
Python version**. If you independently choose to change an existing app's Python
version, Streamlit's [Python-version instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/upgrade-python)
require recreating that Cloud deployment; retain its settings first.
`.python-version` does not switch an existing Cloud interpreter. No `runtime.txt`
workaround is added. This dashboard currently requires no secrets.

Community Cloud installs the root `requirements.txt`; it does **not** automatically
use `requirements-analysis.txt` or `requirements-lock.txt`. Its documented attempt
to install with **uv** is normal. The runtime file deliberately excludes notebook,
static-plot, Excel and test packages that the dashboard does not import. Preserve
the pinned data/report directories listed below. The shared config no longer
forces a localhost-only address; the local command sets it explicitly, and Cloud
can apply its own address/port settings. Real secrets, if later introduced, belong
outside Git; `.streamlit/secrets.toml` is ignored.

If startup still fails, retain the final `ModuleNotFoundError: No module named
'…'` line and nearby traceback frames, or the first package-specific installer
exception. An import line alone does not reveal whether Plotly, NumPy, Pandas or
an internal dependency is missing. The earlier [Python 3.12 recovery report](streamlit_cloud_fix.md)
documents the previous deployment limitation, before 3.14 runtime support was added.

No remote deployment, deletion or merge is performed by this fix. The source
redistribution licences retain their unresolved documented status.

## Pages and filters

| Page | Purpose and interpretation |
|---|---|
| Executive Overview | Three separate cohort cards, plus one-cohort/one-month geographic snapshot. No combined national market total. |
| Land Market Analysis | Select 2022 BuySell or 2024 service-coded data; filter supplied months, governorates, wilayats, buyer type and owner-count bands. 2024 adds literal service code and ownership mode filters. |
| Muscat Brokerage Analysis | January–September 2025 registrations only, with month, wilayat, land-use and property-description filters. |
| Governorate and Wilayat Comparisons | One cohort and one month at a time, ranked governorates, observed wilayat labels and a complete comparison table. |
| Data Coverage and Quality | 2020–2026 availability metadata, actual date ranges, source-column missingness and the completed duplicate audit. |
| Sources and Methodology | Workbook checksums, attribution evidence, unresolved resource URLs/licences and interpretation rules. |

Governorate labels are bilingual from the reviewed dimensions. Wilayat and
property-category names retain the Arabic source labels. English translations
are not guessed. Filters are independent for each page/cohort. A cleared month,
governorate or attribute selection returns an explicit empty state. The optional
wilayat filter uses an empty selection to mean all available labels; its choices
are pruned when parent filters change. Every page states its applied months and
cohort. Geography/categories in multi-month land or brokerage views are pooled
over the selected supplied months only. Shares use **all filtered occurrences**,
including wilayat labels outside the top-15 chart.

## Data and transformations

`docs/dashboard_config.json` pins the EDA and duplicate-audit manifests by SHA-256.
`src/dashboard_data.py` verifies the following on **every rerun**, without a stale
integrity cache:

1. Four original XLSX files against the reviewed EDA manifest.
2. The pinned audited manifest and its fourteen EDA input artifacts.
3. All 31 reviewed EDA CSVs.
4. The duplicate-audit manifest, JSON report and dataset summary used by the app.
5. Complete audit status and source-count reconciliation.

Changed/missing bytes stop the dashboard with an explicit error. To adopt new data,
run and review a new source audit, duplicate audit and EDA; then intentionally update
the dashboard pins. The app does not automatically select a later directory.

| Pinned aggregate fact | Physical CSV rows | Source occurrences | Supplied periods |
|---|---:|---:|---|
| `fact_land_2022.csv` | 361 | 13,168 | November 2022: 7,501; December 2022: 5,667 |
| `fact_land_2024.csv` | 257 | 6,024 | October 2024 |
| `fact_brokerage_2025.csv` | 403 | 9,366 | January–September 2025, Muscat only |

Inputs are under `data/processed/eda/168665c92a8a2ff91598/`; provenance is in
`data/processed/audited/71008482abd46aa7f0bc/`, and duplicate evidence in
`reports/duplicates/4162ac42cfdaebd9d962/`.

Dimension joins use validated many-to-one relationships. All KPI/chart counts
sum `reported_record_count`, never the aggregate CSV row count. CSV downloads
retain aggregate grain, count semantics, cohort ID and EDA version, use UTF-8 BOM,
and contain no birth dates, gender, village identifiers or financial values.
No download is written into `data/processed/` automatically.

## Integrity and interpretation rules

- **Occurrence ≠ unique transaction.** No reliable official transaction/record IDs
  exist. Repeated attributes remain included; zero confirmed duplicate imports
  does not imply zero duplicate economic transactions. The actual latter count is
  unknown. `records_in_repeated_groups` describes membership in full-original-row
  equality groups in the original cohort, not a removal flag or a repetition rate
  recalculated after filtering.
- The 2024 exported payload has 510 occurrences in projection-collision groups
  although no full-source rows repeat. Private fields omitted from analytical
  exports explain these attribute collisions; do not drop them as duplicates.
- The two 2022 land months share a source schema. The 2024 service-coded schema
  differs, and RN13A/RN13C meanings are unverified. Brokerage registrations are a
  separate population. These definitions are never combined into one market total.
- Only supplied month bars are plotted, with a categorical month axis. Isolated
  land months and the partial brokerage year do not become continuous annual trends.
- All eleven governorates appear in each supplied land month; brokerage covers
  Muscat only. Observed wilayat labels are not a complete administrative inventory.
  Two occurrences with the nonstandard source label الساحل الشرقي remain included.
- Coverage cells are **metadata**, with unavailable counts blank, not zero. The
  availability matrix is fixed to the October 13, 2026 audit cutoff; future status
  does not move automatically with the current clock.
- RE_VALUE units/meaning, exact dataset URLs and redistribution licences remain
  unresolved. No monetary conclusions, prices, national demand or investment
  returns are calculated. Embedded brokerage attribution and user-attributed land
  provenance are displayed with their actual evidence strength.

## Tests and browser verification

`tests/test_dashboard.py` tests real weighted totals, filtering, empty states,
category counts, observed periods, safe downloads, missing coverage, checksum
rejection, all six pages and interactive Streamlit reruns. Run the full repository
suite with `python -m pytest -q`; CI installs the lock file and reproduces the
existing audit/EDA in addition to those tests.

In a clean runtime-only environment, run `python tests/check_dashboard_runtime.py`.
This explicitly imports Express, its adapter, the chart module and the entry point;
reconciles real geographic counts; serializes the real-data charts; renders all six
pages; and verifies a filtered KPI. CI runs it on both Python 3.12 and 3.14.

Optional real-browser checks use Playwright and a locally installed Chromium:

```bash
python -m pip install playwright==1.58.0
streamlit run streamlit_app.py
python tests/browser_check_dashboard.py --browser /usr/bin/chromium
```

This separate browser tool is not a dashboard runtime dependency. The checker
visits all six pages at desktop, tablet landscape and Android-like portrait
viewports, detects rendered errors/page-level horizontal overflow, checks visible
charts, and saves screenshots under ignored `work/dashboard-browser/`. Viewport
emulation does not constitute testing on physical Android hardware. See
`docs/dashboard_validation.md` for actual executed results.
