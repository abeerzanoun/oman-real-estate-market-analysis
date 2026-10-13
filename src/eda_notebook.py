"""Build and execute the documented EDA notebook using this Python interpreter."""
from pathlib import Path
import hashlib
import os
import sys

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

from src.eda_figures import FIGURE_TITLES


def notebook_source(run_id):
    cells=[]
    def add(kind,source):
        cell=nbformat.v4.new_markdown_cell(source) if kind=='markdown' else nbformat.v4.new_code_cell(source)
        cell['id']='eda-'+hashlib.sha256(source.encode()).hexdigest()[:12]
        cells.append(cell)
    add('markdown', '''# Oman Real Estate Market Analysis
## Exploratory analysis of uploaded real estate records

**2022 land snapshots · October 2024 service-coded records · January–September 2025 Muscat brokerage**

A reproducible portfolio analysis of 28,558 uploaded source record occurrences. The 2020–2026 window is a coverage objective; the files do not constitute a continuous annual series. No prices, monetary conclusions or missing periods are inferred.

**Metric:** retained source rows, not independently identified transactions. Exact visible-row repeats remain because transaction IDs are absent.

**Navigate:** [provenance](#Provenance-and-reproducibility) · [coverage](#Coverage-before-comparison) · [2022-land](#Two-comparable-2022-land-snapshots) · [2024-land](#October-2024-service-coded-snapshot) · [attributes](#Buyer-type-and-ownership-attributes) · [Muscat](#Muscat-brokerage-registrations) · [interpretation](#Interpretation-and-next-actions).''')
    add('markdown', '''## Provenance and reproducibility

Latest base `main`: `2c4237a`, containing merged PR #4. Input audit run: `71008482abd46aa7f0bc`. Exact input manifest, artifacts and original workbook hashes are checked before analysis. Read `docs/eda_methodology.md`, `docs/data_sources.md` and `docs/uploaded_source_registry.json` for attribution and unresolved provenance.

Muscat has embedded MOHUP attribution; land workbook source URLs/licences remain pending. This analysis inherits those explicit limits. Three incorrect XLSX dimensions were repaired by the prior audit without resaving originals. Arabic shaping is used only for figure display; source labels and grouping keys remain unchanged.

Run from the repository root with `python -m src.run_eda`. Every displayed chart/table comes from the same generated run. Power BI uses separate monthly fact tables and shared observed dimensions; it must not sum the three definitions into one national sales measure.''')
    add('code', f'''from pathlib import Path
import sys
import pandas as pd
from IPython.display import display, Image, Markdown

ROOT = next((p for p in (Path.cwd(), *Path.cwd().parents)
             if (p / "docs/eda_config.json").is_file()), None)
if ROOT is None:
    raise RuntimeError("Open this notebook inside the repository")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.eda_analysis import load_inputs, summarize
from src.run_eda import run

analysis = run(execute_notebook=False)
assert analysis["run_id"] == "{run_id}", "Notebook/code changed: regenerate with python -m src.run_eda"
inputs = load_inputs()
tables = summarize(inputs)
FIGURES = ROOT / analysis["figures_directory"]
pd.set_option("display.max_columns", 20)
pd.set_option("display.width", 140)
pd.set_option("display.float_format", lambda x: f"{{x:,.2f}}")
def show_figure(name):
    display(Image(filename=str(FIGURES / (name + ".png")), width=1100))
display(tables["dataset_summary"])
print("Input hashes verified; record occurrences preserved; no monetary calculations.")''')
    add('markdown','''## Coverage before comparison

All eleven modern governorates are represented in each supplied land month after documented wilayat-based resolution of the combined Sharqiyah label. The brokerage file covers six Muscat wilayats only. Coverage is presence of uploaded records, not proof of full market capture. Grey chart cells are unavailable/outside scope, not zero activity. No uploaded 2020, 2021, 2023 or 2026 records exist.''')
    add('code','''show_figure("coverage_calendar")
show_figure("coverage_governorates")
display(tables["coverage_observed"])''')
    add('markdown','''## Two comparable 2022 land snapshots

November and December share the observed BuySell schema. Compare counts and composition within those two files; completeness and unique transaction identity remain unverified. Percentage points measure geographic share change; percentage changes describe row counts, not prices or annual market growth.

Wilayat charts rank only standard labels. Two source rows labelled الساحل الشرقي under Dhofar are retained in governorate totals and exported tables but excluded from wilayat ranking. Rankings cover observed labels and do not establish a complete administrative inventory.''')
    add('code','''show_figure("land_2022_governorates")
show_figure("land_2022_share_change")
show_figure("land_2022_wilayats")
display(tables["governorate_nov_dec_2022"].sort_values("november_records", ascending=False))''')
    add('markdown','''## October 2024 service-coded snapshot

Analyze this layout separately. RN13A and RN13C are verified as observed source codes; their meanings are unverified, so neither is relabelled as sales, mortgages or another transaction class. RE_VALUE units remain unverified and the analytical facts deliberately exclude amounts. Amount presence is a data-quality attribute only.''')
    add('code','''show_figure("land_2024_governorates")
show_figure("land_2024_wilayats")
show_figure("land_2024_service_codes")
display(tables["service_code_counts_2024"])
display(tables["data_quality_summary"])''')
    add('markdown','''## Buyer type and ownership attributes

Individual/Company are original source buyer labels. Owner bands are derived explicitly from NO_OF_OWNERS: 1, 2, 3, 4, or 5+ owners. Owner numbers are not a count of transactions, properties or buyers independently identified. Each panel describes its own supplied cohort.''')
    add('code','''show_figure("land_buyer_types")
show_figure("land_ownership_bands")
display(tables["buyer_type_counts"])
display(tables["ownership_counts"])''')
    add('markdown','''## Muscat brokerage registrations

Use the brokerage-office sale-contract registration scope separately. January–September contains nine supplied months; the source's annual label does not imply full-year data. Property-use labels and property descriptions are different classification fields. Their raw Arabic categories are retained and should not be conflated with national property supply, prices or demand estimates.''')
    add('code','''show_figure("muscat_monthly")
show_figure("muscat_wilayats")
show_figure("muscat_wilayat_monthly")
show_figure("muscat_property_categories")
display(tables["brokerage_monthly_counts"])
display(tables["brokerage_property_use"])
display(tables["brokerage_property_description"])
display(tables["brokerage_transaction_category"])''')
    add('markdown','''## Interpretation and next actions

The following findings are calculated from this run's tables, not hand-entered market claims. They establish patterns in uploaded records, not causal effects, investment returns or complete market trends. Read the methodology, missingness and repeated-row caveats before presenting rankings. Power BI import, relationships, DAX measures and page design are documented in `powerbi/EDA_MODEL.md`.''')
    add('code','''display(Markdown((ROOT / analysis["report_directory"] / "insights.md").read_text()))
print("Three monthly analytical fact totals:")
for name in ("fact_land_2022", "fact_land_2024", "fact_brokerage_2025"):
    print(name, len(tables[name]), "aggregate rows →", int(tables[name].reported_record_count.sum()), "source occurrences")
print("No annual/YoY, monetary, price, imputation or cross-scope market-total calculation is included.")''')
    nb=nbformat.v4.new_notebook(cells=cells)
    nb.metadata.update(kernelspec={'display_name':'Python 3.12 (project environment)','language':'python','name':'python3'},
        language_info={'name':'python','version':'.'.join(map(str,sys.version_info[:3]))},
        oman_eda={'generated_by':'src.eda_notebook','run_id':run_id,'sources':'docs/eda_config.json'})
    return nb


def execute(notebook,root):
    # Pin the kernel to the interpreter running the pipeline, rather than PATH's Python.
    manager=KernelManager(kernel_name='python3')
    manager.kernel_spec.argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}']
    env=os.environ.copy()
    env.setdefault('IPYTHONDIR',str(Path(root)/'work/ipython'))
    env.setdefault('JUPYTER_RUNTIME_DIR',str(Path(root)/'work/jupyter-runtime'))
    client=NotebookClient(notebook,km=manager,timeout=180,record_timing=False,
        resources={'metadata':{'path':str(root)}},allow_errors=False)
    try:
        client.execute(env=env)
    finally:
        if manager.has_kernel:
            manager.shutdown_kernel(now=True)
    nbformat.validate(notebook)
    return notebook
