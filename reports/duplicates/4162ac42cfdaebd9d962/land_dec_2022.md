# Duplicate audit — land_dec_2022

Original: `data/raw/manual/oman_land_transactions_dec_2022.xlsx`; sheet `BuySell`, header row 1. **5,667 source occurrences; 2022-12-04–2022-12-29.**

Original SHA-256: `fd52d06d8a678597f1cb437cea8510777ac379886e9aa640c955cf0ee0389202`. All source-to-processed values, generated IDs, group sizes and occurrence ranks were verified. Originals and existing processed files are unchanged.

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
| All original data fields | 757 | 2600 | 1843 | 44 |
| Exported source-derived payload | 804 | 2942 | 2138 | 51 |

"After first" is a pattern-occurrence statistic, **not a number approved for removal**. A full-source match is still an unresolved repetition of coarse attributes. Distinct patterns are not unique-transaction counts.

Exported payload comparison columns: `transaction_date`, `buyer_type`, `source_region_ar`, `source_region_en`, `source_wilayat_ar`, `source_wilayat_en`, `source_village_ar`, `source_village_en`, `number_of_owners`.

Source fields excluded from export: `GENDER_NAME_AR`, `GENDER_NAME_EN`.

**286 groups / 1604 occurrences** match the exported fields but contain different full-source records. These are projection collisions, not confirmed source duplicates. Demographic differences distinguish source representations without establishing separate economic transactions.

The payload key excludes generated IDs/row ordinals, hashes, repeat flags and derived normalization keys; otherwise unique lineage would mask matches. Source-to-export checks use documented ISO-date and integer-owner conversion; raw signatures retain original decoded types. Amount equality, where present, compares original XML-derived decimal tokens; no unit, price or financial conclusion is inferred.

## Traceable actual examples

### full_source_equality — 44 source occurrences

Excel rows: `31;208;210;387;549;942;1263;1266;1267;1442;1443;1602;1780;1943;1945;1946;1948;1950;1951;2130;2131;2292;2293;2302;2484;2487;3024;3410;3579;3580;3917;4088;4089;4271;4440;4441;4443;4613;4616;4790;4792;4969;5346;5526`. Processed logical record ordinals: `7531;7708;7710;7887;8049;8442;8763;8766;8767;8942;8943;9102;9280;9443;9445;9446;9448;9450;9451;9630;9631;9792;9793;9802;9984;9987;10524;10910;11079;11080;11417;11588;11589;11771;11940;11941;11943;12113;12116;12290;12292;12469;12846;13026`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"TRANSACTION_DATE": "2022-12-07 00:00:00", "BUYER_TYPE": "Individual", "REGION_AR": "الـداخليـة", "REGION_EN": "AlDakhliah", "WILAYAT_AR": "نزوى", "WILAYAT_EN": "Nizwa", "NO_OF_OWNERS": 1.0}`.

Distinct full-source patterns: 1; differing omitted fields: `none`. Assessment: `full_source_pattern_repetition_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

### full_source_equality — 37 source occurrences

Excel rows: `115;374;531;533;535;541;723;726;930;932;1086;1087;1254;1432;1768;2265;2272;2469;2471;2646;2652;2843;3572;3744;3898;3901;4076;4078;4249;4419;4420;4601;4603;4957;5137;5139;5510`. Processed logical record ordinals: `7615;7874;8031;8033;8035;8041;8223;8226;8430;8432;8586;8587;8754;8932;9268;9765;9772;9969;9971;10146;10152;10343;11072;11244;11398;11401;11576;11578;11749;11919;11920;12101;12103;12457;12637;12639;13010`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"TRANSACTION_DATE": "2022-12-05 00:00:00", "BUYER_TYPE": "Individual", "REGION_AR": "الـداخليـة", "REGION_EN": "AlDakhliah", "WILAYAT_AR": "نزوى(نيابة بركة الموز)", "WILAYAT_EN": "Nizwa (Neyaba Brakat Al Mooz)", "NO_OF_OWNERS": 1.0}`.

Distinct full-source patterns: 1; differing omitted fields: `none`. Assessment: `full_source_pattern_repetition_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

### full_source_equality — 36 source occurrences

Excel rows: `27;205;733;739;1099;1939;2129;2278;2281;2289;2480;2654;2657;3016;3018;3022;3205;3206;3207;3402;3403;3574;3575;3749;3750;3910;3913;4086;4432;4436;4611;4962;5146;5338;5518;5523`. Processed logical record ordinals: `7527;7705;8233;8239;8599;9439;9629;9778;9781;9789;9980;10154;10157;10516;10518;10522;10705;10706;10707;10902;10903;11074;11075;11249;11250;11410;11413;11586;11932;11936;12111;12462;12646;12838;13018;13023`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"TRANSACTION_DATE": "2022-12-06 00:00:00", "BUYER_TYPE": "Individual", "REGION_AR": "الـداخليـة", "REGION_EN": "AlDakhliah", "WILAYAT_AR": "نزوى", "WILAYAT_EN": "Nizwa", "NO_OF_OWNERS": 1.0}`.

Distinct full-source patterns: 1; differing omitted fields: `none`. Assessment: `full_source_pattern_repetition_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

### exported_payload_equality — 51 source occurrences

Excel rows: `31;208;210;387;549;743;942;1263;1266;1267;1442;1443;1602;1604;1780;1943;1945;1946;1948;1950;1951;2130;2131;2292;2293;2297;2302;2483;2484;2487;3024;3031;3213;3410;3579;3580;3917;4088;4089;4271;4440;4441;4443;4613;4616;4617;4790;4792;4969;5346;5526`. Processed logical record ordinals: `7531;7708;7710;7887;8049;8243;8442;8763;8766;8767;8942;8943;9102;9104;9280;9443;9445;9446;9448;9450;9451;9630;9631;9792;9793;9797;9802;9983;9984;9987;10524;10531;10713;10910;11079;11080;11417;11588;11589;11771;11940;11941;11943;12113;12116;12117;12290;12292;12469;12846;13026`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"TRANSACTION_DATE": "2022-12-07 00:00:00", "BUYER_TYPE": "Individual", "REGION_AR": "الـداخليـة", "REGION_EN": "AlDakhliah", "WILAYAT_AR": "نزوى", "WILAYAT_EN": "Nizwa", "NO_OF_OWNERS": 1.0}`.

Distinct full-source patterns: 2; differing omitted fields: `GENDER_NAME_AR;GENDER_NAME_EN`. Assessment: `projection_collision_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

### exported_payload_equality — 50 source occurrences

Excel rows: `24;192;198;375;532;928;931;934;1088;1091;1092;1095;1096;1248;1430;1590;1592;1593;1767;1933;2263;2269;2475;2649;2840;2842;3003;3004;3006;3007;3200;3390;3396;3741;3743;3899;3904;3905;4422;4600;4604;4605;4778;4781;4951;4956;5324;5511;5512;5514`. Processed logical record ordinals: `7524;7692;7698;7875;8032;8428;8431;8434;8588;8591;8592;8595;8596;8748;8930;9090;9092;9093;9267;9433;9763;9769;9975;10149;10340;10342;10503;10504;10506;10507;10700;10890;10896;11241;11243;11399;11404;11405;11922;12100;12104;12105;12278;12281;12451;12456;12824;13011;13012;13014`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"TRANSACTION_DATE": "2022-12-05 00:00:00", "BUYER_TYPE": "Individual", "REGION_AR": "جنـوب الباطنة", "REGION_EN": "South Batinah", "WILAYAT_AR": "بركاء", "WILAYAT_EN": "Barka", "NO_OF_OWNERS": 1.0}`.

Distinct full-source patterns: 2; differing omitted fields: `GENDER_NAME_AR;GENDER_NAME_EN`. Assessment: `projection_collision_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

### exported_payload_equality — 43 source occurrences

Excel rows: `115;374;531;533;535;540;541;723;726;930;932;1086;1087;1247;1254;1432;1766;1768;2265;2272;2465;2469;2471;2646;2652;2843;3572;3744;3898;3901;4076;4078;4084;4249;4419;4420;4601;4602;4603;4957;5137;5139;5510`. Processed logical record ordinals: `7615;7874;8031;8033;8035;8040;8041;8223;8226;8430;8432;8586;8587;8747;8754;8932;9266;9268;9765;9772;9965;9969;9971;10146;10152;10343;11072;11244;11398;11401;11576;11578;11584;11749;11919;11920;12101;12102;12103;12457;12637;12639;13010`. Ordinals exclude the CSV header and are not physical line numbers (quoted labels can contain line breaks).

Selected shared source fields: `{"TRANSACTION_DATE": "2022-12-05 00:00:00", "BUYER_TYPE": "Individual", "REGION_AR": "الـداخليـة", "REGION_EN": "AlDakhliah", "WILAYAT_AR": "نزوى(نيابة بركة الموز)", "WILAYAT_EN": "Nizwa (Neyaba Brakat Al Mooz)", "NO_OF_OWNERS": 1.0}`.

Distinct full-source patterns: 2; differing omitted fields: `GENDER_NAME_AR;GENDER_NAME_EN`. Assessment: `projection_collision_identity_unresolved`.

No birth date, gender, village or monetary token values are displayed; comparisons used the actual fields.

## Decision and recommendations

**Retain every occurrence. Zero confirmed ingestion duplicates, zero records removed, and no cleaned dataset created.** Full processed CSV rows and original file/sheet/row lineage are unique; each original occurrence maps to exactly one audited occurrence. Legitimate same-day, same-location, same-category registrations are plausible. Their economic identity cannot be confirmed or disproved with these fields.

Request an official stable transaction ID (or documented composite business key), export-row ID and row-grain explanation, including how multiple owners appear. Obtain issuer confirmation or a revision/removal ledger before transaction-level deduplication. Never use gender, birth date, date/location or visible-row signature as a transaction key.

Existing aggregate facts preserve every occurrence count; their reduced physical rows are intentional aggregation, not record removal. In Power BI, retain separate definitions and use SUM(reported_record_count) on aggregate facts. Do not apply Remove duplicates/DISTINCT to projected attributes, count physical aggregate rows as transactions, or load raw/audited/aggregated representations into one additive fact.

Exact official workbook URLs/licences and some source definitions remain pending in the source registry. This is a duplicate-evidence audit, not certification of unique or complete-market transactions. Per-occurrence and full group ledgers accompany this report. Any future confirmed removal must be separately named and justified row-by-row; no deletion is authorized by the current evidence.
