// Generated from model_contract.json; do not edit this query independently.
let
    Schema = {
    [Name="buyer_type", Kind="text", Nullable=false]
    },
    Imported = fnAuditedCsv("dim_buyer_type.csv", Schema, 2, null)
in
    Imported
