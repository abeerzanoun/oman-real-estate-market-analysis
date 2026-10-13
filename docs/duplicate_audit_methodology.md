# Duplicate audit methodology and import decision

This audit was requested before further Power BI modeling/import. No model, DAX or dashboard is generated or changed by the audit. It reads all four original XLSX workbooks and every CSV in the two committed output bundles selected for import: audit `71008482abd46aa7f0bc` and EDA `168665c92a8a2ff91598`, **43 CSVs in total**. Later temporary CI validation runs are other versions, not extra inputs to this snapshot. A future import using different files must update the configuration and rerun the audit.

Latest main at branch creation: `c015ded58f219d8b320194b902d3b49c26a4fd7c`, including merged PR #5. Exact settings are in [duplicate_audit_config.json](duplicate_audit_config.json). See the [report index](../reports/DUPLICATE_AUDIT.md) for all dataset reports and evidence files.

## Run without modifying datasets

From the repository root in the locked Python 3.12 environment:

```bash
python -m src.audit_duplicates
python -m pytest
```

The script uses the existing read-only XLSX reader with worksheet dimensions reset in memory. Originals are never saved. All processed CSVs are verified against existing manifests; all 47 original/CSV input hashes are checked again after inspection. Reports go to an immutable `reports/duplicates/<run_id>/` folder. Existing reports with changed bytes are rejected, not overwritten. The run fingerprint records configuration, the auditor, current detector, worksheet reader and all protected input hashes.

## What the current repeated-group flag actually tests

`src.audit_uploaded_data` hashes the tuple of **all decoded data cells in original column order** using `sha256(json.dumps(row, ensure_ascii=False, default=str).encode())`. Source values are case/whitespace sensitive. No normalized governorate, wilayat, source-row ID or inferred property identifier enters this signature. Decoded dates use the existing JSON default string conversion; XML styles/file metadata are not record attributes.

| Original dataset | Exact columns in current signature |
|---|---|
| Muscat brokerage 2025 | اسم المعاملة; الولاية; تاريخ الإجراء; نوع الإستعمال; وصف العقار |
| November 2022 land | TRANSACTION_DATE; BUYER_TYPE; REGION_AR; REGION_EN; WILAYAT_AR; WILAYAT_EN; VILLAGE_AR; VILLAGE_EN; GENDER_NAME_AR; GENDER_NAME_EN; NO_OF_OWNERS |
| December 2022 land | Same eleven original fields as November |
| October 2024 land | TRANSACTION_DATE; SERVICE_SUB_ID; BUYER_TYPE; REGION_AR; REGION_EN; WILAYAT_AR; WILAYAT_EN; VILLAGE_AR; VILLAGE_EN; RE_VALUE; DATE_OF_BIRTH; GENDER_NAME_AR; GENDER_NAME_EN; SINGLE_MULTIPLE; NO_OF_OWNERS |

The audit independently recomputes every original signature, group size and occurrence rank against the existing processed rows. A signature indicates repeated visible **attributes**, not confirmed repeated transactions. Matching every field is insufficient if the source omits its identifying key.

## Four different concepts

1. **Full-source repeated pattern:** equality under the exact original-column signature above. All occurrences remain; coarse attributes can repeat across legitimate registrations. Distinct signatures are not unique transactions.
2. **Exported-payload repetition:** equality using only direct source-derived fields retained in the audited CSV. This excludes generated IDs, source row/hash/sheet, raw-row signature, repeat flags, normalized comparison keys and redundant derived year/month. Dates are matched using the documented ISO conversion, owner counts as integers, and RE_VALUE using its exact XML-derived Decimal export token. Gender is absent from land exports; birth date is also absent from October 2024. Dropping those fields creates projection collisions even when the original full rows differ. Amount matching does not assume OMR or a price meaning.
3. **Confirmed repeated ingestion of one source occurrence:** two identical processed representations of the same original file SHA, sheet and Excel row. This is confirmable without an economic transaction ID. Conflicting representations of one source occurrence are errors requiring review, not a basis for automatic deletion. None exists in the selected current CSVs. Controlled tests replay an actual existing source occurrence in memory to check the distinction; no new market records are generated or saved.
4. **Intentional representation/aggregation:** original → audited rows → monthly facts and summaries. Source occurrences are represented again intentionally. Five byte-identical metadata pairs are copied across the two stages. Their presence is not evidence of duplicate transactions. Monthly facts collapse physical rows into documented groups while preserving SUM(reported_record_count); that is aggregation, not deduplication. Never append raw/audited/aggregated versions into one additive fact.

Full CSV-row equality alone is misleading because generated lineage IDs make source CSV rows unique. Conversely, a business-only DISTINCT can discard genuine source occurrences. The audit tests both criteria and identifies exactly which omitted original fields differ within each projected group. It does not use fuzzy spelling/translation matches, statistical similarity scores or demographic fields as transaction keys.

## Identity and evidence standard

No original workbook supplies a reliable official transaction/record ID. The only ID-named source data column is SERVICE_SUB_ID, with two observed codes; it is not unique. Dates, locations, classifications, owner counts, gender, birth date and numeric amounts do not establish event identity. Every original column is assessed for completeness/distinct values; none is a complete unique column.

`record_id` is generated from `file SHA | sheet | Excel row`. It reliably identifies one occurrence within a specific source version; it is not an official transaction ID and changes when that file/version changes. Source row numbers alone repeat between files. Unique generated IDs do not prove unique economic transactions, and a complete unique combination of attributes would not establish a documented business key.

The four original reporting ranges have no shared observed transaction dates. November/December are the same observed schema but have disjoint periods; other source definitions differ. No cross-file economic identity is claimed. Group/source-row memberships, processed logical record ordinals and known differences are traceable in the evidence ledgers. Ordinals count CSV data records, not physical lines, because original labels can contain quoted line breaks.

## Current disposition and subsequent import

**Zero confirmed ingestion duplicates; zero confirmed economic duplicates; actual economic duplicate count unknown. Zero rows removed.** Every source occurrence remains, and all existing processed files are unchanged. No separately cleaned dataset is warranted by current evidence. Reports and occurrence-review CSVs are audit evidence, not replacement fact tables.

Use reported-occurrence measures and the three separate existing definitions if importing after this completed audit. The current `records_in_repeated_groups` measures describe **full-source patterns**, not processed-payload uniqueness or confirmed errors. In particular, a zero October 2024 full-source repeat count must not be presented as "unique transactions" or "duplicate-free business records". Do not use Power Query Remove duplicates or business-field DISTINCT without authoritative identifying evidence.

Before removing source transaction repetitions, obtain an official stable event/record identifier or documented composite key, issuer duplicate/revision evidence, and row-grain documentation explaining multiple-owner representations. If that evidence later establishes removal, create a new separately named cleaned run and a row-level removal ledger: original SHA/sheet/row, generated ID, official key, evidence reference, reason, survivor choice, affected periods/scopes, and before/after count reconciliation. Preserve current originals and processed files. This audit performs no speculative deletion and does not certify complete-market coverage or transaction identity.

Birth dates, gender values, village values and monetary token values are not displayed in report examples or evidence ledgers. Comparisons used the actual original data; diagnostic field names and counts are sufficient to demonstrate lost granularity. Existing source URL/licence, unit and publication-definition limits remain in the source registry.
