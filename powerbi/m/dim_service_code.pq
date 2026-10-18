// Generated from model_contract.json; do not edit this query independently.
let
    Schema = {
    [Name="service_sub_id", Kind="text", Nullable=false],
    [Name="definition_status", Kind="text", Nullable=false]
    },
    Imported = fnAuditedCsv("dim_service_code.csv", Schema, 2, null)
in
    Imported
