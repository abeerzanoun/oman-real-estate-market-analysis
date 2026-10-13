# Duplicate audit before Power BI import

Completed 2026-10-13 from main `c015ded` (merged PR #5). Immutable audit run `4162ac42cfdaebd9d962`.

**All 28,558 source occurrences retained. Zero confirmed ingestion duplicates, zero removals, no cleaned replacements. Actual economic transaction duplication remains unknown because official event IDs are absent. No Power BI modeling/import was performed.**

[Complete audit](duplicates/4162ac42cfdaebd9d962/README.md) · [Machine-readable report](duplicates/4162ac42cfdaebd9d962/audit_report.json) · [Input/output hash manifest](duplicates/4162ac42cfdaebd9d962/manifest.json) · [Methodology](../docs/duplicate_audit_methodology.md) · [Validation](../docs/duplicate_audit_validation.md)

| Dataset | Source rows | Full-source repeats after first | Exported-payload repeats after first | Dataset report |
|---|---:|---:|---:|---|
| muscat_brokerage_2025 | 9,366 | 6,778 | 6,778 | [Criteria/examples/recommendations](duplicates/4162ac42cfdaebd9d962/muscat_brokerage_2025.md) |
| land_nov_2022 | 7,501 | 2,629 | 3,076 | [Criteria/examples/recommendations](duplicates/4162ac42cfdaebd9d962/land_nov_2022.md) |
| land_dec_2022 | 5,667 | 1,843 | 2,138 | [Criteria/examples/recommendations](duplicates/4162ac42cfdaebd9d962/land_dec_2022.md) |
| land_oct_2024 | 6,024 | 0 | 278 | [Criteria/examples/recommendations](duplicates/4162ac42cfdaebd9d962/land_oct_2024.md) |

These are attribute-pattern repetitions, not counts approved for deletion. Current signatures use all original data columns. Dropping gender and birth-date fields for exported business views creates additional matching groups; October 2024 has 232 such groups with 510 occurrences despite zero full-source repetitions.

Each report has a [source-occurrence review ledger](duplicates/4162ac42cfdaebd9d962/) and full group memberships, including original Excel row numbers and logical CSV record ordinals. These are evidence files, not alternative import facts. [CSV inventory](duplicates/4162ac42cfdaebd9d962/processed_csv_inventory.csv) covers all 43 CSVs in the two committed import snapshots. [Source-column identity assessment](duplicates/4162ac42cfdaebd9d962/source_column_identity_assessment.csv) profiles every original field.

Five byte-identical metadata export pairs are reused across stages. Existing aggregate facts preserve counts 13,168 (2022 land), 6,024 (Oct 2024 land) and 9,366 (Muscat brokerage), with no duplicated aggregation grain. Load one selected model/run; do not append original, audited and aggregate representations or apply business-field DISTINCT.

Obtain stable official IDs, row-grain definitions and issuer duplicate/revision evidence before treating source repetitions as errors. Any justified future removal must have separately named outputs and a row-level evidence/removal ledger. No rows can be justified for removal from the current evidence.
