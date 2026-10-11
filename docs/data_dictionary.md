# Preliminary data dictionary

**Every field below is proposed.** No source dataset or analytical schema has been obtained. Types, requiredness, dimensions and validation rules must be confirmed after acquisition; unsupported dimensions remain unavailable.

Potential observation grain: one source-defined metric for one reporting period, geographic level, property category and transaction scope. Transaction measures and price indices may need separate fact tables when their grains differ. A unique key cannot be finalized yet.

| Proposed field | Proposed type | Meaning / unit | Proposed validation and caveats | Status |
|---|---|---|---|---|
| year | nullable integer | Reporting year | 2020–2026 only where verified; not publication year | Proposed |
| month | nullable integer | Reporting month | 1–12 for monthly observations; null for annual/quarterly records | Proposed |
| governorate | nullable string | Source-defined governorate | Preserve original label; map verified codes; distinguish national totals | Proposed |
| wilayat | nullable string | Source-defined wilayat | Validate hierarchy; null if unavailable or more aggregated | Proposed |
| property_category | nullable string | Source property classification | Preserve definitions; do not infer categories or equate land with all property | Proposed |
| transaction_count | nullable integer | Count of defined transactions | Nonnegative; distinguish sales, mortgages, deeds and other registrations | Proposed |
| transaction_value_omr | nullable decimal | Value in Omani rial | Nonnegative if source definition supports it; retain original scale and convert million OMR explicitly; preserve decimal precision | Proposed |
| property_price_index | nullable decimal | Index points | Retain base year/value; do not store inflation percentages as an index | Proposed |
| data_source | string | Publisher and resource identifier | Traceable to provenance register and original file | Proposed |
| reporting_period | string | Source reporting interval | Explicit start/end and monthly, quarterly, annual or cumulative status | Proposed |
| period_start / period_end | date | Inclusive reporting boundaries | Confirm dates and consistency with frequency | Proposed |
| reporting_frequency | string | Monthly / quarterly / annual | Source-defined; never sum overlapping cumulative records | Proposed |
| transaction_type | nullable string | Sales / mortgages / other source-defined type | Keep scopes separate | Proposed |
| geographic_level | string | National / governorate / wilayat | Prevent totals being added to component geographies | Proposed |
| index_base_period | nullable string | Official index reference period | Required for interpreting/comparing index series | Proposed |
| source_url / source_file | string | Exact resource and local original | Capture during acquisition | Proposed |
| retrieved_at / published_at | timestamp / nullable date | Provenance dates | Retrieval uses explicit timezone; publication differs from reporting period | Proposed |
| is_provisional | nullable boolean | Source provisional/revised status | Unknown is distinct from false | Proposed |

## Cross-tool conventions to confirm

Use UTF-8 and stable snake_case names for future CSV exports; preserve Arabic labels and reviewed English mappings. Use ISO dates, explicit OMR units and documented decimals for Excel/Power BI. Export nulls consistently and avoid mixing missing observations with zero. Power BI relationships require verified date/geography/category keys; no dashboard or model is created in this phase.

Changes to coverage, definitions, units and index bases must be recorded before aggregations or comparisons. An average transaction value is not a property price index and is sensitive to transaction mix.
