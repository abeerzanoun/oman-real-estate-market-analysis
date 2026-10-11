# Oman Real Estate Market Analysis (2020–2026)

## Project overview

A professional, reproducible analytics portfolio project investigating the Sultanate of Oman's real estate market using real, verified public data. Python, Excel and Power BI will support analysis and communication. The 2020–2026 window is a research target: actual coverage will follow reliable source availability, and incomplete 2026 periods will be labelled explicitly.

## Business problem

Developers, investors and business decision-makers need comparable evidence on transaction activity, regional demand and price indicators. Differences in definitions, reporting frequencies and historical coverage must be resolved before drawing conclusions or identifying potential investment opportunities.

## Research objectives and questions

- Track market evolution: how has the Omani market evolved between 2020 and 2026?
- Measure activity: how have transaction values and volumes changed over time?
- Compare regions: which governorates have the highest market activity?
- Study pricing: how do price indicators differ across locations and property categories?
- Identify patterns: what trends and potential investment opportunities emerge from verified evidence?
- Support decisions: what actionable insights can help developers, investors and business decision-makers?

## Planned methodology

1. Verify official sources, licences, definitions and historical coverage; build a provenance register.
2. Acquire immutable originals, record checksums and metadata, and approve a source-backed data dictionary.
3. Implement reproducible cleaning, geography/category harmonization and quality checks with tests.
4. Analyze comparable periods, transaction scopes, regional activity and price indices; document missingness and revisions.
5. Produce documented notebooks, charts, Excel outputs and a Power BI model/dashboard.
6. Communicate evidence-backed findings, limitations and business recommendations.

Separate sales from mortgages and other registrations. Do not combine national totals with regional components, sum overlapping cumulative series, infer missing observations, or equate average transaction values with property price indices. No synthetic market data or fabricated findings are used.

## Technology stack

Python **3.12**, Pandas, NumPy, Matplotlib, Seaborn, Plotly, Jupyter/JupyterLab, openpyxl and XlsxWriter for Excel exchange, Microsoft Excel, Power BI Desktop, Git/GitHub and Pytest. OpenAI Codex assists project implementation. Excel and Power BI are separate desktop applications, not pip dependencies.

## Repository structure

```text
oman-real-estate-market-analysis/
├── data/
│   ├── raw/.gitkeep
│   └── processed/.gitkeep
├── notebooks/.gitkeep
├── src/
│   ├── __init__.py
│   └── validate_environment.py
├── reports/
│   └── figures/.gitkeep
├── powerbi/.gitkeep
├── docs/
│   ├── data_sources.md
│   ├── data_dictionary.md
│   └── setup_validation.md
├── tests/
│   └── test_environment.py
├── .gitignore
├── .python-version
├── pytest.ini
├── README.md
├── requirements.txt
└── requirements-lock.txt
```

## Setup and execution

From a clone of this repository, use Python 3.12 and an isolated environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m src.validate_environment
python -m pytest
python -m pip check
jupyter lab
```

On Windows, create the environment with `py -3.12 -m venv .venv`, then activate it in PowerShell using `.venv\Scripts\Activate.ps1`. Execute remaining commands from the repository root.

`requirements.txt` pins direct dependencies; `requirements-lock.txt` records the full validated resolution. To deliberately refresh dependencies, install direct requirements in a fresh Python 3.12 environment, run all checks, then regenerate the lock with `python -m pip freeze > requirements-lock.txt` and review changes. The initial lock is validated on Linux/Python 3.12; validate other operating systems separately. The validator checks Python and all required imports and returns a nonzero exit code on failure. Tests cover actual imports and failure handling. Validation does not certify future data or dashboard correctness.

Install Microsoft Excel separately as needed and Power BI Desktop on a supported Windows machine. Future processed UTF-8 CSV or XLSX exports will feed these tools with documented types, units and keys. Notebooks and dashboards are intentionally pending acquisition.

## Data source strategy

Prioritize NCSI, the Ministry of Housing and Urban Planning and Oman official data portals. See [source register](docs/data_sources.md) for verified pages and unresolved dataset questions, and [proposed dictionary](docs/data_dictionary.md) for candidate variables. No dataset has yet been accepted. Raw and processed data are ignored by default pending provenance, size and redistribution review; `.gitkeep` preserves their directories.

## Expected deliverables

A verified source inventory and dictionary; reproducible Python preparation and analysis; documented Jupyter notebooks; static and interactive figures; Excel analysis exports; Power BI model/dashboard; a business report with traceable recommendations and limitations; automated data and pipeline tests as implementation progresses.

## Current project status

**Infrastructure setup.** Repository organization, dependency specifications, environment validation, tests and preliminary documentation are prepared. No data collection, exploratory analysis, figures, dashboard or market findings have been produced. See [setup validation](docs/setup_validation.md) for executed checks and remaining requirements. Main-branch integration is subject to review; this setup does not merge changes automatically.
