// Generated from model_contract.json; do not edit this query independently.
let
    Schema = {
    [Name="governorate_id", Kind="text", Nullable=false],
    [Name="governorate_en", Kind="text", Nullable=false],
    [Name="governorate_ar", Kind="text", Nullable=false]
    },
    Imported = fnAuditedCsv("dim_governorate.csv", Schema, 11, null)
in
    Imported
