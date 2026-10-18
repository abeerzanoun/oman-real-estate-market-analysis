# Outstanding Power BI Desktop acceptance record

**Status: NOT RUN.** No `.pbix` exists in this package. Do not check these boxes or fill in invented results. This record is for the person executing Power BI Desktop after the reviewed package is available.

| Evidence | Actual result |
|---|---|
| Desktop version / Windows version | Pending |
| Repository commit / data pin | Pending; expected EDA 168665c92a8a2ff91598 |
| Execution date / reviewer | Pending |
| Python preflight and test results | Pending local rerun |
| Full Power Query refresh result / error count | Pending |
| DAX query exports / location | Pending |
| Saved PBIX path and checksum | Pending; do not claim an artifact before saving/testing it |
| Visual / Arabic / interaction review | Pending |

- [ ] 16 loaded tables, with the exact types and row counts in SCHEMA.md; parameter/function not loaded as tables.
- [ ] Exactly 19 active 1:* single-direction relationships; metadata disconnected; Auto date/time and auto-relationships disabled.
- [ ] Null counts and unresolved URL/licence/currency fields remain null; no Remove duplicates, fill or replace-errors steps.
- [ ] All 17 measures created with catalog home tables and formats, no extra implicit fact-count or monetary measures.
- [ ] Run all nine `validation/desktop_*.dax` files independently in DAX query view. Every Pass is TRUE; export results and record paths above. Blank versus zero cases must pass.
- [ ] Default family sums are separately 13,168 / 6,024 / 9,366; physical fact rows are 361 / 257 / 403.
- [ ] Fixed Nov/Dec measures remain 2022-only even when a period/dataset filter is set; geography/buyer/owner restrictions retained.
- [ ] Geographic share denominators clear both geography dimensions and preserve source/period/attribute contexts.
- [ ] Coverage page shows correct scope/year/status cells and blanks for unavailable counts; no zero-filled missing months or completeness percentage.
- [ ] Land service selections do not affect the 2022 panel; no incompatible population totals or trends.
- [ ] Brokerage shows only Jan–Sep 2025 and six Muscat wilayats, with expected monthly counts.
- [ ] Repeat membership clearly differs from confirmed duplicates; no rows removed.
- [ ] Six pages, navigation/reset bookmarks, text legibility, Arabic rendering, scroll behavior, theme import and visual tooltips reviewed at desktop and tablet landscape size.
- [ ] Provenance limitations and monetary caveats visible; owner attribution is not labelled independently verified official authenticity.
- [ ] Only after all checks pass, save the real PBIX, document version/hash, and describe any remaining issues. No automatic public publication.
