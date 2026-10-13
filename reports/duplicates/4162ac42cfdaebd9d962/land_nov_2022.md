# Duplicate audit — land_nov_2022

Original: `data/raw/manual/oman_land_transactions_nov_2022.xlsx`; sheet `BuySell`, header row 1. **7,501 source occurrences; 2022-11-01–2022-11-29.**

Original SHA-256: `80b8c39857e6379b72960342574feb721b55007e1d95bcd37db7f473768edf8a`. All source-to-processed values, generated IDs, group sizes and occurrence ranks were verified. Originals and existing processed files are unchanged.

## Current repeated-group columns

`TRANSACTION_DATE`, `BUYER_TYPE`, `REGION_AR`, `REGION_EN`, `WILAYAT_AR`, `WILAYAT_EN`, `VILLAGE_AR`, `VILLAGE_EN`, `GENDER_NAME_AR`, `GENDER_NAME_EN`, `NO_OF_OWNERS`

SHA-256 of json.dumps(tuple(original decoded row), ensure_ascii=False, default=str), preserving original field order/values, no normalization. The scope is one source dataset; no cross-file pooling. Headers/metadata sheets, file/sheet/row IDs and derived fields are not part of that pattern. Nulls compare as null; no trimming, translation or normalization is used.

## Identifier assessment

**No reliable official transaction or record identifier is supplied.** Generated record_id is unique for the file/sheet/row, not evidence of unique economic events. Dates, classifications, gender/birth dates, locations, amounts and owner counts do not establish identity.

Every data column was profiled for completeness and distinct values; none is a complete unique official identity key. See source_column_identity_assessment.csv. Source values used for this assessment are not republished.

Candidate ID-named source columns: none.

## Repetition statistics

| Criterion | Repeated groups | Occurrences in groups | Occurrences after first | Largest group |
|---|---:|---:|---:|---:|
| All original data fields | 1046 | 3675 | 2629 | 49 |
| Exported source-derived payload | 1094 | 4170 | 3076 | 59 |

"After first" is a pattern-occurrence statistic, **not a number approved for removal**. A full-source match is still an unresolved repetition of coarse attributes. Distinct patterns are not unique-transaction counts.

Exported payload comparison columns: `transaction_date`, `buyer_type`, `source_region_ar`, `source_region_en`, `source_wilayat_ar`, `source_wilayat_en`, `source_village_ar`, `source_village_en`, `number_of_owners`.

Source fields excluded from export: `GENDER_NAME_AR`, `GENDER_NAME_EN`.

**437 groups / 2391 occurrences** match the exported fields but contain different full-source records. These are projection collisions, not confirmed source duplicates. Demographic differences distinguish source representations without establishing separate economic transactions.

The payload key excludes generated IDs/row ordinals, hashes, repeat flags and derived normalization keys; otherwise unique lineage would mask matches. Source-to-export checks use documented ISO-date and integer-owner conversion; raw signatures retain original decoded types. Amount equality, where present, compares original XML-derived decimal tokens; no unit, price or financial conclusion is inferred.

## Traceable actual examples

### full_source_equality — 49 source occurrences

Excel rows: `129;131;136;584;594;1045;1258;1484;1486;1493;1740;1744;1747;1969;1973;2211;2213;2214;2451;2675;2684;2921;3159;3162;3369;3371;3607;3850;3860;4087;4570;4804;4811;4812;5042;5266;5277;5493;5739;5746;6201;6460;6692;6695;6697;6934;6936;7189;7394`. Processed logical record ordinals: `128;130;135;583;593;1044;1257;1483;1485;1492;1739;1743;1746;1968;1972;2210;2212;2213;2450;2674;2683;2920;3158;3161;3368;3370;3606;3849;3859;4086;4569;4803;4810;4811;5041;5265;5276;5492;5738;5745;6200;6459;6691;6694;6696;6933;6935;7188;7393`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"TRANSACTION_DATE": "2022-11-22 00:00:00", "BUYER_TYPE": "Individual", "REGION_AR": "الـداخليـة", "REGION_EN": "AlDakhliah", "WILAYAT_AR": "نزوى", "WILAYAT_EN": "Nizwa", "NO_OF_OWNERS": 1.0}`.

Distinct full-source patterns: 1; differing omitted fields: `none`. Assessment: `full_source_pattern_repetition_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

### full_source_equality — 32 source occurrences

Excel rows: `79;1000;1444;1690;1926;2631;2863;2867;2870;3112;3113;3320;3561;3562;4038;4286;4287;4528;4762;5228;5229;5694;5923;5924;6406;6407;6408;6411;6897;6901;7148;7150`. Processed logical record ordinals: `78;999;1443;1689;1925;2630;2862;2866;2869;3111;3112;3319;3560;3561;4037;4285;4286;4527;4761;5227;5228;5693;5922;5923;6405;6406;6407;6410;6896;6900;7147;7149`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"TRANSACTION_DATE": "2022-11-14 00:00:00", "BUYER_TYPE": "Individual", "REGION_AR": "الـداخليـة", "REGION_EN": "AlDakhliah", "WILAYAT_AR": "نزوى", "WILAYAT_EN": "Nizwa", "NO_OF_OWNERS": 1.0}`.

Distinct full-source patterns: 1; differing omitted fields: `none`. Assessment: `full_source_pattern_repetition_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

### full_source_equality — 31 source occurrences

Excel rows: `53;282;286;493;1187;1189;1412;1653;1892;2135;2136;2376;2586;2593;3074;3076;3521;3525;3768;4497;4718;4723;4961;5187;5189;5654;5888;5896;6374;7102;7110`. Processed logical record ordinals: `52;281;285;492;1186;1188;1411;1652;1891;2134;2135;2375;2585;2592;3073;3075;3520;3524;3767;4496;4717;4722;4960;5186;5188;5653;5887;5895;6373;7101;7109`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"TRANSACTION_DATE": "2022-11-08 00:00:00", "BUYER_TYPE": "Individual", "REGION_AR": "الـداخليـة", "REGION_EN": "AlDakhliah", "WILAYAT_AR": "ادم", "WILAYAT_EN": "Adam", "NO_OF_OWNERS": 1.0}`.

Distinct full-source patterns: 1; differing omitted fields: `none`. Assessment: `full_source_pattern_repetition_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

### exported_payload_equality — 59 source occurrences

Excel rows: `129;131;133;136;584;590;594;1045;1046;1258;1484;1486;1493;1740;1744;1747;1969;1973;2211;2213;2214;2216;2218;2451;2675;2684;2685;2921;3159;3162;3369;3371;3373;3607;3850;3860;4085;4087;4098;4570;4804;4811;4812;5042;5266;5277;5493;5739;5746;6201;6460;6689;6692;6695;6697;6934;6936;7189;7394`. Processed logical record ordinals: `128;130;132;135;583;589;593;1044;1045;1257;1483;1485;1492;1739;1743;1746;1968;1972;2210;2212;2213;2215;2217;2450;2674;2683;2684;2920;3158;3161;3368;3370;3372;3606;3849;3859;4084;4086;4097;4569;4803;4810;4811;5041;5265;5276;5492;5738;5745;6200;6459;6688;6691;6694;6696;6933;6935;7188;7393`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"TRANSACTION_DATE": "2022-11-22 00:00:00", "BUYER_TYPE": "Individual", "REGION_AR": "الـداخليـة", "REGION_EN": "AlDakhliah", "WILAYAT_AR": "نزوى", "WILAYAT_EN": "Nizwa", "NO_OF_OWNERS": 1.0}`.

Distinct full-source patterns: 2; differing omitted fields: `GENDER_NAME_AR;GENDER_NAME_EN`. Assessment: `projection_collision_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

### exported_payload_equality — 40 source occurrences

Excel rows: `53;280;282;286;493;752;1187;1189;1412;1653;1892;2135;2136;2376;2586;2593;3074;3076;3521;3525;3526;3768;4252;4497;4718;4723;4950;4961;5187;5189;5195;5654;5887;5888;5889;5896;6374;6856;7102;7110`. Processed logical record ordinals: `52;279;281;285;492;751;1186;1188;1411;1652;1891;2134;2135;2375;2585;2592;3073;3075;3520;3524;3525;3767;4251;4496;4717;4722;4949;4960;5186;5188;5194;5653;5886;5887;5888;5895;6373;6855;7101;7109`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"TRANSACTION_DATE": "2022-11-08 00:00:00", "BUYER_TYPE": "Individual", "REGION_AR": "الـداخليـة", "REGION_EN": "AlDakhliah", "WILAYAT_AR": "ادم", "WILAYAT_EN": "Adam", "NO_OF_OWNERS": 1.0}`.

Distinct full-source patterns: 2; differing omitted fields: `GENDER_NAME_AR;GENDER_NAME_EN`. Assessment: `projection_collision_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

### exported_payload_equality — 33 source occurrences

Excel rows: `79;1000;1444;1690;1926;2631;2863;2867;2870;3112;3113;3320;3561;3562;4038;4286;4287;4528;4762;5228;5229;5694;5923;5924;6406;6407;6408;6411;6892;6897;6901;7148;7150`. Processed logical record ordinals: `78;999;1443;1689;1925;2630;2862;2866;2869;3111;3112;3319;3560;3561;4037;4285;4286;4527;4761;5227;5228;5693;5922;5923;6405;6406;6407;6410;6891;6896;6900;7147;7149`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"TRANSACTION_DATE": "2022-11-14 00:00:00", "BUYER_TYPE": "Individual", "REGION_AR": "الـداخليـة", "REGION_EN": "AlDakhliah", "WILAYAT_AR": "نزوى", "WILAYAT_EN": "Nizwa", "NO_OF_OWNERS": 1.0}`.

Distinct full-source patterns: 2; differing omitted fields: `GENDER_NAME_AR;GENDER_NAME_EN`. Assessment: `projection_collision_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

## Decision and recommendations

**Retain every occurrence. Zero confirmed ingestion duplicates, zero records removed, and no cleaned dataset created.** Full processed CSV rows and original file/sheet/row lineage are unique; each original occurrence maps to exactly one audited occurrence. Legitimate same-day, same-location, same-category registrations are plausible. Their economic identity cannot be confirmed or disproved with these fields.

Request an official stable transaction ID (or documented composite business key), export-row ID and row-grain explanation, including how multiple owners appear. Obtain issuer confirmation or a revision/removal ledger before transaction-level deduplication. Never use gender, birth date, date/location or visible-row signature as a transaction key.

Existing aggregate facts preserve every occurrence count; their reduced physical rows are intentional aggregation, not record removal. In Power BI, retain separate definitions and use SUM(reported_record_count) on aggregate facts. Do not apply Remove duplicates/DISTINCT to projected attributes, count physical aggregate rows as transactions, or load raw/audited/aggregated representations into one additive fact.

Exact official workbook URLs/licences and some source definitions remain pending in the source registry. This is a duplicate-evidence audit, not certification of unique or complete-market transactions. Per-occurrence and full group ledgers accompany this report. Any future confirmed removal must be separately named and justified row-by-row; no deletion is authorized by the current evidence.
