# Power BI reporting package — audited uploaded data

This package prepares a six-page **Import mode** report from the reviewed EDA aggregates derived from the four uploaded workbooks. It includes reproducible Power Query imports, a verified schema and relationship list, DAX definitions, a theme, page specifications and acceptance queries. **No `.pbix` has been created or validated.** Microsoft engine execution and visual acceptance remain pending in Power BI Desktop on Windows.

Start with [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md), then [REPORT_SPECIFICATION.md](REPORT_SPECIFICATION.md). Read [COVERAGE_AND_LIMITATIONS.md](COVERAGE_AND_LIMITATIONS.md) before interpreting a visual.

| Population | Supplied period | Aggregate fact rows | Retained source occurrences |
|---|---|---:|---:|
| Land BuySell layout | Nov–Dec 2022 | 361 | 13,168 |
| Land service-coded layout | Oct 2024 | 257 | 6,024 |
| Muscat brokerage registrations | Jan–Sep 2025 | 403 | 9,366 |

These populations have different definitions. Display their counts separately; never add them into a national sales KPI. Physical aggregate rows are not transaction counts. None of the source files contains a reliable official event identifier, so these are **source record occurrences**, not verified unique transactions. Full-source equality groups remain retained and are not confirmed economic duplicates.

## Package navigation

| File / directory | Purpose |
|---|---|
| [model_contract.json](model_contract.json) | Reviewed immutable input paths, hashes, exact ordered columns, explicit types/nullability, grains and 19 relationships |
| [SCHEMA.md](SCHEMA.md) | Generated column-level data dictionary for all 16 imported tables |
| [RELATIONSHIPS.csv](RELATIONSHIPS.csv) | Exact 1:* active, single-direction relationship configuration |
| [m/](m/) | One root parameter, a strict CSV reader and 16 named import queries |
| [EDA_MEASURES.dax](EDA_MEASURES.dax) | 17 named measures; create each separately in Desktop |
| [MEASURE_CATALOG.csv](MEASURE_CATALOG.csv) / [MEASURES.md](MEASURES.md) | Home tables, formats, filter behavior, interpretation and validation limits |
| [report_theme.json](report_theme.json) | Navy/teal/amber presentation theme; Desktop rendering pending |
| [REPORT_SPECIFICATION.md](REPORT_SPECIFICATION.md) | Six page layouts with field bindings, filters, interactions and acceptance criteria |
| [prepare_package.py](prepare_package.py) / [dax_reference.py](dax_reference.py) | Read-only input validation, reproducible artifacts, limited DAX reference interpreter and independent source-row oracle |
| [validate_m.cjs](validate_m.cjs), package.json, package-lock.json | Pinned Microsoft Power Query parser; development-only syntax validation |
| [validation/](validation/) | Reproducible results, 2,227 measure/context checks and nine Desktop acceptance queries |
| [VALIDATION.md](VALIDATION.md) / [DESKTOP_ACCEPTANCE.md](DESKTOP_ACCEPTANCE.md) | Checks performed here and the separate outstanding Microsoft engine / visual checklist |
| [tests/](tests/) | Real-input model, integrity, filter, blank and reproducibility regression tests |

## Reproduce from the repository root

Use the existing locked Python 3.12 environment; [project setup](../README.md#setup-and-execution) remains applicable. Node 22+ is needed only for M syntax checks.

```bash
python -m pip install -r requirements-lock.txt
python -m powerbi.prepare_package --check
python -m pytest tests powerbi/tests
npm ci --prefix powerbi --ignore-scripts
npm --prefix powerbi run validate:m
```

To deliberately regenerate the package after reviewing an implementation change:

```bash
python -m powerbi.prepare_package
node powerbi/validate_m.cjs
python -m powerbi.prepare_package --check
```

The generator writes only its enumerated outputs under `powerbi/`; it does not collect data, edit CSVs/workbooks, impute, deduplicate, execute Power BI, or publish anything. It verifies the existing source/processed manifests and completed duplicate audit before generating files. There is no “latest folder” discovery. A new data version requires an explicit reviewed contract/configuration update, not a folder swap.

## Model choice and lineage

This package selects the **aggregate model** in [EDA_MODEL.md](EDA_MODEL.md). The [UPLOADED_DATA_MODEL.md](UPLOADED_DATA_MODEL.md) row-level model is an alternative, with `COUNTROWS` on its row facts. Here, use `SUM(reported_record_count)` on the three EDA facts. **Do not import both models or any additional count summary as an additive fact.**

Pinned EDA directory: `data/processed/eda/168665c92a8a2ff91598/`.
Audited parent: `data/processed/audited/71008482abd46aa7f0bc/`.
All four originals and every existing processed output remain unchanged.

File integrity and traceable local transformations do not prove official authenticity. Exact official resource URLs and redistribution licences remain unresolved for all four files. See [DATA_PROVENANCE_AUDIT.md](../DATA_PROVENANCE_AUDIT.md), [duplicate audit](../reports/DUPLICATE_AUDIT.md), and [uploaded source registry](../docs/uploaded_source_registry.json). Publication/redistribution review is outside this local report-build package.
