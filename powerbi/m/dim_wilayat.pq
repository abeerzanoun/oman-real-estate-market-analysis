// Generated from model_contract.json; do not edit this query independently.
let
    Schema = {
    [Name="wilayat_key", Kind="text", Nullable=false],
    [Name="governorate_id", Kind="text", Nullable=false],
    [Name="wilayat_ar", Kind="text", Nullable=false]
    },
    Imported = fnAuditedCsv("dim_wilayat.csv", Schema, 65, null)
in
    Imported
