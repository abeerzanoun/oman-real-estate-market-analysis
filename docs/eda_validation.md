# EDA validation — 2026-10-13 (Asia/Muscat)

Base latest main: `2c4237a5ec24e01b3dde13f2b0ac518b92437db3`, containing merged PR #4; feature branch `feature/scoped-exploratory-analysis`. Analysis run: `168665c92a8a2ff91598`. Locked Python 3.12.14 environment. Two pinned presentation dependencies (arabic-reshaper 3.0.0, python-bidi 0.6.7) added; existing dependency versions unchanged.

| Check | Executed result |
|---|---|
| Git ancestry and committed PR4 audit outputs | PASS, explicit main fetch, merged audit commit verified |
| Original and pinned input SHA-256 | PASS, four XLSX originals and all fourteen audit artifacts unchanged |
| Current offline upload audit | PASS, 28,558 rows, no aggregate inputs/errors; its fourteen artifact hashes exactly equal the pinned run |
| Full EDA `python -m src.run_eda` | PASS, 31 analytical CSVs, 14 PNG + 14 SVG figures, computed findings |
| Executed Jupyter notebook | PASS, seven code cells, fourteen embedded figures, no cell errors |
| Land 2022 fact reconciliation | 361 monthly aggregate rows represent 13,168 source occurrences (7,501 + 5,667) |
| Land Oct 2024 fact reconciliation | 257 monthly aggregate rows represent 6,024 source occurrences |
| Muscat brokerage fact reconciliation | 403 monthly aggregate rows represent 9,366 source occurrences |
| Coverage and share checks | PASS, 42 actual governorate-month cells, 12 observed months, denominators reconcile, shares sum to 100 within cohorts |
| Dimensional integrity | PASS, unique dimension keys, matched foreign keys, distinct scopes and separate category definitions |
| Monetary/data-gap safeguards | PASS, no monetary/demographic analytical fact fields, unknown service meanings retained, missing coverage counts stay null |
| Repeated execution | PASS, byte-identical CSVs/figures/manifests; changed immutable output rejected |
| Full `python -m pytest -q` | **85 passed**, 14 existing Matplotlib/Pyparsing deprecation warnings; 19.88 seconds |
| Python/import environment validation | PASS, Python 3.12 and thirteen required imports |
| `python -m pip check` | PASS, no broken requirements |
| `git diff --check` | PASS; exact CSV bytes preserved by Git attributes |

Original workbooks and the merged PR4 audit directory were not modified. The current audit rerun receives a new run ID because the dependency-lock fingerprint includes presentation additions; all actual audit artifacts/source hashes match. That redundant validation copy was retained in ignored scratch work rather than duplicating the historical audit in this PR.

Initial notebook execution in the isolated sandbox could not establish Jupyter's local kernel connections. A real Python 3.12 kernel check and the complete notebook then succeeded with the required execution permissions. No remote data retrieval was performed. Writable Matplotlib/IPython cache paths are documented. Pip only reported an unwritable default cache and disabled caching; dependency checks passed.

Tests cover real-source baselines, protected inputs, scope/comparison restrictions, observed-only periods, aggregation/repeated-group preservation, shares, category labels, all model relationships, generated PNG/SVG/hash integrity, reproducibility, immutable output refusal and the executed notebook. No synthetic market fixtures were introduced.

Charts were visually inspected for layout, common 2022 axes, coverage semantics and Arabic readability. Suggested DAX and the dashboard specification were reviewed against the table grains, but **not executed in Power BI Desktop**. No PBIX or deployed dashboard is claimed. CI regenerates the notebook and analytical bundle before running tests.

The EDA is meaningful for supplied-record geography, categories and the documented two-month comparison. It does not establish continuous 2020–2026 trends, complete-market volumes, independently unique transactions, monetary values/prices or investment returns. Exact official workbook URLs/licences, land publication dates, service definitions and RE_VALUE units remain pending.


## Portability correction verified after the first Actions attempt

The initial GitHub Actions attempt passed imports, dependencies and original/input validation, then stopped at the immutable analytical bundle check. A portability bug used filesystem listing order in figure-hash serialization; the local listing was reverse creation order and is not guaranteed on another filesystem. Artifact names and JSON keys are now sorted. Native rendering inputs (Python patch, OS/architecture/libc, FreeType, zlib and exact font bytes) are recorded in the run fingerprint; environments may have distinct figure bytes without changing analytical results.

All 31 analytical CSV hashes are independently pinned in the reviewed configuration and must match across rendering environments. The new executed run verifies every hash. An integration test deliberately reverses the figure directory listing and requires identical regenerated bundle bytes. Different statistical outputs still fail closed; no original or historical PR4 audit artifact is overwritten. The corrected Actions result is available in PR #5 checks.
