// Generated from model_contract.json; do not edit this query independently.
let
    Schema = {
    [Name="dataset_id", Kind="text", Nullable=false],
    [Name="reported_record_count", Kind="integer", Nullable=false],
    [Name="records_in_repeated_groups", Kind="integer", Nullable=false],
    [Name="repeated_occurrences_after_first", Kind="integer", Nullable=false],
    [Name="repeated_group_share_pct", Kind="decimal", Nullable=false],
    [Name="rows_removed", Kind="integer", Nullable=false],
    [Name="reported_amount_present_records", Kind="integer", Nullable=true],
    [Name="reported_amount_missing_records", Kind="integer", Nullable=true],
    [Name="monetary_unit_verified", Kind="boolean", Nullable=false]
    },
    Imported = fnAuditedCsv("data_quality_summary.csv", Schema, 4, null)
in
    Imported
