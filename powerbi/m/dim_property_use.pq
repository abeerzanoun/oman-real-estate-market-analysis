// Generated from model_contract.json; do not edit this query independently.
let
    Schema = {
    [Name="property_use_key", Kind="text", Nullable=false],
    [Name="property_use_ar", Kind="text", Nullable=false]
    },
    Imported = fnAuditedCsv("dim_property_use.csv", Schema, 8, null)
in
    Imported
