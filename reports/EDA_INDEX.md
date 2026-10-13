# EDA artifact index

Committed run: `168665c92a8a2ff91598`. Input audit: `71008482abd46aa7f0bc`; base latest main: `2c4237a` (merged PR #4).

[Executed notebook](../notebooks/01_scoped_real_estate_eda.ipynb) · [Computed findings](eda/168665c92a8a2ff91598/insights.md) · [Methodology](../docs/eda_methodology.md) · [Analytical dictionary](../docs/eda_data_dictionary.md) · [Power BI model/DAX](../powerbi/EDA_MODEL.md)

[31 analytical CSV tables](../data/processed/eda/168665c92a8a2ff91598/) and [hash/reconciliation manifest](../data/processed/eda/168665c92a8a2ff91598/analysis_manifest.json) contain source-backed summaries and three separate monthly facts. PNG/SVG figures are available below.

| Power BI fact | Aggregate rows | Reconciled source occurrences |
|---|---:|---:|
| fact_land_2022 | 361 | 13,168 |
| fact_land_2024 | 257 | 6,024 |
| fact_brokerage_2025 | 403 | 9,366 |

Counts are retained source occurrences, not independently identified transactions. No financial KPI, missing month, annual trend or cross-family market total is generated.

| Figure | PNG | SVG |
|---|---|---|
| Reporting coverage • 2020–2026 | [Preview](figures/eda/168665c92a8a2ff91598/coverage_calendar.png) | [Vector export](figures/eda/168665c92a8a2ff91598/coverage_calendar.svg) |
| Governorate coverage • supplied datasets only | [Preview](figures/eda/168665c92a8a2ff91598/coverage_governorates.png) | [Vector export](figures/eda/168665c92a8a2ff91598/coverage_governorates.svg) |
| 2022 land records • governorate distribution | [Preview](figures/eda/168665c92a8a2ff91598/land_2022_governorates.png) | [Vector export](figures/eda/168665c92a8a2ff91598/land_2022_governorates.svg) |
| 2022 land records • change in geographic share | [Preview](figures/eda/168665c92a8a2ff91598/land_2022_share_change.png) | [Vector export](figures/eda/168665c92a8a2ff91598/land_2022_share_change.svg) |
| 2022 land records • ten highest wilayat counts per month | [Preview](figures/eda/168665c92a8a2ff91598/land_2022_wilayats.png) | [Vector export](figures/eda/168665c92a8a2ff91598/land_2022_wilayats.svg) |
| October 2024 land records • governorate distribution | [Preview](figures/eda/168665c92a8a2ff91598/land_2024_governorates.png) | [Vector export](figures/eda/168665c92a8a2ff91598/land_2024_governorates.svg) |
| October 2024 land records • ten highest wilayat counts | [Preview](figures/eda/168665c92a8a2ff91598/land_2024_wilayats.png) | [Vector export](figures/eda/168665c92a8a2ff91598/land_2024_wilayats.svg) |
| October 2024 • observed service-code mix | [Preview](figures/eda/168665c92a8a2ff91598/land_2024_service_codes.png) | [Vector export](figures/eda/168665c92a8a2ff91598/land_2024_service_codes.svg) |
| Land records • reported buyer types within each file | [Preview](figures/eda/168665c92a8a2ff91598/land_buyer_types.png) | [Vector export](figures/eda/168665c92a8a2ff91598/land_buyer_types.svg) |
| Land records • number of owners within each file | [Preview](figures/eda/168665c92a8a2ff91598/land_ownership_bands.png) | [Vector export](figures/eda/168665c92a8a2ff91598/land_ownership_bands.svg) |
| Muscat brokerage • nine supplied months of 2025 | [Preview](figures/eda/168665c92a8a2ff91598/muscat_monthly.png) | [Vector export](figures/eda/168665c92a8a2ff91598/muscat_monthly.svg) |
| Muscat brokerage • wilayat distribution, Jan–Sep 2025 | [Preview](figures/eda/168665c92a8a2ff91598/muscat_wilayats.png) | [Vector export](figures/eda/168665c92a8a2ff91598/muscat_wilayats.svg) |
| Muscat brokerage • observed property classifications | [Preview](figures/eda/168665c92a8a2ff91598/muscat_property_categories.png) | [Vector export](figures/eda/168665c92a8a2ff91598/muscat_property_categories.svg) |
| Muscat brokerage • supplied wilayat/month distribution | [Preview](figures/eda/168665c92a8a2ff91598/muscat_wilayat_monthly.png) | [Vector export](figures/eda/168665c92a8a2ff91598/muscat_wilayat_monthly.svg) |

Outputs are immutable and hash-verified; all 31 analytical CSVs match the reviewed baseline. Native rendering versions and font hashes are recorded; different environments receive distinct run IDs. Source attribution, publication/licence gaps, repeated-row limits and missing-period interpretations remain explicit in methodology and findings.
