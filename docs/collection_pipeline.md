# Collection and validation pipeline

Run from repository root with Python 3.12 and the locked environment:

```bash
python -m src.collect_data
python -m src.collect_data --source ncsi_2025_10 --source ncsi_2026_09
python -m src.process_data
python -m pytest
```

Install **Poppler (`pdftotext`)** for PDF processing. It is available in the connected workspace; it is a system executable, not a Python requirement. TLS verification and inherited proxy settings stay enabled. HTTPS and official-host redirects are enforced. The collector is bounded to 50 MiB per file and 30 seconds per request; failed resources can be retried selectively. It does not silently scrape unreviewed endpoints.

## Outputs and guarantees

- Originals: `data/raw/<source_id>/<original_filename>`; atomic write, SHA-256, no overwrite of changed bytes.
- Audit: `docs/acquisition_manifest.json`, including failed attempts with null checksum and successful downloads with actual byte metadata. Failed refreshes preserve prior successful provenance.
- Processed output, **only after originals exist and parse**: `data/processed/national_activity.csv`.
- Source/evidence inventory: `docs/source_catalog.json`; availability matrix: `docs/data_availability.md` and `.csv`.

Processing checks each original hash, extracts the reviewed page with `pdftotext -raw`, requires the six inspected Arabic metric rows and seven numeric columns, converts million OMR to OMR with `Decimal`, and retains six observation columns with explicit periods. The last column is a percentage change and is excluded. Layout changes, missing rows, fractional counts, negative/nonfinite values and duplicate observation keys fail visibly. No imputation, annualization or inference of geography/property categories occurs.

## Current completion and boundaries

**Completed:** official web research; two inspected NCSI tables/releases; provider-site licence verification; catalogue and discovery matrix; downloader, provenance handling, conservative processor and offline tests.

**Attempted and blocked:** eight original downloads; all failed at proxy CONNECT 403. No original checksums or processed observations are available. `src.process_data` correctly refuses to write a dataset in this state.

**Pending:** network configuration, successful originals, full-file integrity inspection, actual Poppler-layout validation, source-to-output reconciliation, exact publication dates, full historical coverage, regional source licences and price-index processing. Tests use a genuine, disclosed transcription of an official table plus technical error fixtures; they do not certify the original-PDF extraction path. If actual extraction differs, update the profile only after inspecting the source; do not relax checks to manufacture output.

Raw and processed records stay Git-ignored pending redistribution review. The repository tracks all discovery/provenance documentation and a small licensed test excerpt. No market findings or dashboards are produced in this phase.


## Manual ingestion option

Use the offline [manual upload guide](../DATA_UPLOAD_GUIDE.md) while automated destinations remain blocked. `python -m src.manual_ingestion run` consumes provenance-reviewed originals under `data/raw/manual/`. No collector call is made. The original PDF pipeline, audit register and historical work are preserved. New manual outputs appear only after real accepted input values exist.
