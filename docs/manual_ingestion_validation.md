# Manual ingestion setup validation

Executed 2026-10-12 using Linux/Python 3.12.14 and the locked environment.

| Check | Result |
|---|---|
| Pytest | PASS — 61 tests; 14 existing upstream deprecation warnings |
| Environment validator | PASS — Python 3.12 and all 11 imports |
| pip dependency consistency | PASS — no broken requirements |
| Python compilation | PASS |
| Workflow YAML / embedded Python parsing | PASS |
| Git whitespace checks | PASS |
| Empty manual folder run | EXPECTED — exit 2, awaiting_official_files, zero observations, ready=false |

The 41 added test cases cover bilingual governorate reference labels, header mappings/ambiguity, explicit units and periods, immutable originals and outputs, XLSX sheet selection, CSV ingestion, wide-year conversion with preserved cell lineage, equal duplicates/conflicts, missing source values, index-base and licence requirements, and geographic presence rules. Tests use the existing attributed genuine NCSI national excerpt, empty/header-only technical files and deliberate corruption checks. No invented governorate market observations or sample data files are shipped.

No actual official workbook or CSV has been uploaded to `data/raw/manual/`. Consequently, no production analytical files, full regional import, Power BI model or market findings have been validated. The current status explicitly reports zero imported files/observations and false readiness. The source registry and automated collectors are preserved; blocked URLs were not retried.

After actual uploads arrive, review source/licence evidence, inspect the real sheets and headers, complete sidecars, run ingestion, reconcile values and all-11 coverage against originals, and inspect Power BI types/relationships before claiming readiness. Tests verify safeguards, not the authenticity or completeness of yet-unprovided files.
