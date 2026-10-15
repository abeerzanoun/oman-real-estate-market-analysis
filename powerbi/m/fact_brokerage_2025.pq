// Generated from model_contract.json; do not edit this query independently.
let
    Schema = {
    [Name="dataset_id", Kind="text", Nullable=false],
    [Name="period_id", Kind="text", Nullable=false],
    [Name="governorate_id", Kind="text", Nullable=false],
    [Name="wilayat_key", Kind="text", Nullable=false],
    [Name="nonstandard_wilayat_label", Kind="boolean", Nullable=false],
    [Name="property_use_key", Kind="text", Nullable=false],
    [Name="property_description_key", Kind="text", Nullable=false],
    [Name="reported_record_count", Kind="integer", Nullable=false],
    [Name="records_in_repeated_groups", Kind="integer", Nullable=false]
    },
    Imported = fnAuditedCsv("fact_brokerage_2025.csv", Schema, 403, 9366)
in
    Imported
