// Generated from model_contract.json; do not edit this query independently.
let
    Schema = {
    [Name="dataset_id", Kind="text", Nullable=false],
    [Name="scope_id", Kind="text", Nullable=false],
    [Name="file", Kind="text", Nullable=false],
    [Name="sha256", Kind="text", Nullable=false],
    [Name="sheet", Kind="text", Nullable=false],
    [Name="header_row", Kind="integer", Nullable=false],
    [Name="audited_row_count", Kind="integer", Nullable=false],
    [Name="filename_period_label", Kind="text", Nullable=false],
    [Name="provider", Kind="text", Nullable=false],
    [Name="provider_evidence", Kind="text", Nullable=false],
    [Name="official_download_url", Kind="text", Nullable=true],
    [Name="official_landing_url", Kind="text", Nullable=true],
    [Name="provider_entry_point", Kind="text", Nullable=false],
    [Name="source_verification_status", Kind="text", Nullable=false],
    [Name="licence", Kind="text", Nullable=true],
    [Name="licence_url", Kind="text", Nullable=true],
    [Name="currency_unit", Kind="text", Nullable=true],
    [Name="service_code_definitions", Kind="text", Nullable=false],
    [Name="uploaded_commit", Kind="text", Nullable=false],
    [Name="min_date", Kind="date", Nullable=false],
    [Name="max_date", Kind="date", Nullable=false],
    [Name="reported_record_count", Kind="integer", Nullable=false]
    },
    Imported = fnAuditedCsv("dim_dataset.csv", Schema, 4, null)
in
    Imported
