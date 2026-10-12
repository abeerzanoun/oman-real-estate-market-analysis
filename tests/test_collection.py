"""Network-free collection checks; technical payloads contain no market records."""
import json
from pathlib import Path
import urllib.error
import pytest
from src.collect_data import check_url, collect, store_original, validate_payload, sha256
from src.process_data import parse_number, parse_page, process

ROOT = Path(__file__).resolve().parents[1]


def test_official_urls_only():
    check_url('https://api.ncsi.gov.om/uploads/a.pdf')
    for url in ['http://api.ncsi.gov.om/a.pdf','https://ncsi.gov.om.example.org/a.pdf','https://example.org/a.pdf']:
        with pytest.raises(ValueError):
            check_url(url)


def test_reject_html_error_as_pdf():
    with pytest.raises(ValueError, match='not a PDF'):
        validate_payload(b'<html>Access denied</html>', 'pdf')


def test_reject_empty_file():
    with pytest.raises(ValueError, match='Empty'):
        validate_payload(b'', 'pdf')


def test_original_cannot_be_overwritten(tmp_path):
    source={'source_id':'technical_test','url':'https://api.ncsi.gov.om/test.pdf','format':'pdf'}
    # Technical signature fixture, not a dataset or valid complete PDF.
    payload=b'%PDF-1.7\n'
    path,digest=store_original(tmp_path,source,payload)
    assert digest == sha256((tmp_path/path).read_bytes())
    assert store_original(tmp_path,source,payload) == (path,digest)
    with pytest.raises(ValueError, match='Original changed'):
        store_original(tmp_path,source,b'%PDF-1.6\n')


def test_failed_download_never_claims_checksum(tmp_path,monkeypatch):
    (tmp_path/'docs').mkdir()
    source={'source_id':'technical_test','url':'https://api.ncsi.gov.om/test.pdf','format':'pdf'}
    (tmp_path/'docs/source_catalog.json').write_text(json.dumps([source]))
    class Blocked:
        def open(self,*args,**kwargs):
            raise urllib.error.URLError('Tunnel connection failed: 403 Forbidden')
    monkeypatch.setattr('src.collect_data.urllib.request.build_opener',lambda *a:Blocked())
    assert not collect(tmp_path)
    record=json.loads((tmp_path/'docs/acquisition_manifest.json').read_text())[0]
    assert record['status']=='failed'
    assert record['sha256'] is None and record['raw_path'] is None and record['retrieved_at'] is None
    assert not (tmp_path/'data').exists()


def test_unknown_source_is_error(tmp_path):
    (tmp_path/'docs').mkdir()
    (tmp_path/'docs/source_catalog.json').write_text('[]')
    with pytest.raises(ValueError,match='Unknown'):
        collect(tmp_path,['unknown'])


def test_genuine_source_excerpt_conversion_and_periods():
    source=json.loads((ROOT/'docs/source_catalog.json').read_text())[0]
    text=(ROOT/'tests/fixtures/ncsi_2025_10_activity_excerpt.txt').read_text()
    rows=parse_page(text,source,'checksum-not-available-for-transcription')
    assert len(rows)==36
    sales=[r for r in rows if r['indicator']=='sales_value_omr']
    assert sales[0]['value']=='1094900000.0'
    assert sales[3]['value']=='97300000.0'
    assert sales[3]['period_end']=='2025-09-30' and sales[3]['frequency']=='monthly'
    assert sales[5]['frequency']=='year_to_date'
    counts=[r for r in rows if r['indicator']=='sales_contract_count']
    assert counts[3]['value']=='6204'
    assert all(r['property_category']=='not_disaggregated' for r in rows)


def test_parser_fails_closed_for_changed_layout():
    source=json.loads((ROOT/'docs/source_catalog.json').read_text())[0]
    with pytest.raises(ValueError,match='Review extraction'):
        parse_page('Unrecognized PDF layout',source,'digest')


@pytest.mark.parametrize('token,unit',[('NaN','OMR'),('-1','OMR'),('1.5','count')])
def test_invalid_values_are_rejected(token,unit):
    with pytest.raises(ValueError):
        parse_number(token,unit)


def test_no_processed_dataset_without_originals(tmp_path):
    (tmp_path/'docs').mkdir()
    (tmp_path/'docs/source_catalog.json').write_text('[]')
    (tmp_path/'docs/acquisition_manifest.json').write_text('[]')
    with pytest.raises(ValueError,match='No downloaded originals'):
        process(tmp_path)
    assert not (tmp_path/'data/processed').exists()


def test_checksum_mismatch_prevents_processing(tmp_path):
    (tmp_path/'docs').mkdir()
    source=json.loads((ROOT/'docs/source_catalog.json').read_text())[0]
    (tmp_path/'docs/source_catalog.json').write_text(json.dumps([source]))
    raw=tmp_path/'data/raw/technical.pdf'
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b'%PDF-1.7\n')
    entry={'source_id':source['source_id'],'raw_path':'data/raw/technical.pdf','sha256':'0'*64}
    (tmp_path/'docs/acquisition_manifest.json').write_text(json.dumps([entry]))
    with pytest.raises(ValueError,match='checksum mismatch'):
        process(tmp_path)
    assert not (tmp_path/'data/processed').exists()


def test_ambiguous_duplicate_source_rows_are_rejected():
    source=json.loads((ROOT/'docs/source_catalog.json').read_text())[0]
    text=(ROOT/'tests/fixtures/ncsi_2025_10_activity_excerpt.txt').read_text()
    with pytest.raises(ValueError,match='Review extraction'):
        parse_page(text+text,source,'digest')


def test_invalid_thousands_grouping_is_rejected():
    with pytest.raises(ValueError,match='numeric syntax'):
        parse_number('1,3.2','OMR')


def test_unreviewed_extra_numeric_column_is_rejected():
    source=json.loads((ROOT/'docs/source_catalog.json').read_text())[0]
    text=(ROOT/'tests/fixtures/ncsi_2025_10_activity_excerpt.txt').read_text()
    # Inject a technical corruption marker into the genuine row layout.
    corrupted=text.replace('13.5 contracts sales','13.5 999 contracts sales')
    with pytest.raises(ValueError,match='Review extraction'):
        parse_page(corrupted,source,'digest')
