"""Read-only, fail-closed access to reviewed EDA facts and duplicate evidence."""
from io import BytesIO
from pathlib import Path
import hashlib
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = {
    "land_2022": "Land BuySell • Nov–Dec 2022",
    "land_2024": "Land service-coded • Oct 2024",
    "brokerage_2025": "Muscat brokerage • Jan–Sep 2025",
}
SCOPES = {
    "land_2022": "land_buy_sell_2022",
    "land_2024": "land_service_coded_2024",
    "brokerage_2025": "muscat_brokerage_registration_2025",
}
COUNT = "reported_record_count"


def _verified(path, expected):
    payload = Path(path).read_bytes()
    if hashlib.sha256(payload).hexdigest() != expected:
        raise ValueError(f"Checksum mismatch: {Path(path).name}. Review a new data version.")
    return payload


def _csv(payload):
    return pd.read_csv(BytesIO(payload), encoding="utf-8-sig")


def load_dashboard(root=ROOT):
    """Verify originals, audited artifacts, all EDA CSVs and used audit evidence.

    No glob/latest-directory lookup, writes, downloads, imputation or deduplication.
    Every Streamlit rerun verifies bytes again; no stale integrity cache.
    """
    root = Path(root)
    config = json.loads((root / "docs/dashboard_config.json").read_text())
    folder = root / config["eda_directory"]
    manifest = json.loads(_verified(folder / "analysis_manifest.json", config["eda_manifest_sha256"]))
    for name, expected in manifest["original_sha256"].items():
        _verified(root / name, expected)
    audit_folder = root / manifest["input_audit_directory"]
    _verified(audit_folder / "manifest.json", manifest["input_manifest_sha256"])
    for name, expected in manifest["input_artifact_sha256"].items():
        _verified(audit_folder / name, expected)
    tables = {Path(name).stem: _csv(_verified(folder / name, expected))
              for name, expected in manifest["csv_sha256"].items()}
    dup_folder = root / config["duplicate_directory"]
    dup_manifest = json.loads(_verified(dup_folder / "manifest.json", config["duplicate_manifest_sha256"]))
    report = json.loads(_verified(dup_folder / "audit_report.json", dup_manifest["output_sha256"]["audit_report.json"]))
    tables["duplicate_summary"] = _csv(_verified(dup_folder / "dataset_duplicate_summary.csv",
                                               dup_manifest["output_sha256"]["dataset_duplicate_summary.csv"]))
    if not report["audit_complete"] or not report["source_and_processed_occurrences_match"]:
        raise ValueError("Duplicate audit is incomplete or unreconciled")
    if report["rows_removed"] != 0:
        raise ValueError("This dashboard version expects the reviewed, unremoved occurrences")
    for family in FAMILIES:
        fact = tables["fact_" + family]
        expected = manifest["fact_reconciliation"][family]["source_rows"]
        if int(fact[COUNT].sum()) != expected or not fact[COUNT].gt(0).all():
            raise ValueError(f"Fact reconciliation failed: {family}")
        if not fact.records_in_repeated_groups.between(0, fact[COUNT]).all():
            raise ValueError("Invalid repeated occurrence counts")
    return {"tables": tables, "manifest": manifest, "duplicates": report, "config": config}


def family_frame(bundle, family):
    """Join dimensions without changing the fact grain or its weighted count."""
    tables = bundle["tables"]
    frame = tables["fact_" + family].copy()
    frame = frame.merge(tables["dim_governorate"], on="governorate_id", validate="many_to_one")
    frame = frame.merge(tables["dim_wilayat"][["wilayat_key", "wilayat_ar"]],
                        on="wilayat_key", validate="many_to_one")
    if family == "brokerage_2025":
        for field in ("property_use", "property_description"):
            frame = frame.merge(tables["dim_" + field], on=field + "_key", validate="many_to_one")
    return frame


def filter_frame(frame, filters):
    """An empty selection means no matches; unavailable selections also stay empty."""
    result = frame.copy()
    for column, values in filters.items():
        if column not in result.columns:
            raise ValueError(f"Unsupported filter: {column}")
        result = result[result[column].isin(values)]
    return result.reset_index(drop=True)


def summarize(frame, keys):
    """Count source occurrences by SUM of fact weights, never aggregate row count."""
    result = frame.groupby(keys, observed=True, dropna=False)[COUNT].sum().reset_index()
    denominator = result[COUNT].sum()
    result["share_of_selection_pct"] = 100 * result[COUNT] / denominator if denominator else pd.Series(dtype=float)
    return result.sort_values(COUNT, ascending=False, kind="stable").reset_index(drop=True)


def export_csv(frame, family):
    """Download the selected aggregate facts with interpretation metadata, UTF-8 BOM."""
    result = frame.copy()
    result["scope_id"] = SCOPES[family]
    result["count_semantics"] = "source_record_occurrences_not_verified_unique_transactions"
    result["eda_run_id"] = "168665c92a8a2ff91598"
    return result.to_csv(index=False).encode("utf-8-sig")
