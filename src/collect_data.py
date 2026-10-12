"""Retrieve catalogued originals atomically, recording integrity and failures."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from io import BytesIO

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_HOSTS = {'api.ncsi.gov.om', 'ncsi.gov.om', 'www.ncsi.gov.om',
                 'cms.mohup.gov.om', 'mohup.gov.om', 'www.housing.gov.om',
                 'webapps.housing.gov.om', 'opendata.gov.om', 'data.gov.om'}
MAX_BYTES = 50 * 1024 * 1024


def check_url(url):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != 'https' or parts.hostname not in ALLOWED_HOSTS or parts.username:
        raise ValueError('Only catalogued official HTTPS hosts are supported')


class OfficialRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def validate_payload(payload, file_format):
    if not payload or len(payload) > MAX_BYTES:
        raise ValueError('Empty or oversized response')
    if file_format == 'pdf' and not payload.startswith(b'%PDF-'):
        raise ValueError('Response is not a PDF (possibly an HTML error page)')
    if file_format == 'xlsx':
        with zipfile.ZipFile(BytesIO(payload)) as archive:
            if 'xl/workbook.xml' not in archive.namelist():
                raise ValueError('Response is not an XLSX workbook')
    if file_format not in {'pdf', 'xlsx'}:
        raise ValueError('Unsupported original format')


def sha256(payload):
    return hashlib.sha256(payload).hexdigest()


def store_original(root, source, payload):
    """Preserve decoded original filename; never overwrite changed originals."""
    validate_payload(payload, source['format'])
    filename = Path(urllib.parse.unquote(urllib.parse.urlsplit(source['url']).path)).name
    identifier = source['source_id']
    if not identifier or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789_' for c in identifier):
        raise ValueError('Invalid source identifier')
    if not filename or filename in {'.', '..'}:
        raise ValueError('Invalid source filename')
    path = root / 'data' / 'raw' / identifier / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != payload:
        raise ValueError('Original changed; catalogue a new revision rather than overwrite')
    if not path.exists():
        temporary = path.with_suffix(path.suffix + '.part')
        temporary.write_bytes(payload)
        temporary.replace(path)
    return path.relative_to(root).as_posix(), sha256(payload)


def collect(root=ROOT, source_ids=None):
    catalogue = json.loads((root / 'docs/source_catalog.json').read_text())
    if source_ids and set(source_ids) - {s['source_id'] for s in catalogue}:
        raise ValueError('Unknown source id')
    opener = urllib.request.build_opener(OfficialRedirects())
    records = []
    for source in catalogue:
        if source_ids and source['source_id'] not in source_ids:
            continue
        record = dict(source_id=source['source_id'], source_url=source['url'],
                      attempted_at=datetime.now(timezone.utc).isoformat(), retrieved_at=None,
                      status='failed', raw_path=None, sha256=None, bytes=None)
        try:
            check_url(source['url'])
            request = urllib.request.Request(source['url'], headers={'User-Agent':'OmanRealEstatePortfolio/0.2 (public research)'})
            with opener.open(request, timeout=30) as response:
                check_url(response.geturl())
                payload = response.read(MAX_BYTES + 1)
                record.update(final_url=response.geturl(), content_type=response.headers.get('Content-Type'),
                              http_last_modified=response.headers.get('Last-Modified'))
            raw_path, digest = store_original(root, source, payload)
            record.update(status='downloaded_signature_checked', retrieved_at=datetime.now(timezone.utc).isoformat(), raw_path=raw_path,
                          sha256=digest, bytes=len(payload))
        except (ValueError, OSError, urllib.error.URLError, zipfile.BadZipFile) as exc:
            record['error'] = f'{type(exc).__name__}: {exc}'
        records.append(record)
        print(source['source_id'], record['status'])
    # Merge selected retries into the audit register; one record per source.
    target = root / 'docs/acquisition_manifest.json'
    previous = json.loads(target.read_text()) if target.exists() else []
    merged = {r['source_id']: r for r in previous}
    for record in records:
        # A failed refresh must not erase an existing original's checksum.
        if record['status'] == 'failed' and merged.get(record['source_id'], {}).get('sha256'):
            merged[record['source_id']]['last_refresh_error'] = record['error']
        else:
            merged[record['source_id']] = record
    target.write_text(json.dumps(list(merged.values()), indent=2, ensure_ascii=False) + '\n')
    return all(r['status'] != 'failed' for r in records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', action='append', help='Repeat to retry selected source identifiers')
    args = parser.parse_args()
    return 0 if collect(source_ids=args.source) else 1


if __name__ == '__main__':
    raise SystemExit(main())
