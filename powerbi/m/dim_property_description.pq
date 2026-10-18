// Generated from model_contract.json; do not edit this query independently.
let
    Schema = {
    [Name="property_description_key", Kind="text", Nullable=false],
    [Name="property_description_ar", Kind="text", Nullable=false]
    },
    Imported = fnAuditedCsv("dim_property_description.csv", Schema, 13, null)
in
    Imported
