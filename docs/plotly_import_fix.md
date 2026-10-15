# Plotly Express import and Python 3.14.8 runtime investigation

Investigated October 15, 2026, from main `9506df7` (merged PR #8).

## Findings and limits

The reported failure occurs at `import plotly.express` in
`src/dashboard_charts.py`. The final missing-module name and complete traceback
were not supplied. That import location alone cannot identify the missing module:
Express also imports NumPy and its Narwhals dataframe adapter. The exact remote
`ModuleNotFoundError` remains unconfirmed.

On main, `plotly==6.0.1` was **already declared** in root `requirements.txt`.
The dependency file is at the same level as `streamlit_app.py`; no alternative
recognized dependency manifest takes precedence. Express, its adapter, the chart
module and the entry point import successfully in the existing clean Python 3.12
runtime. There is no evidence that a separate `plotly-express` distribution is
needed; Express is part of Plotly itself.

The verified deployment mismatch is that the owner still uses Python **3.14.8**,
while the old root pins are Pandas **2.2.3** and NumPy **2.2.3**, which lack CPython
3.14 wheels. In a newly created **actual Python 3.14.8** environment, the old
requirements fail uv installation with `--no-build`: Pandas has no usable wheel.
This intentionally excludes source builds; it does not reproduce the exact Cloud
exception or prove that Pandas was the module named in that exception. A failed
installation, stale runtime or nested missing module can all lead to an import
failure; the final traceback line is needed to distinguish them remotely.

## Fix

| Dependency | Python 3.12 runtime | Python 3.14 runtime |
|---|---|---|
| Pandas | 2.2.3, unchanged | 2.3.3 |
| NumPy | 2.2.3, unchanged | 2.3.5 |
| Plotly Express | `plotly[express]==6.0.1` | Same |
| Narwhals adapter | 2.27.1, the existing analysis-lock version | Same |
| Streamlit | 1.65.0, unchanged | Same |

PEP 508 markers choose the numerical pins according to the interpreter.
[Pandas 2.3.3 release files](https://pypi.org/pypi/pandas/2.3.3/json) and
[NumPy 2.3.5 release files](https://pypi.org/pypi/numpy/2.3.5/json) publish CPython
3.14 Linux x86_64 wheels. Both installed successfully with source builds disabled.
`plotly[express]` explicitly requests Express's NumPy dependency, and Narwhals is
pinned directly to the already-validated adapter version. This makes the dependency
contract explicit; it is not a claim that the Cloud traceback named Narwhals.

Only the numerical runtime pins change on 3.14. The full Python 3.12 analysis
`requirements-lock.txt`, `.python-version`, dashboard implementation, features,
original XLSX files, processed CSVs, notebook, figures and audit outputs are
unchanged. No dataset is regenerated or rewritten. Full analysis tools continue
to target Python 3.12; Python 3.14 support here is for the dashboard runtime.

## Executed verification

Fresh isolated environments were created with **Python 3.12.14** and **3.14.8**.
In each:

```bash
uv pip install --python PATH_TO_ENV_PYTHON --no-build -r requirements.txt
uv pip check --python PATH_TO_ENV_PYTHON
PATH_TO_ENV_PYTHON tests/check_dashboard_runtime.py
```

Both installs resolve 39 packages entirely from wheels, and compatibility checks
pass. The runtime checker passes on both versions:

- Direct imports of `plotly.express`, `narwhals.stable.v1`,
  `src.dashboard_charts` and `streamlit_app`.
- Reconciliation against the pinned canonical governorate counts for every dataset
  and supplied month, preserving 13,168 land-2022, 6,024 land-2024 and 9,366 brokerage
  source occurrences.
- Plotly monthly/ranked chart construction and JSON serialization from the real
  data, with plotted count totals reconciled to their cohort.
- All six Streamlit pages render without exceptions/errors.
- A November 2022 land filter produces the same KPI as the pinned source summary.

The full local Python 3.12 suite passes **118 tests**, with 14 existing
Matplotlib/Pyparsing deprecation warnings; its dependency check also passes.
A real local server running Python **3.14.8** passes all six pages in Chromium
at desktop 1440×1000, touch landscape 1280×800 and Android-style portrait 800×1280
sizes: **18 page/viewport checks**, including rendered charts, no JavaScript or
Streamlit exceptions, and no page/main horizontal overflow. This is viewport
emulation, not a physical Android device test.

CI runs the runtime checker on a Python **3.12/3.14 matrix**, plus the existing
Python 3.12 full environment, audit, EDA and Pytest job. GitHub Actions outcomes
are recorded in the pull request. Neither import success nor occurrence counts
establish verified unique transactions.

## After merging

1. Verify the Cloud app still targets this repository, branch `main` and
   `streamlit_app.py`; ensure the build uses the newly merged commit.
2. Allow requirements to rebuild. Python **3.14.8 can remain selected** with the
   new requirements. Reboot the app if Cloud is still serving an old environment;
   changing interpreters or deleting the deployment is not required for this fix.
3. Confirm the build installs Pandas 2.3.3, NumPy 2.3.5, Plotly 6.0.1, Narwhals
   2.27.1 and Streamlit 1.65.0 on Python 3.14. Check all six pages.
4. If an import still fails, capture the **exact final missing-module name** and
   nearby traceback frames plus the preceding installer errors. Do not infer that
   Plotly itself is absent merely because its Express import starts the traceback.

No Cloud settings, deployment, merge or data files are changed by this PR.
