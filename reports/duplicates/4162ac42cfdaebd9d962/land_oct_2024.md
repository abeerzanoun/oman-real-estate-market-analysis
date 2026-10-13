# Duplicate audit — land_oct_2024

Original: `data/raw/manual/oman_land_transactions_oct_2024.xlsx`; sheet `Sheet1`, header row 1. **6,024 source occurrences; 2024-10-01–2024-10-31.**

Original SHA-256: `df278f485f7d66bab0376c38c468d4f2fad2f88a4923fd9aaa7d2e0f2af1848c`. All source-to-processed values, generated IDs, group sizes and occurrence ranks were verified. Originals and existing processed files are unchanged.

## Current repeated-group columns

`TRANSACTION_DATE`, `SERVICE_SUB_ID`, `BUYER_TYPE`, `REGION_AR`, `REGION_EN`, `WILAYAT_AR`, `WILAYAT_EN`, `VILLAGE_AR`, `VILLAGE_EN`, `RE_VALUE`, `DATE_OF_BIRTH`, `GENDER_NAME_AR`, `GENDER_NAME_EN`, `SINGLE_MULTIPLE`, `NO_OF_OWNERS`

SHA-256 of json.dumps(tuple(original decoded row), ensure_ascii=False, default=str), preserving original field order/values, no normalization. The scope is one source dataset; no cross-file pooling. Headers/metadata sheets, file/sheet/row IDs and derived fields are not part of that pattern. Nulls compare as null; no trimming, translation or normalization is used.

## Identifier assessment

**No reliable official transaction or record identifier is supplied.** Generated record_id is unique for the file/sheet/row, not evidence of unique economic events. Dates, classifications, gender/birth dates, locations, amounts and owner counts do not establish identity.

Every data column was profiled for completeness and distinct values; none is a complete unique official identity key. See source_column_identity_assessment.csv. Source values used for this assessment are not republished.

Candidate ID-named source columns: [{"column": "SERVICE_SUB_ID", "nonmissing": 6024, "distinct_nonmissing": 2, "role": "service classification code, not transaction/record identity", "reliable_unique_transaction_id": false}].

## Repetition statistics

| Criterion | Repeated groups | Occurrences in groups | Occurrences after first | Largest group |
|---|---:|---:|---:|---:|
| All original data fields | 0 | 0 | 0 | 1 |
| Exported source-derived payload | 232 | 510 | 278 | 8 |

"After first" is a pattern-occurrence statistic, **not a number approved for removal**. A full-source match is still an unresolved repetition of coarse attributes. Distinct patterns are not unique-transaction counts.

Exported payload comparison columns: `transaction_date`, `service_sub_id`, `buyer_type`, `source_region_ar`, `source_region_en`, `source_wilayat_ar`, `source_wilayat_en`, `source_village_ar`, `source_village_en`, `reported_re_value`, `ownership_mode`, `number_of_owners`.

Source fields excluded from export: `DATE_OF_BIRTH`, `GENDER_NAME_AR`, `GENDER_NAME_EN`.

**232 groups / 510 occurrences** match the exported fields but contain different full-source records. These are projection collisions, not confirmed source duplicates. Demographic differences distinguish source representations without establishing separate economic transactions.

The payload key excludes generated IDs/row ordinals, hashes, repeat flags and derived normalization keys; otherwise unique lineage would mask matches. Source-to-export checks use documented ISO-date and integer-owner conversion; raw signatures retain original decoded types. Amount equality, where present, compares original XML-derived decimal tokens; no unit, price or financial conclusion is inferred.

## Traceable actual examples

### exported_payload_equality — 8 source occurrences

Excel rows: `3910;3911;3912;3913;3914;3915;3916;3917`. Processed logical record ordinals: `3909;3910;3911;3912;3913;3914;3915;3916`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"TRANSACTION_DATE": "2024-10-22 00:00:00", "SERVICE_SUB_ID": "RN13C", "BUYER_TYPE": "Individual", "REGION_AR": "جنـوب الباطنة", "REGION_EN": "South Batinah", "WILAYAT_AR": "بركاء", "WILAYAT_EN": "Barka", "SINGLE_MULTIPLE": "Single", "NO_OF_OWNERS": 1.0}`.

Distinct full-source patterns: 8; differing omitted fields: `DATE_OF_BIRTH`. Assessment: `projection_collision_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

### exported_payload_equality — 5 source occurrences

Excel rows: `3539;3540;3541;3542;3543`. Processed logical record ordinals: `3538;3539;3540;3541;3542`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"TRANSACTION_DATE": "2024-10-20 00:00:00", "SERVICE_SUB_ID": "RN13C", "BUYER_TYPE": "Individual", "REGION_AR": "محافظـة ظفـار", "REGION_EN": "Dhofar", "WILAYAT_AR": "صلالة", "WILAYAT_EN": "Salalah", "SINGLE_MULTIPLE": "Single", "NO_OF_OWNERS": 1.0}`.

Distinct full-source patterns: 5; differing omitted fields: `DATE_OF_BIRTH`. Assessment: `projection_collision_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

### exported_payload_equality — 4 source occurrences

Excel rows: `841;842;843;844`. Processed logical record ordinals: `840;841;842;843`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"TRANSACTION_DATE": "2024-10-03 00:00:00", "SERVICE_SUB_ID": "RN13C", "BUYER_TYPE": "Individual", "REGION_AR": "مسقط", "REGION_EN": "Muscat", "WILAYAT_AR": "العامرات", "WILAYAT_EN": "Amerat", "SINGLE_MULTIPLE": "Single", "NO_OF_OWNERS": 1.0}`.

Distinct full-source patterns: 4; differing omitted fields: `DATE_OF_BIRTH;GENDER_NAME_AR;GENDER_NAME_EN`. Assessment: `projection_collision_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

## Decision and recommendations

**Retain every occurrence. Zero confirmed ingestion duplicates, zero records removed, and no cleaned dataset created.** Full processed CSV rows and original file/sheet/row lineage are unique; each original occurrence maps to exactly one audited occurrence. Legitimate same-day, same-location, same-category registrations are plausible. Their economic identity cannot be confirmed or disproved with these fields.

Request an official stable transaction ID (or documented composite business key), export-row ID and row-grain explanation, including how multiple owners appear. Obtain issuer confirmation or a revision/removal ledger before transaction-level deduplication. Never use gender, birth date, date/location or visible-row signature as a transaction key.

Existing aggregate facts preserve every occurrence count; their reduced physical rows are intentional aggregation, not record removal. In Power BI, retain separate definitions and use SUM(reported_record_count) on aggregate facts. Do not apply Remove duplicates/DISTINCT to projected attributes, count physical aggregate rows as transactions, or load raw/audited/aggregated representations into one additive fact.

Exact official workbook URLs/licences and some source definitions remain pending in the source registry. This is a duplicate-evidence audit, not certification of unique or complete-market transactions. Per-occurrence and full group ledgers accompany this report. Any future confirmed removal must be separately named and justified row-by-row; no deletion is authorized by the current evidence.
