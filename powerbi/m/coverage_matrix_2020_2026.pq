// Generated from model_contract.json; do not edit this query independently.
let
    Schema = {
    [Name="scope_id", Kind="text", Nullable=false],
    [Name="governorate_id", Kind="text", Nullable=false],
    [Name="year", Kind="integer", Nullable=false],
    [Name="month", Kind="integer", Nullable=false],
    [Name="availability_status", Kind="text", Nullable=false],
    [Name="reported_record_count", Kind="integer", Nullable=true]
    },
    Imported = fnAuditedCsv("coverage_matrix_2020_2026.csv", Schema, 2772, null)
in
    Imported
