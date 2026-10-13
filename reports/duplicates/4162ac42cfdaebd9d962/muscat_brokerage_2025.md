# Duplicate audit — muscat_brokerage_2025

Original: `data/raw/manual/muscat_brokerage_sales_2025.xlsx`; sheet `تسجيل عقد بيع - مسقط`, header row 3. **9,366 source occurrences; 2025-01-02–2025-09-30.**

Original SHA-256: `f00cabf8a4084644321dda07061167e69030091300ba8fadf3ab5eccc7c857ca`. All source-to-processed values, generated IDs, group sizes and occurrence ranks were verified. Originals and existing processed files are unchanged.

## Current repeated-group columns

`اسم المعاملة`, `الولاية`, `تاريخ الإجراء`, `نوع الإستعمال`, `وصف العقار`

SHA-256 of json.dumps(tuple(original decoded row), ensure_ascii=False, default=str), preserving original field order/values, no normalization. The scope is one source dataset; no cross-file pooling. Headers/metadata sheets, file/sheet/row IDs and derived fields are not part of that pattern. Nulls compare as null; no trimming, translation or normalization is used.

## Identifier assessment

**No reliable official transaction or record identifier is supplied.** Generated record_id is unique for the file/sheet/row, not evidence of unique economic events. Dates, classifications, gender/birth dates, locations, amounts and owner counts do not establish identity.

Every data column was profiled for completeness and distinct values; none is a complete unique official identity key. See source_column_identity_assessment.csv. Source values used for this assessment are not republished.

Candidate ID-named source columns: none.

## Repetition statistics

| Criterion | Repeated groups | Occurrences in groups | Occurrences after first | Largest group |
|---|---:|---:|---:|---:|
| All original data fields | 1396 | 8174 | 6778 | 41 |
| Exported source-derived payload | 1396 | 8174 | 6778 | 41 |

"After first" is a pattern-occurrence statistic, **not a number approved for removal**. A full-source match is still an unresolved repetition of coarse attributes. Distinct patterns are not unique-transaction counts.

Exported payload comparison columns: `transaction_category_ar`, `source_wilayat_ar`, `transaction_date`, `property_use_ar`, `property_description_ar`.

Source fields excluded from export: none.

**0 groups / 0 occurrences** match the exported fields but contain different full-source records. These are projection collisions, not confirmed source duplicates. Demographic differences distinguish source representations without establishing separate economic transactions.

The payload key excludes generated IDs/row ordinals, hashes, repeat flags and derived normalization keys; otherwise unique lineage would mask matches. Source-to-export checks use documented ISO-date and integer-owner conversion; raw signatures retain original decoded types. Amount equality, where present, compares original XML-derived decimal tokens; no unit, price or financial conclusion is inferred.

## Traceable actual examples

### full_source_equality — 41 source occurrences

Excel rows: `5860;5861;5862;5863;5864;5865;5866;5867;5868;5869;5870;5871;5872;5873;5874;5875;5876;5877;5878;5879;5880;5881;5882;5883;5884;5885;5886;5887;5888;5889;5890;5891;5892;5893;5894;5895;5897;5898;5899;5900;5901`. Processed logical record ordinals: `5857;5858;5859;5860;5861;5862;5863;5864;5865;5866;5867;5868;5869;5870;5871;5872;5873;5874;5875;5876;5877;5878;5879;5880;5881;5882;5883;5884;5885;5886;5887;5888;5889;5890;5891;5892;5894;5895;5896;5897;5898`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"اسم المعاملة": "تسجيل عقد بيع من خلال مكاتب الوساطة العقارية", "الولاية": "العامرات", "تاريخ الإجراء": "2025-08-26 00:00:00", "نوع الإستعمال": "سكني", "وصف العقار": "أرض فضاء"}`.

Distinct full-source patterns: 1; differing omitted fields: `none`. Assessment: `full_source_pattern_repetition_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

### full_source_equality — 29 source occurrences

Excel rows: `6082;6083;6084;6085;6086;6087;6088;6089;6090;6091;6092;6093;6094;6095;6096;6097;6098;6100;6101;6102;6103;6104;6105;6106;6107;6108;6109;6110;6111`. Processed logical record ordinals: `6079;6080;6081;6082;6083;6084;6085;6086;6087;6088;6089;6090;6091;6092;6093;6094;6095;6097;6098;6099;6100;6101;6102;6103;6104;6105;6106;6107;6108`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"اسم المعاملة": "تسجيل عقد بيع من خلال مكاتب الوساطة العقارية", "الولاية": "العامرات", "تاريخ الإجراء": "2025-09-11 00:00:00", "نوع الإستعمال": "سكني", "وصف العقار": "أرض فضاء"}`.

Distinct full-source patterns: 1; differing omitted fields: `none`. Assessment: `full_source_pattern_repetition_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

### full_source_equality — 28 source occurrences

Excel rows: `4737;4738;4739;4740;4741;4742;4743;4744;4745;4746;4747;4749;4750;4751;4752;4753;4754;4755;4756;4758;4759;4760;4761;4762;4763;4764;4765;4766`. Processed logical record ordinals: `4734;4735;4736;4737;4738;4739;4740;4741;4742;4743;4744;4746;4747;4748;4749;4750;4751;4752;4753;4755;4756;4757;4758;4759;4760;4761;4762;4763`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"اسم المعاملة": "تسجيل عقد بيع من خلال مكاتب الوساطة العقارية", "الولاية": "العامرات", "تاريخ الإجراء": "2025-05-18 00:00:00", "نوع الإستعمال": "سكني", "وصف العقار": "أرض فضاء"}`.

Distinct full-source patterns: 1; differing omitted fields: `none`. Assessment: `full_source_pattern_repetition_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

### exported_payload_equality — 41 source occurrences

Excel rows: `5860;5861;5862;5863;5864;5865;5866;5867;5868;5869;5870;5871;5872;5873;5874;5875;5876;5877;5878;5879;5880;5881;5882;5883;5884;5885;5886;5887;5888;5889;5890;5891;5892;5893;5894;5895;5897;5898;5899;5900;5901`. Processed logical record ordinals: `5857;5858;5859;5860;5861;5862;5863;5864;5865;5866;5867;5868;5869;5870;5871;5872;5873;5874;5875;5876;5877;5878;5879;5880;5881;5882;5883;5884;5885;5886;5887;5888;5889;5890;5891;5892;5894;5895;5896;5897;5898`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"اسم المعاملة": "تسجيل عقد بيع من خلال مكاتب الوساطة العقارية", "الولاية": "العامرات", "تاريخ الإجراء": "2025-08-26 00:00:00", "نوع الإستعمال": "سكني", "وصف العقار": "أرض فضاء"}`.

Distinct full-source patterns: 1; differing omitted fields: `none`. Assessment: `full_source_pattern_repetition_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

### exported_payload_equality — 29 source occurrences

Excel rows: `6082;6083;6084;6085;6086;6087;6088;6089;6090;6091;6092;6093;6094;6095;6096;6097;6098;6100;6101;6102;6103;6104;6105;6106;6107;6108;6109;6110;6111`. Processed logical record ordinals: `6079;6080;6081;6082;6083;6084;6085;6086;6087;6088;6089;6090;6091;6092;6093;6094;6095;6097;6098;6099;6100;6101;6102;6103;6104;6105;6106;6107;6108`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"اسم المعاملة": "تسجيل عقد بيع من خلال مكاتب الوساطة العقارية", "الولاية": "العامرات", "تاريخ الإجراء": "2025-09-11 00:00:00", "نوع الإستعمال": "سكني", "وصف العقار": "أرض فضاء"}`.

Distinct full-source patterns: 1; differing omitted fields: `none`. Assessment: `full_source_pattern_repetition_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

### exported_payload_equality — 28 source occurrences

Excel rows: `4737;4738;4739;4740;4741;4742;4743;4744;4745;4746;4747;4749;4750;4751;4752;4753;4754;4755;4756;4758;4759;4760;4761;4762;4763;4764;4765;4766`. Processed logical record ordinals: `4734;4735;4736;4737;4738;4739;4740;4741;4742;4743;4744;4746;4747;4748;4749;4750;4751;4752;4753;4755;4756;4757;4758;4759;4760;4761;4762;4763`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"اسم المعاملة": "تسجيل عقد بيع من خلال مكاتب الوساطة العقارية", "الولاية": "العامرات", "تاريخ الإجراء": "2025-05-18 00:00:00", "نوع الإستعمال": "سكني", "وصف العقار": "أرض فضاء"}`.

Distinct full-source patterns: 1; differing omitted fields: `none`. Assessment: `full_source_pattern_repetition_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

## Decision and recommendations

**Retain every occurrence. Zero confirmed ingestion duplicates, zero records removed, and no cleaned dataset created.** Full processed CSV rows and original file/sheet/row lineage are unique; each original occurrence maps to exactly one audited occurrence. Legitimate same-day, same-location, same-category registrations are plausible. Their economic identity cannot be confirmed or disproved with these fields.

Request an official stable transaction ID (or documented composite business key), export-row ID and row-grain explanation, including how multiple owners appear. Obtain issuer confirmation or a revision/removal ledger before transaction-level deduplication. Never use gender, birth date, date/location or visible-row signature as a transaction key.

Existing aggregate facts preserve every occurrence count; their reduced physical rows are intentional aggregation, not record removal. In Power BI, retain separate definitions and use SUM(reported_record_count) on aggregate facts. Do not apply Remove duplicates/DISTINCT to projected attributes, count physical aggregate rows as transactions, or load raw/audited/aggregated representations into one additive fact.

Exact official workbook URLs/licences and some source definitions remain pending in the source registry. This is a duplicate-evidence audit, not certification of unique or complete-market transactions. Per-occurrence and full group ledgers accompany this report. Any future confirmed removal must be separately named and justified row-by-row; no deletion is authorized by the current evidence.
