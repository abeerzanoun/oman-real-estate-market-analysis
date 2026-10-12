# Setup validation record

Executed 2026-10-11 in the connected Linux workspace with Python 3.12.14 and an isolated `.venv`.

| Check | Result |
|---|---|
| Install pinned direct dependencies | PASS after network-enabled execution |
| `python -m src.validate_environment` | PASS: Python 3.12 and all 11 required imports |
| `python -m pytest` | PASS: 4 tests; 14 upstream deprecation warnings |
| `python -m pip check` | PASS: no broken requirements |
| Python compilation of src/tests | PASS |
| `git diff --check` | PASS |

Validated direct versions: pandas 2.2.3, numpy 2.2.3, matplotlib 3.10.1, seaborn 0.13.2, plotly 6.0.1, jupyter 1.1.1, jupyterlab 4.3.6, ipykernel 6.29.5, openpyxl 3.1.5, xlsxwriter 3.2.2 and pytest 8.3.5. Full resolved dependency versions are in `requirements-lock.txt`.

## Observed limitations and remaining setup

- Initial sandboxed Git/PyPI commands could not reach the proxy. Network-enabled execution succeeded; repository history was fetched and installation completed.
- The read-only home directory produced pip/font-cache warnings. Validation used writable `MPLCONFIGDIR` directories under `/tmp`. A fontconfig cache warning remained, without import or test failure. On a similarly restricted host, set writable `MPLCONFIGDIR` and `XDG_CACHE_HOME` for analysis commands.
- Matplotlib 3.10.1 with the resolved Pyparsing version emits 14 deprecation warnings in the actual-import test. No warnings were suppressed; a future dependency refresh should review compatibility and rerun checks.
- Microsoft Excel and Power BI Desktop are not installed or validated in this Linux workspace. Configure them separately; Power BI Desktop needs supported Windows. No dashboard is created.
- The lock is validated on Linux/Python 3.12 only. Cross-platform installation, desktop exports and future data pipelines require their own checks.
- Source pages are documented, but no datasets, licences for particular files, full historical coverage or source schema have been accepted. There are no market findings.

## Next phase

Inspect official NCSI and MOHUP resource metadata, construct a 2020–2026 availability matrix, confirm transaction definitions, licence, units and reporting frequency, then acquire approved originals with checksums and provenance. Update the proposed dictionary from actual files before cleaning or analysis.
