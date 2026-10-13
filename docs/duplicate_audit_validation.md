# Duplicate audit validation — 2026-10-13

Base main `c015ded58f219d8b320194b902d3b49c26a4fd7c`, merged PR #5. Audit `4162ac42cfdaebd9d962`. Python 3.12.14 with existing locked dependencies; no dependency/version changes were needed.

| Check | Actual result |
|---|---|
| Four originals and all six worksheets | Read-only inspection; incorrect source dimensions reset in memory |
| Input hashes before/after | All four XLSX and 43 selected CSV hashes unchanged, 47 protected data files |
| Current raw signature/group-size/rank recomputation | PASS for all 28,558 source occurrences |
| Source → audited value and occurrence mapping | PASS, one representation per original file/sheet/row; generated lineage IDs verified |
| Full-source pattern repeats after first | 6,778 brokerage; 2,629 November; 1,843 December; 0 October |
| Exported-payload pattern repeats after first | 6,778 brokerage; 3,076 November; 2,138 December; 278 October |
| Official identifier assessment | No reliable official transaction/record IDs; SERVICE_SUB_ID has only two observed values |
| Full-row duplicates in current CSV snapshot | Zero within each of all 43 CSVs; full-row uniqueness does not prove unique economic events |
| Cross-file representation review | Five metadata copy pairs are byte-identical and intentional; all four source periods have disjoint observed transaction dates |
| Existing monthly aggregate validation | Every bucket and repeated-group count reconciles: 361 rows→13,168; 257→6,024; 403→9,366 |
| Confirmed duplicate ingestion occurrences | Zero in actual selected inputs |
| Confirmed economic duplicate transactions | Zero confirmed; actual count unknown without identifying evidence |
| Removed records / reasons | Zero; no justification supports deleting any source occurrence |
| Cleaned outputs | None created; reports/ledgers are audit evidence, not replacement facts |
| Power BI work during audit | No model, DAX or dashboard generated/imported |
| Full automated tests | **97 passed**, 14 existing Matplotlib/Pyparsing deprecation warnings, 26.51 seconds |

The twelve new tests use genuine source-derived data. An in-memory replay of one real original occurrence confirms ingestion duplication can be recognized, while two separate real source rows with equal attributes are retained. No synthetic market observations or new sample datasets are saved. Tests cover keys/criteria, actual repetition/collision counts, privacy-safe examples and full memberships, all CSV/copy inventories, source/aggregate multiplicity, original/output hashes, immutable report refusal and checksum failures.

Full tests ran after the duplicate audit completed. Existing EDA tests reproduce prior analytical artifacts only in temporary validation output; no new Power BI modeling was performed. CI now runs duplicate auditing before existing analytical/model reproduction. The actual current audit provides sufficient import guidance for reported occurrences, but does not establish event uniqueness.

The duplicate audit does not modify original workbooks, historical processed outputs, model definitions or financial meanings. Recommended future removal requires source-backed IDs/grain and issuer evidence, new cleaned outputs and a removal ledger. All current source-authenticity/licence/completeness limitations remain documented.
