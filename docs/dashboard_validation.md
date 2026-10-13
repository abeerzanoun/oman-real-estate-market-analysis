# Executed dashboard validation

Validated on October 13, 2026, from latest main `82566ae88578cb79fdf788d7abe959748f2ea446`
(merged PR #6), using Linux, Python 3.12.14 and Streamlit 1.65.0.

| Check | Result |
|---|---|
| Python/version and all 14 required imports | PASS |
| `python -m pip check` | PASS; no broken requirements |
| Full `python -m pytest -q` | **118 passed**, including 21 new dashboard tests |
| Existing duplicate audit reproduction | PASS; 28,558 source occurrences; zero confirmed duplicate imports; zero removed |
| Existing upload validation | PASS; 28,558 source occurrences; zero aggregate errors |
| Existing EDA and executed notebook reproduction | PASS; all 31 CSVs match the reviewed baseline; 14 figures; 28,558 source occurrences |
| Original and committed processed-output preservation | PASS; `git diff origin/main -- data/raw data/processed notebooks reports/duplicates reports/eda reports/figures/eda` is empty |
| Local HTTP `/_stcore/health` | PASS (`ok`) |
| Six pages in Chromium, desktop 1440×1000 | PASS |
| Six pages in Chromium, touch landscape 1280×800 | PASS |
| Six pages in Chromium, Android user-agent/touch portrait 800×1280 | PASS |

The browser checker waits for the requested page heading, Streamlit's finished
script state and rendered Plotly SVGs. It checks JavaScript/render errors, chart
presence and page/main-content horizontal overflow, and captures chart/page
screenshots. Viewport/user-agent emulation is **not a physical Android hardware
test**. Other browsers and physical devices have not been tested.

Pytest emits 14 pre-existing Matplotlib/Pyparsing deprecation warnings. No test
fails or is skipped. Existing dependency versions are unchanged; Streamlit and
its additional dependencies are pinned in the updated lock file. Browser testing
uses optional Playwright 1.58.0 outside the runtime dependency lock.

Pipeline reproduction creates new immutable run IDs because the dependency lock
is part of the existing lineage fingerprint. These validation-only runs and the
regenerated notebook were retained under ignored `work/dashboard-pipeline-validation/`;
the prior committed outputs and notebook were preserved exactly. Dashboard inputs
remain pinned to audited `71008482abd46aa7f0bc`, EDA `168665c92a8a2ff91598` and
duplicate audit `4162ac42cfdaebd9d962`.

## Count reconciliation

| Cohort | Aggregate fact rows | Source occurrences | Supplied months |
|---|---:|---:|---|
| Land BuySell 2022 | 361 | 13,168 | 2022-11, 2022-12 |
| Land service-coded 2024 | 257 | 6,024 | 2024-10 |
| Muscat brokerage 2025 | 403 | 9,366 | 2025-01 through 2025-09 |

All counts are weighted source occurrences, not verified unique transactions.
Monetary analysis, annual trends and public deployment remain unsupported or
unauthorized. Exact official dataset resource URLs, licences, RN13 meanings and
RE_VALUE units retain their documented unresolved status.

GitHub Actions results are recorded in the dashboard pull request checks.
No merge or public deployment is performed.

Review screenshots: [desktop overview](../reports/figures/dashboard/desktop_overview.png)
and [brokerage chart at the tablet portrait viewport](../reports/figures/dashboard/tablet_brokerage_months.png).
