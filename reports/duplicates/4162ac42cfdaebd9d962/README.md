# Duplicate audit before Power BI import

**Audit complete: 28,558 source occurrences, four workbooks and 43 existing CSVs inspected.** Zero confirmed duplicated ingestion occurrences. Economic transaction duplication is **not determinable**. **Zero records removed; no cleaned replacement files generated.**

| Dataset | Rows | Full-source groups | Full-source after first | Exported-payload groups | Payload after first |
|---|---:|---:|---:|---:|---:|
| [muscat_brokerage_2025](muscat_brokerage_2025.md) | 9366 | 1396 | 6778 | 1396 | 6778 |
| [land_nov_2022](land_nov_2022.md) | 7501 | 1046 | 2629 | 1094 | 3076 |
| [land_dec_2022](land_dec_2022.md) | 5667 | 757 | 1843 | 804 | 2138 |
| [land_oct_2024](land_oct_2024.md) | 6024 | 0 | 0 | 232 | 278 |

No workbook contains a reliable official event ID. Current group flags hash **all original data fields**, including non-exported gender/birth-date fields. This explains why October 2024 has zero full-source repetitions but exported-attribute matches. Equal attributes are not proven duplicate transactions, and different demographics do not prove separate transactions.

## Evidence and representations

- Original and processed hashes are protected; every audited occurrence maps to its original sheet/row. Current signatures/group sizes/ranks were recomputed.
- All 43 CSVs in the two selected committed output bundles have zero repeated full rows under their complete columns. Source row CSVs also have unique generated IDs and source occurrence keys. Dropping those unique lineage columns exposes attribute repetitions; uniqueness of full CSV rows alone does not establish unique transactions.
- Three existing monthly fact tables were compared bucket-by-bucket to source occurrences, including repeated-group counts. Every multiplicity is preserved; lower physical fact-row counts are intentional aggregation.
- 5 identical CSV-copy groups are reference/quality/coverage exports reused across stages, not duplicated transaction evidence. Load one chosen model run, not multiple copies.
- The four original date ranges do not overlap. This prevents same-date matches across these uploads; it does not establish economic event identity or justify pooling different definitions.

## Files and action

Each dataset has a Markdown report, a full repeated-group ledger and an occurrence review CSV. Review CSVs are audit evidence, **not cleaned analytical fact replacements**; they contain no birth dates, genders or monetary amounts. audit_report.json includes criteria, example source rows, identifier assessment, inventories and recommendations. manifest.json records every original/processed input and output hash.

**Import guidance after this audit:** retain reported source occurrences under their separate definitions; do not deduplicate business attributes. Source authenticity/completeness, transaction identity and financial/code meanings retain the existing limitations. Power BI modeling/import was not performed during this audit.

If official IDs or issuer evidence later confirm duplicates, preserve current outputs and create a new reviewed cleaned run plus a removal ledger containing source/processed occurrence IDs, evidence, survivor choice and reconciliation. The current files provide insufficient removal evidence.
