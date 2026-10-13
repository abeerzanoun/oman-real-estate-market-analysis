"""Dispatch registered row uploads and remaining aggregate uploads offline."""
import json
from pathlib import Path
import tempfile
from src.audit_uploaded_data import ROOT, REGISTRY, run as audit_run
from src.manual_ingestion import input_files, run as aggregate_run


def main():
    registered = {ROOT / item['file'] for item in json.loads(REGISTRY.read_text())}
    report, target = audit_run()
    remaining = [path for path in input_files(ROOT/'data/raw/manual') if path not in registered]
    with tempfile.TemporaryDirectory() as temporary:
        aggregate, code = aggregate_run(ROOT/'data/raw/manual', ROOT/'data/processed/manual',
            Path(temporary)/'aggregate_status.json', files=remaining)
    print(json.dumps(dict(row_records=report['record_count'],audit_directory=str(target),
                         remaining_aggregate_files=len(remaining),aggregate_errors=aggregate['errors']),indent=2))
    # Empty/partial aggregate coverage is reported; any unregistered invalid upload fails.
    raise SystemExit(1 if code == 1 else 0)


if __name__ == '__main__':
    main()
