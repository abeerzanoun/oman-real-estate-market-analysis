"""Dashboard checks use the existing audited records; no synthetic market rows."""
from io import BytesIO
from pathlib import Path
import shutil

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from src.dashboard_charts import coverage_heatmap, period_bar
from src.dashboard_data import COUNT, FAMILIES, ROOT, export_csv, family_frame, filter_frame, load_dashboard, summarize
from src.dashboard_pages import PAGES


@pytest.fixture(scope="module")
def bundle():
    return load_dashboard()


@pytest.mark.parametrize("family,expected,physical", [("land_2022", 13168, 361),
    ("land_2024", 6024, 257), ("brokerage_2025", 9366, 403)])
def test_join_and_weighted_totals(bundle, family, expected, physical):
    frame = family_frame(bundle, family)
    assert len(frame) == physical
    assert frame[COUNT].sum() == expected
    assert summarize(frame, ["governorate_id"])[COUNT].sum() == expected
    assert not frame.wilayat_ar.isna().any()


def test_real_filters_and_empty_selection(bundle):
    frame = family_frame(bundle, "land_2022")
    nov = filter_frame(frame, {"period_id": ["2022-11"]})
    assert nov[COUNT].sum() == 7501
    muscat = filter_frame(nov, {"governorate_id": ["muscat"]})
    assert muscat[COUNT].sum() == 960
    assert filter_frame(frame, {"period_id": []}).empty
    assert filter_frame(frame, {"period_id": ["2023-01"]}).empty
    with pytest.raises(ValueError, match="Unsupported filter"):
        filter_frame(frame, {"unverified_price": []})


def test_supplied_periods_only_and_unresolved_uniqueness(bundle):
    assert set(family_frame(bundle, "land_2022").period_id) == {"2022-11", "2022-12"}
    broker = family_frame(bundle, "brokerage_2025")
    assert set(broker.period_id) == {f"2025-{m:02d}" for m in range(1, 10)}
    assert set(broker.governorate_id) == {"muscat"}
    assert bundle["duplicates"]["actual_duplicate_economic_transaction_count"] is None
    assert bundle["duplicates"]["rows_removed"] == 0


@pytest.mark.parametrize("family", list(FAMILIES))
def test_downloads_are_safe_weighted_aggregates(bundle, family):
    result = pd.read_csv(BytesIO(export_csv(family_frame(bundle, family), family)))
    assert result[COUNT].sum() == bundle["manifest"]["fact_reconciliation"][family]["source_rows"]
    assert result.count_semantics.eq("source_record_occurrences_not_verified_unique_transactions").all()
    assert not {"reported_re_value", "currency_unit", "date_of_birth", "gender_name_ar"} & set(result.columns)
    assert not any("price" in c or "amount" in c or "birth" in c for c in result.columns)


def test_brokerage_monthly_plot_is_observed_categorical_bar(bundle):
    table = summarize(family_frame(bundle, "brokerage_2025"), ["period_id"])
    fig = period_bar(table, "Observed months")
    assert fig.layout.xaxis.type == "category"
    assert all(trace.type == "bar" for trace in fig.data)
    assert list(fig.data[0].y) == [857, 1147, 819, 880, 1207, 816, 1277, 1141, 1222]


def test_coverage_unknowns_are_never_zero_counts(bundle):
    tables = bundle["tables"]
    matrix = tables["coverage_matrix_2020_2026"]
    assert matrix.loc[~matrix.availability_status.eq("observed"), COUNT].isna().all()
    matrix = matrix[matrix.scope_id.eq("muscat_brokerage_registration_2025")]
    fig = coverage_heatmap(matrix, tables["dim_governorate"], 2025)
    assert len(fig.data[0].z) == 11
    assert "Count unavailable" in fig.data[0].text[0][9]
    assert "1,222 source occurrences" in fig.data[0].text[0][8]


@pytest.mark.parametrize("target", ["fact_land_2022.csv", "original", "duplicate_report"])
def test_loader_fails_closed_on_changed_bytes(tmp_path, target):
    # Copy actual reviewed files, then corrupt bytes solely in temporary test storage.
    for name in ("docs", "data/processed/audited/71008482abd46aa7f0bc",
                 "data/processed/eda/168665c92a8a2ff91598", "data/raw/manual",
                 "reports/duplicates/4162ac42cfdaebd9d962"):
        shutil.copytree(ROOT / name, tmp_path / name)
    if target == "original":
        path = tmp_path / "data/raw/manual/oman_land_transactions_nov_2022.xlsx"
    elif target == "duplicate_report":
        path = tmp_path / "reports/duplicates/4162ac42cfdaebd9d962/audit_report.json"
    else:
        path = tmp_path / "data/processed/eda/168665c92a8a2ff91598" / target
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="Checksum mismatch"):
        load_dashboard(tmp_path)


@pytest.mark.parametrize("page", list(PAGES))
def test_every_page_renders(page):
    app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30).run()
    app.radio(key="page").set_value(page).run()
    assert not app.exception
    assert not app.error


def test_land_page_filters_and_empty_state():
    app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30).run()
    app.radio(key="page").set_value("Land Market Analysis").run()
    assert app.metric[0].value == "13,168"
    app.multiselect(key="land_land_2022_periods").set_value(["2022-11"]).run()
    assert app.metric[0].value == "7,501"
    app.multiselect(key="land_land_2022_govs").set_value(["muscat"]).run()
    assert app.metric[0].value == "960"
    app.multiselect(key="land_land_2022_wilayats").set_value(["muscat|السيب"]).run()
    assert not app.exception
    app.multiselect(key="land_land_2022_govs").set_value(["dhofar"]).run()
    assert app.multiselect(key="land_land_2022_wilayats").value == []
    app.multiselect(key="land_land_2022_periods").set_value([]).run()
    assert not app.metric
    assert any("No supplied records" in info.value for info in app.info)
    app.selectbox(key="land_family").set_value("land_2024").run()
    assert not app.exception
    assert app.metric[0].value == "6,024"


def test_brokerage_category_filter():
    app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30).run()
    app.radio(key="page").set_value("Muscat Brokerage Analysis").run()
    assert app.metric[0].value == "9,366"
    app.multiselect(key="broker_property_use_key").set_value(["سكني"]).run()
    assert app.metric[0].value == "8,202"
    assert app.multiselect(key="broker_govs").value == ["muscat"]
    assert not app.exception
