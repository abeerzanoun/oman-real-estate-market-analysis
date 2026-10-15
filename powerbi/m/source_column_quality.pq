// Generated from model_contract.json; do not edit this query independently.
let
    Schema = {
    [Name="dataset_id", Kind="text", Nullable=false],
    [Name="column", Kind="text", Nullable=false],
    [Name="missing", Kind="integer", Nullable=false],
    [Name="observed_types", Kind="text", Nullable=false]
    },
    Imported = fnAuditedCsv("source_column_quality.csv", Schema, 42, null)
in
    Imported
