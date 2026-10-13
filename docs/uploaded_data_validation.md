# Uploaded workbook validation — 2026-10-13

Python 3.12.14, locked dependencies. All checks executed locally; GitHub Actions runs the same imports, dependencies, tests and offline upload dispatcher.

| Check | Result |
|---|---|
| `python -m src.audit_uploaded_data` / `src.validate_uploads` | PASS, 28,558 retained occurrences, four originals, zero aggregate inputs/errors |
| Original SHA-256 before/after | All four match registered upload bytes |
| Worksheet inspection | Six sheets; three incorrect A1 dimensions recovered in memory |
| Actual record/date reconciliation | PASS, 9,366 + 7,501 + 5,667 + 6,024; all filenames match observed periods |
| Coverage summaries | 42 observed governorate-month cells; totals reconcile with 28,558 occurrences |
| Missing values / repetitions | Preserved; zero records removed |
| Output SHA-256 / repeated execution | All artifacts match manifest; identical run reuses byte-identical output |
| `python -m pytest -q` | 72 passed; 14 existing Matplotlib/Pyparsing deprecation warnings |
| `python -m src.validate_environment` | PASS, Python and all eleven required library imports |
| `python -m pip check` | PASS, no broken requirements |
| `git diff --check` | PASS |

Current committed output: [immutable audited run](../data/processed/audited/71008482abd46aa7f0bc/), [quality report](../reports/data_quality_report.md), [dictionary](uploaded_data_dictionary.md), [Power BI model](../powerbi/UPLOADED_DATA_MODEL.md).

The first environment invocation could not write Matplotlib/font caches to the read-only home directory and used a temporary cache; rerunning with `MPLCONFIGDIR=/tmp/oman-mpl XDG_CACHE_HOME=/tmp/oman-cache` passed cleanly. The final tests report dependency deprecation warnings, not validation failures.

Limitations are substantive source gaps, not silent validation errors: unknown exact official download URLs/licences, land-file publication dates, RE_VALUE units and RN13A/RN13C definitions, record identity and source completeness; sparse years/months. The source publication label in Muscat precedes some records. Future months and all absent coverage have blank counts; no observations were fabricated.

These exports are ready for constrained descriptive record analysis and Power BI import. The project is not ready for a comprehensive 2020–2026 market, price or investment study. No dashboard or unsupported market conclusions are included.
