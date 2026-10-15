# Coverage and interpretation contract

The **research target** is 2020–2026. The actual uploaded records cover the snapshots below. A file's first/last date describes observed rows, not proof of complete reporting on all days between those dates.

| File / dataset_id | Observed dates | Supplied months | Geography | Retained occurrences |
|---|---|---|---|---:|
| land_nov_2022 | 2022-11-01–2022-11-29 | Nov 2022 | 11 governorates; 62 observed wilayat labels | 7,501 |
| land_dec_2022 | 2022-12-04–2022-12-29 | Dec 2022 | 11 governorates; 61 observed wilayat labels | 5,667 |
| land_oct_2024 | 2024-10-01–2024-10-31 | Oct 2024 | 11 governorates; 63 observed wilayat labels | 6,024 |
| muscat_brokerage_2025 | 2025-01-02–2025-09-30 | Jan–Sep 2025 | Muscat only; six observed wilayats | 9,366 |

The 2022 observed labels include `الساحل الشرقي` (one row in each file), a nonstandard Dhofar label retained and flagged. Neither observed label counts nor representation of all 11 governorates establish complete wilayat or national market capture. The shared dimension has 65 observed wilayat keys; it is not an official exhaustive administrative register. Legacy Al Sharqiyah source labels were mapped to modern governorates with the reviewed wilayat crosswalk; the Power BI imports do not redo that mapping.

## Missing periods

There are no uploaded observations for **2020, 2021, 2023 or 2026**. The land 2022 scope has no supplied Jan–Oct months; the land 2024 scope has only October. No cross-scope trend links them. Brokerage has no supplied Oct–Dec 2025, covers only Muscat, and is not a national sales register. Other months in the 2020–2026 research window are absent for each scope unless explicitly observed. Do not extend the Jan–Sep chart to a full year with zeros or annualize it.

The committed `coverage_matrix_2020_2026` is a **2026-10-13 audit snapshot**, not a live calendar. It contains 2,772 scope × governorate × year × month metadata cells:

| Status | Cells | Display / meaning |
|---|---:|---|
| observed | 42 | Teal; at least one uploaded occurrence, not complete reporting certification |
| not_provided | 1,844 | Amber; file/month not supplied, count blank |
| outside_source_scope | 840 | Gray; non-Muscat governorates outside brokerage scope, count blank |
| future_period | 46 | Pale blue; month starts after the audit snapshot, count blank |

Future November/December 2026 metadata cells are not forecasts or missing transactions. The current October 2026 month is not complete and has no supplied observations. All 2,730 non-observed counts remain blank. “Missing files” is not “zero activity.” The 42 cells must not be divided by the entire grid and labelled Oman market completeness: scopes have different populations and geographic domains.

## Definitions, amounts and provenance

- 2022 has a BuySell-layout source; 2024 has raw service codes **RN13A (599 occurrences)** and **RN13C (5,425)**, whose official meanings remain unverified. Do not relabel them sale/mortgage or compare them as equivalent to 2022.
- The 2024 source field `RE_VALUE` has 5,657 present and 367 missing tokens. Its meaning and currency/unit are unverified. It is excluded from analytical fact imports. The counts of present/missing tokens in quality metadata are **record counts, not amounts**. Other files have no such amount field: their quality counts are null, not zero.
- Brokerage property-use and description categories are observed Arabic labels (eight uses, thirteen descriptions), not comparable land-use attributes from the two land layouts. The brokerage transaction category is constant: `تسجيل عقد بيع من خلال مكاتب الوساطة العقارية`.
- No trustworthy official unique event ID is present. All source occurrences were retained; zero removals were justified by the completed duplicate audit. Same attributes do not prove duplicate transactions. Cross-file unique economic event counts cannot be determined.
- None of the four exact official resource URLs or redistribution licences has been independently established. Brokerage has embedded provider attribution; the three land workbooks have user-declared Ministry attribution. Recorded provider entry points are discovery leads, not verified exact file downloads. See the authoritative [DATA_PROVENANCE_AUDIT.md](../DATA_PROVENANCE_AUDIT.md) and [source registry](../docs/uploaded_source_registry.json).
- No verified price, currency, area-normalized value, continuous annual series or investment outcome exists. No price ranking, financial KPI, annual growth, forecast or investment recommendation is supported.

Supported uses: source-occurrence distributions within comparable populations/months, explicitly caveated Nov/Dec 2022 file comparison, October 2024 raw service mix, Muscat Jan–Sep 2025 registration/property mix, and transparent coverage/quality/provenance reporting.
