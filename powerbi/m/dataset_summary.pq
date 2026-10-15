// Generated from model_contract.json; do not edit this query independently.
let
    Schema = {
    [Name="dataset_id", Kind="text", Nullable=false],
    [Name="scope_id", Kind="text", Nullable=false],
    [Name="reported_record_count", Kind="integer", Nullable=false],
    [Name="first_record_date", Kind="date", Nullable=false],
    [Name="last_record_date", Kind="date", Nullable=false],
    [Name="observed_months", Kind="integer", Nullable=false],
    [Name="observed_governorates", Kind="integer", Nullable=false],
    [Name="observed_wilayat_labels", Kind="integer", Nullable=false],
    [Name="nonstandard_wilayat_rows", Kind="integer", Nullable=false]
    },
    Imported = fnAuditedCsv("dataset_summary.csv", Schema, 4, null)
in
    Imported
