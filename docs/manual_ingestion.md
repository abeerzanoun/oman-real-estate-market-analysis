# Manual ingestion metadata contract

No original uploads exist yet. The blank admission state in `manual_ingestion_status.json` is not an analytical dataset. Source metadata is a documented reviewer attestation; this offline workflow does not independently authenticate a publisher URL or certify every value.

## Sidecar fields

Store one `<original filename>.metadata.json` beside each XLSX/CSV. `init` generates the real checksum and pending fields once a real file is present.

| Field | Required value |
|---|---|
| dataset_id | Unique lowercase project identifier using letters, digits, underscores |
| title / publisher | Actual official title and institution |
| source_url | Exact official HTTPS resource on a `.gov.om` host |
| publication_date | Actual ISO date, or null when unknown |
| retrieved_at | Actual download ISO timestamp, including timezone |
| expected_sha256 | SHA-256 of original bytes, populated by init and checked on import |
| verification.status | `reviewed_official` only after source/file review; pending blocks ingestion |
| verification.reviewed_by / reviewed_at | Reviewer identifier and ISO timestamp with timezone |
| licence.name / url / redistribution_allowed | Verified licence attribution and HTTPS terms link; explicit true is required for repository ingestion |
| tables | Nonempty list of reviewed selections described below |

Keep source notes and original metadata/release definitions. A new source revision gets its own original, dataset registration and sidecar. Do not change expected hashes to conceal edited originals.

## Table fields

| Field | Meaning |
|---|---|
| sheet | Exact XLSX sheet name; ignored for CSV |
| header_row | 1-based header row, default 1; choose actual table headers, not title text |
| observation_grain | Must be `aggregate`; row-level transactions need a separate adapter |
| scope_id | Reviewed semantic series identifier. Matching scopes mean definitions are comparable; use separate scopes for brokerage-only, land-only or differently defined series |
| geographic_level | `governorate`, `wilayat` or `national`; all-11 readiness is checked only for governorate aggregates |
| layout | `records` (default) or `wide` |
| columns | Optional object mapping canonical field to actual source header. Explicit mapping overrides automatic aliases; ambiguous/unmapped nonempty columns are errors |
| constants | Optional verified table-level canonical dimensions: periods, frequency, governorate, category/type. Constants cannot override source columns and must derive from source metadata, never filenames or guesses |
| ignored_columns | Explicit source header list for columns reviewed as outside this selected table's observation grain |
| metrics | Nonempty metric declarations: field, indicator, source_unit, canonical unit and conversion/base details |
| totals_policy | Set `exclude` explicitly when a governorate table contains national total rows; exclusions are logged, never added to governorates |
| encoding / delimiter | CSV defaults: UTF-8 BOM supported, comma delimiter; set actual source encoding/delimiter when different |
| decimal_separator / thousands_separator | Defaults dot/comma. Explicit locale settings supported; Arabic numeric separators and digits are normalized |
| wide_dimension / wide_columns / wide_value_field | For wide layout: axis `year` or `governorate`; actual selected headers; canonical value field. No automatic interpretation of similarly named columns |

Canonical fields: `year`, `month`, `quarter`, `governorate`, `wilayat`, `property_category`, `transaction_type`, `transaction_count`, `transaction_value`, `property_price_index`, `value`, `period_start`, `period_end`, `frequency`. Year/month/quarter values are numeric; native Excel dates or ISO strings are supported for boundaries. If months are written as names, provide a source-specific adapter rather than guess their interpretation.

Metric `field` must be a mapped `transaction_count`, `transaction_value`, `property_price_index` or `value`. `indicator` is a reviewed lowercase semantic identifier, not inferred from the heading. `unit` is `count`, `OMR` or `index_points`. Every metric requires `source_unit`. Currency requires explicit positive `multiplier` (1 for OMR, 1000 for thousand OMR, 1000000 for million OMR, only where documented). Counts/indices must not be scaled; indices require the actual `index_base_period`.

Frequency must be explicit: monthly, quarterly, annual or year_to_date. Year/month/quarter dimensions can establish complete period boundaries. Cumulative records require explicit boundaries starting January 1. The reporting interval must lie within 2020–2026 and not end in the future. Unknown/missing category labels remain blank rather than fabricated. Wilayat labels are preserved without claiming a validated hierarchy.

## Outputs and review gates

Output observations are long-format real values with explicit period/unit/scope/geographic dimensions. `observation_id` hashes the business key. Equal duplicates are collapsed with all distinct cell provenance retained; differing values for a key halt the import rather than choose an undocumented revision. Select the appropriate release/files explicitly if vintages overlap.

Coverage checks every comparable governorate aggregate group, including category/type and index base; missing governorates are listed rather than created as rows. National/wilayat data remain separate and do not establish complete governorate coverage. Missing source metrics are logged and not imputed. Any invalid input prevents a new analytical run from being published; prior runs are untouched.

Each valid run is content-addressed using original and metadata hashes, pipeline version and validation date. Originals are read-only to the workflow, hashes are checked again after reading, and changed output bytes cannot overwrite an existing run. `provenance.csv` retains original cell coordinates, publisher, URL, title, licence, publication/retrieval dates and unit conversion. The dictionary documents all output fields. Processed files remain Git-ignored for review and size management.

Formula results without saved numeric caches remain missing; no formula is executed. Merged multirow headers, footnotes embedded as records, legacy XLS, arbitrary pivots and transaction-level files require a reviewed adapter/selection. Preserve the original and adjust a sidecar or adapter; do not edit raw files to bypass validation.

For maintainers: increment the pipeline version when transformations change. New versions publish new run directories instead of replacing earlier outputs. Raw manual XLSX/CSV paths are marked `-text` in `.gitattributes` to preserve original bytes across Git checkouts.
