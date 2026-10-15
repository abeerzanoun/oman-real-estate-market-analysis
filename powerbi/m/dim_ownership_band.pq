// Generated from model_contract.json; do not edit this query independently.
let
    Schema = {
    [Name="ownership_band", Kind="text", Nullable=false]
    },
    Imported = fnAuditedCsv("dim_ownership_band.csv", Schema, 5, null)
in
    Imported
