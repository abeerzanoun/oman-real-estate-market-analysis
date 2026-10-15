"""Runtime-only import/chart regression checks using the existing audited data.

Run from the repository root: python tests/check_dashboard_runtime.py
Requires only requirements.txt; Pytest and analysis tools are not needed.
"""
import importlib.metadata
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    # Keep direct imports explicit: a missing Express/transitive module must fail
    # this check instead of being hidden by a fallback or optional chart path.
    import plotly.express
    import narwhals.stable.v1
    import src.dashboard_charts
    import streamlit_app
    from streamlit.testing.v1 import AppTest
    from src.dashboard_charts import period_bar, ranked_bar
    from src.dashboard_data import COUNT, FAMILIES, family_frame, load_dashboard, summarize
    from src.dashboard_pages import PAGES

    print(f"Python {sys.version.split()[0]}")
    for name in ("plotly", "narwhals", "pandas", "numpy", "streamlit"):
        print(f"{name} {importlib.metadata.version(name)}")
    print("PASS Plotly Express, dataframe adapter, chart module and entry-point imports")
    bundle = load_dashboard()
    keys = ["dataset_id", "period_id", "governorate_id"]
    for family in FAMILIES:
        frame = family_frame(bundle, family)
        expected_total = bundle["manifest"]["fact_reconciliation"][family]["source_rows"]
        assert int(frame[COUNT].sum()) == expected_total, family
        actual = summarize(frame, keys)[keys + [COUNT]].sort_values(keys)
        expected = bundle["tables"]["governorate_counts"]
        expected = expected[expected.dataset_id.isin(frame.dataset_id.unique())]
        expected = expected[keys + [COUNT]].sort_values(keys)
        assert actual.to_dict("records") == expected.to_dict("records"), family
        monthly = summarize(frame, ["period_id"])
        governorates = summarize(frame, ["governorate_en"])
        for fig in (period_bar(monthly, family), ranked_bar(governorates, "governorate_en", family)):
            assert json.loads(fig.to_json())["data"][0]["type"] == "bar", family
            trace = fig.data[0]
            values = trace.x if trace.orientation == "h" else trace.y
            assert sum(int(v) for v in values) == expected_total, family
        print(f"PASS {family}: {expected_total:,} source occurrences; canonical geography counts and chart serialization")

    app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30).run()
    for page in PAGES:
        app.radio(key="page").set_value(page).run()
        assert not app.exception and not app.error, f"Runtime failure: {page}"
        print(f"PASS page: {page}")
    app.radio(key="page").set_value("Land Market Analysis").run()
    app.multiselect(key="land_land_2022_periods").set_value(["2022-11"]).run()
    assert not app.exception and not app.error
    expected = bundle["tables"]["dataset_summary"]
    nov_count = int(expected.loc[expected.dataset_id.eq("land_nov_2022"), COUNT].iloc[0])
    assert app.metric[0].value == f"{nov_count:,}"
    print("PASS filtered land KPI matches the pinned November source summary")


if __name__ == "__main__":
    main()
