# Measure definitions and validation boundaries

[EDA_MEASURES.dax](EDA_MEASURES.dax) is the source of truth for 17 definitions. [MEASURE_CATALOG.csv](MEASURE_CATALOG.csv) specifies their home tables, families, reference-check kinds and numeric formats. Create measures, not calculated columns. Use dimension fields for slicers and axes; direct fact-column slicers are outside the checked filter contract.

| Measures | Meaning / filter behavior | Unfiltered reference |
|---|---|---|
| Land 2022 Reported Records | SUM weights, two supplied BuySell-layout files | 13,168 |
| Land Oct 2024 Reported Records | SUM weights, raw service-coded file | 6,024 |
| Muscat Brokerage Registrations | SUM weights, brokerage register occurrences | 9,366 |
| Three Geographic Share measures | Numerator in selected geography; denominator removes **both** dim_governorate and dim_wilayat filters. Keeps dataset, month and applicable attributes. Not “share of the entire Oman market” or share of the selected locations only. | 100% for each unfiltered population |
| Brokerage Property Use Share | Removes dim_property_use only from denominator; keeps month, wilayat and description. At a description row, share is within that description cohort. | 100% |
| Land 2022 / Land Oct 2024 Supplied Governorates | DISTINCTCOUNT fact governorate keys in the current cohort. Can fall under attribute filters; not proof of complete market reporting. | 11 / 11 |
| Muscat Brokerage Supplied Months | DISTINCTCOUNT observed fact month keys; a filtered month count, not elapsed year length. | 9 |
| Three Repeated Group Share measures | SUM full-source repeat-group membership weights / reported weights. Includes every member of a group, including its first occurrence. No group is recomputed after slicers. | 2022: 6,275 / 13,168; 2024: 0 / 6,024; brokerage: 8,174 / 9,366 |
| Land 2022 November Rows / December Rows | Fixed 2022 months: REMOVEFILTERS dim_period and dim_dataset, then select the explicit month. Preserve geography, buyer and owner filters. Show only in 2022 panel; these deliberately ignore a different dataset/period selection. | 7,501 / 5,667 |
| Land 2022 Nov Dec Row Difference | December minus November, blank if either cohort absent under remaining filters | −1,834 |
| Land 2022 Nov Dec Row Change | Difference / November; **two uploaded-file count comparison**, not annual growth or a proven market decline. Monthly completeness is not established. | −24.4500733236% |

No-data SUM, DISTINCTCOUNT and share results remain BLANK rather than being coerced to zero. An observed zero repeat-group share in October 2024 is different from an unavailable cohort. Geographic shares may sum to less than 100% when a visual shows only a top-ten subset; the denominator still includes the full applicable cohort. Fact attribute filters such as service code affect only the fact that has that relationship.

Repeat membership was established using original full-source fields, including demographic attributes excluded from the analytical facts. It is not the count of duplicates in a business-only projection or unique economic events. Zero full-source repeats in the October file does not prove unique transactions. No economic duplicate count or unique transaction measure is supported.

## What “validated” means here

1. The custom parser reads the **actual DAX file**, rejects unsupported tokens/functions, binds all table/column/measure references, checks SUM numeric inputs, and rejects dependency cycles.
2. The limited Python interpreter evaluates those parsed expressions using the 19 documented single-direction relationships and dimension-only filter contexts.
3. An independent oracle joins dimensions to the **audited source occurrence rows**, counts rows rather than aggregate weights, and calculates cohort shares and two-file differences. Each measure is compared against it in 131 contexts, including every actual dimension value, empty selection, an unavailable month, scope filters and conflicting geography filters: **2,227 checks**.
4. `validation/measure_test_vectors.csv` records every expected/reference pair; empty numeric cells mean BLANK. Filter scenarios describe QA contexts, not invented market observations. Nine generated DAX queries let Desktop test all measures in representative contexts against those expectations.

This is **not Microsoft DAX execution** or a general DAX emulator. Expanded-table behavior, arbitrary row context, RLS, locale/collation differences, visuals and engine optimizations are not certified. The supported expressions use SUM, DISTINCTCOUNT, DIVIDE, CALCULATE, REMOVEFILTERS, VAR/RETURN, IF, ISBLANK, BLANK, `||` and subtraction. Unsupported formulas fail rather than silently passing. All Desktop acceptance checks remain pending until recorded there.

No annual/YTD/YoY, price, monetary SUM, forecast, investment return, cross-family grand total or DISTINCTCOUNT of a generated lineage ID is provided.
