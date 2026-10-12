# Phase 2 execution record

Date: 2026-10-12. Platform: Linux, Python 3.12.14, isolated locked environment.

| Executed check | Result |
|---|---|
| Environment validator | PASS — Python 3.12 and 11 imports |
| Pytest | PASS — 20 tests, 14 existing upstream deprecation warnings |
| `python -m pip check` | PASS — no broken requirements |
| Python compilation | PASS |
| `git diff --check` | PASS |
| Official collector | BLOCKED — 8/8 proxy CONNECT 403; exit 1 |
| Processor with current manifest | EXPECTED REFUSAL — no originals; no output; exit 1 |

The new tests cover official HTTPS URL selection, HTML/empty download rejection, immutable originals, failed-attempt provenance, unknown source IDs, decimal unit conversion using a genuine NCSI excerpt, cumulative versus monthly periods, invalid counts/values, ambiguous layout, checksum tampering and refusal to process without originals.

These are offline safeguards. Original-PDF extraction, source-to-output reconciliation, historical completeness, actual geographic/category schemas, Excel/Power BI exports have **not** been validated. Remote GitHub Actions checks succeeded on implementation commit `22c6f7e` ([PR run](https://github.com/abeerzanoun/oman-real-estate-market-analysis/actions/runs/38206830118), [push run](https://github.com/abeerzanoun/oman-real-estate-market-analysis/actions/runs/38206786963)). The checked-in GitHub Actions workflow runs imports, dependency consistency and offline Pytest checks on Python 3.12; no collection happens in CI.

Network request remains pending in the environment configuration. The collector can resume from the catalogue after the official hosts are permitted. No failure is reclassified as unavailable data; no original checksum or processed observation is invented.
