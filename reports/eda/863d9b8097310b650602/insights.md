# Exploratory findings — supplied record occurrences

Analysis run `863d9b8097310b650602`; input audit `71008482abd46aa7f0bc`; base main `2c4237a` (merged PR #4).

**Interpretation:** counts describe uploaded source record occurrences. Completeness and unique transaction identity are unverified; repeated visible rows remain. The three scopes are never pooled into a national sales series. No monetary or price conclusion is calculated.

## Data used

| dataset_id | reported_record_count | first_record_date | last_record_date | observed_governorates | observed_wilayat_labels |
| --- | --- | --- | --- | --- | --- |
| land_dec_2022 | 5667 | 2022-12-04 | 2022-12-29 | 11 | 61 |
| land_nov_2022 | 7501 | 2022-11-01 | 2022-11-29 | 11 | 62 |
| land_oct_2024 | 6024 | 2024-10-01 | 2024-10-31 | 11 | 63 |
| muscat_brokerage_2025 | 9366 | 2025-01-02 | 2025-09-30 | 1 | 6 |

All four originals and every audited artifact match their pinned checksums. The land months represent all eleven modern governorates; the 2025 dataset covers Muscat only. Its nine months are not full-year coverage. Wilayat-label totals include nonstandard source labels, not a certified administrative inventory.

## 2022 land: two same-layout monthly snapshots

November has **7,501** reported rows and December **5,667**: a difference of **-1,834** (-24.45% relative to the November file). This is a supplied-file comparison, not verified market contraction or an annual trend.

- 2022-11: **Ad Dakhiliyah** has 1,301 rows (17.34% of that file).
- 2022-12: **Ad Dakhiliyah** has 1,075 rows (18.97% of that file).

November’s top two are Ad Dakhiliyah (1,301) and North Ash Sharqiyah (1,300), separated by 1 row(s); the rank alone does not establish a substantive market distinction. December’s geographic composition differs from November:

| governorate_en | november_records | december_records | november_share_pct | december_share_pct | share_change_percentage_points |
| --- | --- | --- | --- | --- | --- |
| Al Wusta | 105 | 294 | 1.40 | 5.19 | 3.79 |
| South Al Batinah | 1053 | 909 | 14.04 | 16.04 | 2.00 |
| Ad Dakhiliyah | 1301 | 1075 | 17.34 | 18.97 | 1.63 |
| North Al Batinah | 954 | 760 | 12.72 | 13.41 | 0.69 |
| Al Buraimi | 212 | 196 | 2.83 | 3.46 | 0.63 |
| South Ash Sharqiyah | 402 | 330 | 5.36 | 5.82 | 0.46 |
| Muscat | 960 | 734 | 12.80 | 12.95 | 0.15 |
| Musandam | 34 | 23 | 0.45 | 0.41 | -0.05 |
| Adh Dhahirah | 309 | 208 | 4.12 | 3.67 | -0.45 |
| Dhofar | 871 | 432 | 11.61 | 7.62 | -3.99 |
| North Ash Sharqiyah | 1300 | 706 | 17.33 | 12.46 | -4.87 |

Share shifts are percentage points, not property appreciation. Different source coverage or record-generation processes could affect these patterns. Two Dhofar rows labelled الساحل الشرقي are excluded only from wilayat rankings; all source rows remain in governorate totals. The complete observed wilayat table accompanies the top-ten charts.

## October 2024 land: separate service-coded snapshot

**North Al Batinah** has the highest supplied count (1,143; 18.97%). The top three are North Al Batinah, Muscat, South Al Batinah, with 3,325 rows (55.20% of the October file). This is a within-file concentration measure, not a cross-year trend or investment ranking.

| service_sub_id | reported_record_count | share_pct |
| --- | --- | --- |
| RN13A | 599 | 9.94 |
| RN13C | 5425 | 90.06 |

RN13A/RN13C are literal service codes with unverified meanings; neither is classified as sales, mortgages or another economic category. RE_VALUE contains 5,657 reported numbers and 367 blanks. Units and meanings are unresolved, so amounts are excluded from analytical facts and DAX calculations.

## Muscat brokerage: January–September 2025

**9,366** brokerage-office registrations are present. The highest supplied month is **2025-07**, with **1,277** rows, and the lowest is **2025-06**, with **816**. No missing month or year-end projection is created. Seasonality is not established by one partial year.

Wilayats **السيب and العامرات** together account for **6,349** rows (**67.79%**). This describes geographic distribution inside the brokerage scope; it does not establish national demand or investment returns.

The original residential-use label **سكني** appears on **8,202** rows (**87.57%**). The separate vacant-land description **أرض فضاء** appears on **6,839** (**73.02%**). Use and description are different fields and must not be added together as categories of one classification.

8 property-use labels, 13 property-description labels and 1 registration-category label(s) are supplied. Raw Arabic labels are preserved. Category distributions describe registered records, not the stock, supply or prices of all properties.

## Buyer and ownership attributes

| period_id | buyer_type | reported_record_count | share_pct |
| --- | --- | --- | --- |
| 2022-12 | Company | 35 | 0.62 |
| 2022-12 | Individual | 5632 | 99.38 |
| 2022-11 | Company | 54 | 0.72 |
| 2022-11 | Individual | 7447 | 99.28 |
| 2024-10 | Company | 17 | 0.28 |
| 2024-10 | Individual | 6007 | 99.72 |

Individual is the predominant reported buyer label in each file. Owner-count bands measure ownership multiplicity; they are not independent buyers, transaction counts or property prices. Five or more owners are grouped explicitly for readable distributions.

## Reliability and recommended decisions

1. Use regional and category distributions to prioritize further official data verification and investigation within each supplied scope. These files alone do not support investment recommendations.
2. Obtain complete comparable monthly series before trend, seasonality or annual-growth analysis. No 2020, 2021, 2023 or 2026 uploads exist; 2022 and 2024 are isolated land snapshots; 2025 brokerage is Muscat-only and partial year.
3. Confirm source URLs/licences, land-file publication dates, source completeness, transaction identity, service definitions and financial units before broader or monetary conclusions. Muscat’s embedded publication label predates some records.
4. Keep Power BI pages and measures separate by dataset definition. Count occurrences with SUM of the prepared count field; do not count aggregated fact rows or sum owner numbers as transactions.

Figures are generated by pandas/Matplotlib/Seaborn, and their chart-data tables are committed beside the Power BI facts. Methodology, transformations and provenance are documented in `docs/eda_methodology.md` and the source registry. All counts/shares reconcile; no originals are modified.
