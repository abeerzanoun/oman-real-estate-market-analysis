# Original-source download retry

Retried on 2026-10-12T09:44:08.314195+04:00 (Asia/Muscat), after the user reported publishing an eight-domain environment policy.

The actual bound runtime still reported restricted, enforced networking with no custom allowed hosts, observations current, desired and observed revision 26. The safe configuration snapshot is in [retry_network_status.json](retry_network_status.json).

| Official-host resource | Retry result | Reason | Original SHA-256 |
|---|---|---|---|
| Monthly Statistical Bulletin: October 2025 | Failed | Proxy CONNECT HTTP 403, before origin server access | Unavailable: no original received |
| Monthly Statistical Bulletin: September 2026 | Failed | Proxy CONNECT HTTP 403, before origin server access | Unavailable: no original received |
| Statistical Year Book 2026, Issue 54 | Failed | Proxy CONNECT HTTP 403, before origin server access | Unavailable: no original received |
| Monthly Statistical Bulletin: February 2024 | Failed | Proxy CONNECT HTTP 403, before origin server access | Unavailable: no original received |
| Monthly Statistical Bulletin: January 2026, XLSX | Failed | Proxy CONNECT HTTP 403, before origin server access | Unavailable: no original received |
| Real Estate Bulletin: Q1 2021 | Failed | Proxy CONNECT HTTP 403, before origin server access | Unavailable: no original received |
| Real Estate Bulletin: Q1 2022 | Failed | Proxy CONNECT HTTP 403, before origin server access | Unavailable: no original received |
| Annual Statistical Report 2021 | Failed | Proxy CONNECT HTTP 403, before origin server access | Unavailable: no original received |

## Verified outcome

- Downloaded originals: **0 of 8**.
- Real acquired analytical observations: **0**.
- `data/raw/` and `data/processed/` contain only directory placeholders; originals were not overwritten.
- The collector exited 1 and recorded fresh per-source attempt timestamps and errors in `acquisition_manifest.json`.
- The processor exited 1: `Processing blocked: No downloaded originals with reviewed profiles; no dataset written`.
- No dataset is ready for Python market analysis or Power BI ingestion.
- Offline checks: **20 Pytest tests passed**, with 14 existing upstream deprecation warnings. Tests do not establish source availability.

## Remaining requirement

The published government-host policy must be applied to the runtime bound to this chat. All eight catalogue download URLs use just two hosts: **api.ncsi.gov.om** (five resources) and **cms.mohup.gov.om** (three resources). Confirm these exact subdomains are included; allowing ncsi.gov.om or mohup.gov.om alone does not establish subdomain permission. Provider-site existence and previous online table verification remain separate from successful local acquisition.

This is an observed proxy policy denial, not an automatic approval rejection, provider HTTP 403, or proof of dataset nonavailability. Source URLs, proposed units and evidence levels are preserved in the catalogue. No synthetic records, inferred missing values, or substitute checksum claims are included.
