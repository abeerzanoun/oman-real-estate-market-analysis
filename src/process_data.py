"""Process reviewed NCSI table profiles only from hash-verified original PDFs."""
import argparse
import csv
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
import subprocess
import sys
from .collect_data import ROOT, sha256

# Exact source labels from inspected national activity tables (Arabic is stable
# across the reversed English text order in PDF extraction).
METRICS = {
    'القيمة المتداولة لعقود البيع': ('sales_value_omr', 'OMR', Decimal('1000000')),
    'عقود البيع': ('sales_contract_count', 'count', Decimal('1')),
    'القيمة المتداولة لعقود الرهن': ('mortgage_value_omr', 'OMR', Decimal('1000000')),
    'عقود الرهن': ('mortgage_contract_count', 'count', Decimal('1')),
    'القيمة المتداولة لعقود المبادلة': ('barter_value_omr', 'OMR', Decimal('1000000')),
    'عقود المبادلة': ('barter_contract_count', 'count', Decimal('1')),
}


def parse_number(token, unit):
    if not re.fullmatch(r'(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?', token):
        raise ValueError('Invalid source numeric syntax')
    try:
        value = Decimal(token.replace(',', ''))
    except InvalidOperation as exc:
        raise ValueError('Invalid source number') from exc
    if not value.is_finite() or value < 0:
        raise ValueError('Observation must be finite and nonnegative')
    if unit == 'count' and value != value.to_integral_value():
        raise ValueError('Contract counts must be integers')
    return value


def parse_page(text, source, digest):
    """Fail closed if a reviewed row or seven-column layout cannot be recognized.

    Six observation columns plus a published percent-change column are expected.
    The change column is not treated as an observation. Index/fees/title-deed
    tables require separate future profiles and are deliberately excluded.
    """
    if len(source['profile']['columns']) != 6:
        raise ValueError('Expected six reviewed observation columns')
    records = []
    for label, (indicator, unit, scale) in METRICS.items():
        # Match only a complete Arabic row label immediately before its values.
        pattern = r'(?<![\u0600-\u06ff])' + re.escape(label) + r'\s*(?:\([^)]*\))?\s+((?:-?\d[\d,.]*\s+){6}-?\d[\d,.]*)(?![\d,.])(?=\s+(?!-?\d)|$)'
        matches = re.findall(pattern, text)
        if len(matches) != 1:
            raise ValueError(f'Review extraction layout for {source["source_id"]}: {label}')
        tokens = matches[0].split()
        for token, period in zip(tokens[:6], source['profile']['columns'], strict=True):
            value = parse_number(token, unit) * scale
            records.append(dict(indicator=indicator, value=format(value, 'f'), unit=unit,
                                geographic_level='national', governorate='', wilayat='',
                                property_category='not_disaggregated', **period,
                                source_id=source['source_id'], source_url=source['url'],
                                source_page=source['profile']['page'], raw_sha256=digest))
    return records


def process(root=ROOT):
    catalogue = json.loads((root / 'docs/source_catalog.json').read_text())
    manifest = json.loads((root / 'docs/acquisition_manifest.json').read_text())
    downloads = {r['source_id']:r for r in manifest if r.get('sha256')}
    rows = []
    for source in catalogue:
        entry = downloads.get(source['source_id'])
        if not entry or not source.get('profile'):
            continue
        if source['verification_status'] != 'content_verified_online':
            raise ValueError('Unreviewed source profile')
        raw = (root / entry['raw_path']).resolve()
        if not raw.is_relative_to((root / 'data/raw').resolve()):
            raise ValueError('Raw path is outside data/raw')
        if sha256(raw.read_bytes()) != entry['sha256']:
            raise ValueError('Raw checksum mismatch')
        page = str(source['profile']['page'])
        # Poppler handles originals; fail loudly rather than infer from snippets.
        output = subprocess.run(['pdftotext','-raw','-f',page,'-l',page,str(raw),'-'],
                                check=True, capture_output=True, text=True).stdout
        rows.extend(parse_page(output, source, entry['sha256']))
    if not rows:
        raise ValueError('No downloaded originals with reviewed profiles; no dataset written')
    keys = [(r['indicator'],r['period_start'],r['period_end'],r['frequency']) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError('Overlapping releases: choose an explicit source revision before processing')
    target = root / 'data/processed/national_activity.csv'
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix('.csv.part')
    with temporary.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(target)
    print(f'Wrote {len(rows)} traceable observations to {target}')


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        process()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f'Processing blocked: {exc}', file=sys.stderr)
        raise SystemExit(1) from exc
