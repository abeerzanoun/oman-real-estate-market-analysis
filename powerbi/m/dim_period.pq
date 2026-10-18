// Generated from model_contract.json; do not edit this query independently.
let
    Schema = {
    [Name="period_id", Kind="text", Nullable=false],
    [Name="year", Kind="integer", Nullable=false],
    [Name="month", Kind="integer", Nullable=false],
    [Name="period_label", Kind="text", Nullable=false]
    },
    Imported = fnAuditedCsv("dim_period.csv", Schema, 12, null)
in
    Imported
