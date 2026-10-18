"""Current provider/portal evidence, joined to immutable data by ID and checksum.

The ingestion registry and processed metadata remain their original audit snapshot.
This addendum changes source presentation only; it never changes analytical tables.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_source_attribution(dataset_dimension, root=ROOT):
    document = json.loads((Path(root) / 'docs/source_attribution.json').read_text(encoding='utf-8'))
    if document['schema_version'] != 1:
        raise ValueError('Unsupported source attribution schema')
    entries = document['datasets']
    by_id = {row['dataset_id']: row for row in entries}
    expected = dataset_dimension.set_index('dataset_id')
    if (not expected.index.is_unique or len(entries) != len(by_id)
            or set(by_id) != set(expected.index)):
        raise ValueError('Source attribution IDs do not match the reviewed datasets')
    for dataset_id, row in by_id.items():
        pinned = expected.loc[dataset_id]
        if row['source_sha256'] != pinned['sha256']:
            raise ValueError(f'Source attribution checksum mismatch: {dataset_id}')
        if row['original_data_provider'] != pinned['provider']:
            raise ValueError(f'Source attribution provider mismatch: {dataset_id}')
        # All current portal evidence comes from the owner, not a new retrieval.
        if (row['download_portal_evidence'] != 'user_confirmed'
                or row['independently_verified_official_download'] is not False
                or row['portal_url_role'] != 'portal_landing_page_not_dataset_page_or_download'):
            raise ValueError('Source attribution evidence needs a reviewed schema update')
        if any(row[key] is not None for key in ('dataset_page_url', 'exact_download_url',
                'redistribution_licence', 'licence_url', 'verified_publication_date', 'original_download_date')):
            raise ValueError('New exact-resource/licence metadata needs an evidence review')
    return by_id
