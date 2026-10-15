# Validation evidence and limits

`validation/validation_results.json` is generated from real pinned inputs. It records 16 imported tables, 19 relationships, 17 measures, 131 filter contexts and **2,227 passing source-row/reference comparisons**. `validation/measure_test_vectors.csv` contains the complete comparison evidence. Its filter scenarios are QA metadata, not real estate observations or a new dataset to import.

Input checks use the existing fail-closed loaders to verify four original workbook hashes, parent audit manifest/artifacts, all 31 EDA CSVs and completed duplicate-audit evidence. The import contract additionally checks exact CSV headers/field counts, explicit types/nullability, physical rows, positive integral aggregate weights, complete aggregate grains, matched unique dimension keys, geographic consistency, per-source subtotals and observed coverage reconciliation. The original files and all existing processed CSVs are read only.

The limited DAX parser binds every measure and numeric SUM input. The reference evaluator executes the parsed definitions in the documented single-direction model, comparing them with independent arithmetic on audited occurrence rows. All actual dimension values are included; additional cases cover scope, combined filters, empty selection, missing months and incompatible geography. [MEASURES.md](MEASURES.md) describes the semantics and scope of that validation. This is not execution by Microsoft's DAX engine.

`validation/m_syntax_results.json` records hashes and passing syntax results for all **18 M files**, parsed using Microsoft's `@microsoft/powerquery-parser` **0.19.0**, locked in `package-lock.json`. The parser validates syntax; it does not resolve Power Query library names, access Windows paths or run queries. The helper's null/type/count guards still require an actual Desktop refresh. The theme is JSON, not an imported/rendered theme until Desktop tests it.

## Re-run

```bash
python -m powerbi.prepare_package --check
python -m pytest tests powerbi/tests
npm ci --prefix powerbi --ignore-scripts
npm --prefix powerbi run validate:m
python -m pip check
```

The package tests reject modified CSV bytes, orphaned keys, duplicate dimension keys, unsupported relationship direction, unknown DAX columns/functions, SUM of text, and fractional/missing required integer tokens. Regression checks also cover full-source counts versus aggregate rows, retained zero/blank distinction, comparison filter clearing, geographic denominators, immutable originals and byte-for-byte generated-output reproduction. They alter only in-memory copies/temporary files for negative tests and do not export fake records.

Local validation in Python 3.12.14: **133 tests passed**, including 15 package tests; 14 existing Matplotlib/Pyparsing deprecation warnings were reported by the EDA figure test. The package preflight, 2,227 reference comparisons, 18-query Microsoft M syntax check, Python environment validation and `pip check` passed. CI runs these checks alongside the existing Python 3.12/3.14 dashboard runtime checks; remote workflow status is recorded in the PR.

## Pending

Microsoft Power Query evaluation, VertiPaq/DAX execution, Desktop relationships, CSV engine collation behavior, six-page layout, theme rendering, filters and Arabic text rendering have **not** been tested in Power BI Desktop. No PBIX was created and no report was deployed. Run the nine `validation/desktop_*.dax` queries and complete [DESKTOP_ACCEPTANCE.md](DESKTOP_ACCEPTANCE.md) after following [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md). Expected Desktop test results are specifications until actually observed.
