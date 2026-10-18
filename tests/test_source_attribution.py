"""Portal attribution evidence against the actual immutable reviewed workbooks."""
import copy
import hashlib
import json

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from src.dashboard_data import ROOT, load_dashboard
from src.source_attribution import load_source_attribution

MOHUP_PORTAL = 'https://webapps.housing.gov.om/opendata/ar/pages/default.aspx'
LAND = {'land_nov_2022', 'land_dec_2022', 'land_oct_2024'}


@pytest.fixture(scope='module')
def bundle():
    return load_dashboard()


def test_current_provider_is_separate_from_user_confirmed_portal(bundle):
    dimension = bundle['tables']['dim_dataset']
    before = dimension.copy(deep=True)
    current = load_source_attribution(dimension)
    assert set(current) == LAND | {'muscat_brokerage_2025'}
    for dataset_id, row in current.items():
        assert row['original_data_provider'] == 'Ministry of Housing and Urban Planning, Oman'
        assert row['confirmation_date'] == '2026-10-18'
        assert row['download_portal_evidence'] == 'user_confirmed'
        assert not row['independently_verified_official_download']
        assert row['portal_url_role'] == 'portal_landing_page_not_dataset_page_or_download'
        if dataset_id in LAND:
            assert row['portal_landing_url'] == MOHUP_PORTAL
            assert row['download_portal'] == 'MOHUP monthly Buy and Sell datasets portal'
        else:
            assert row['download_portal'] == 'Oman Open Data Portal'
            assert row['portal_landing_url'] == 'https://opendata.gov.om/'
            assert 'embedded' in row['provider_evidence']
        for key in ('dataset_page_url', 'exact_download_url', 'redistribution_licence',
                    'licence_url', 'verified_publication_date', 'original_download_date'):
            assert row[key] is None
    pd.testing.assert_frame_equal(dimension, before)


def test_attribution_matches_original_bytes_and_historical_registry(bundle):
    registry = json.loads((ROOT/'docs/uploaded_source_registry.json').read_text(encoding='utf-8'))
    current = load_source_attribution(bundle['tables']['dim_dataset'])
    for row in registry:
        assert hashlib.sha256((ROOT/row['file']).read_bytes()).hexdigest() == row['sha256']
        assert current[row['dataset_id']]['source_sha256'] == row['sha256']
    manifest = json.loads((ROOT/'data/processed/audited/71008482abd46aa7f0bc/manifest.json').read_text())
    assert hashlib.sha256((ROOT/'docs/uploaded_source_registry.json').read_bytes()).hexdigest() == manifest['implementation_sha256']['docs/uploaded_source_registry.json']


@pytest.mark.parametrize('change,reason', [
    ('duplicate_id','IDs do not match'), ('unknown_id','IDs do not match'),
    ('checksum','checksum mismatch'), ('provider','provider mismatch'),
    ('exact_url','evidence review'), ('verified','schema update'),
])
def test_unreviewed_or_misbound_attribution_fails_closed(tmp_path, bundle, change, reason):
    document = json.loads((ROOT/'docs/source_attribution.json').read_text(encoding='utf-8'))
    document = copy.deepcopy(document)
    first = document['datasets'][0]
    if change == 'duplicate_id':
        document['datasets'].append(copy.deepcopy(first))
    elif change == 'unknown_id':
        first['dataset_id'] = 'unregistered_source'
    elif change == 'checksum':
        first['source_sha256'] = '0'*64
    elif change == 'provider':
        first['original_data_provider'] = first['download_portal']
    elif change == 'exact_url':
        first['exact_download_url'] = first['portal_landing_url']
    else:
        first['independently_verified_official_download'] = True
    (tmp_path/'docs').mkdir()
    (tmp_path/'docs/source_attribution.json').write_text(json.dumps(document),encoding='utf-8')
    with pytest.raises(ValueError, match=reason):
        load_source_attribution(bundle['tables']['dim_dataset'],tmp_path)


def test_sources_page_shows_provider_portals_and_remaining_gaps():
    app = AppTest.from_file(str(ROOT/'streamlit_app.py'),default_timeout=30).run()
    app.radio(key='page').set_value('Sources and Methodology').run()
    assert not app.exception and not app.error
    markdown = '\n'.join(item.value for item in app.markdown)
    assert markdown.count('Original data provider: Ministry of Housing and Urban Planning, Oman') == 4
    assert markdown.count('Download / publishing portal: MOHUP monthly Buy and Sell datasets portal') == 3
    assert markdown.count('Download / publishing portal: Oman Open Data Portal') == 1
    assert 'redistribution licence' in markdown and 'unverified' in markdown
    assert 'verified publication date' in markdown and 'original download date' in markdown
    assert any('NCSI' in info.value and 'supplied none' in info.value for info in app.info)
    buttons = app.get('link_button')
    assert len(buttons) == 4
    assert [button.proto.url for button in buttons].count(MOHUP_PORTAL) == 3
    assert [button.proto.url for button in buttons].count('https://opendata.gov.om/') == 1
    assert all('landing page' in button.proto.label for button in buttons)
    assert '/blob/main/DATA_PROVENANCE_AUDIT.md' in markdown
    assert '/blob/feature/streamlit-dashboard/' not in markdown


def test_ncsi_is_not_an_analytical_workbook_provider_or_download_portal(bundle):
    document = json.loads((ROOT/'docs/source_attribution.json').read_text(encoding='utf-8'))
    assert 'Not a provider or download portal' in document['ncsi_usage']
    current = load_source_attribution(bundle['tables']['dim_dataset'])
    assert not any('ncsi' in str(row[key]).lower() for row in current.values()
                   for key in ('original_data_provider','download_portal','portal_landing_url'))
