"""Collect evidence without converting missing records into facts."""
from common import KINDS, cli, digest, evidence, now, read, save, snapshot, validate, verify_record


def run(root):
    root = root.resolve()
    entries = []
    for kind in KINDS:
        path = root / 'evidence' / f'{kind}.json'
        if not path.exists() or read(path)['status'] in ('missing', 'not_run'):
            evidence(root, kind, status='not_run' if kind == 'performance' else 'missing',
                     limitations=['No collector output is available; this is not implementation evidence.'])
        value = verify_record(root, kind)
        if value['status'] == 'failed': raise ValueError(f'Cannot build downstream manifest after failed {kind}')
        entries.append({'kind': kind, 'path': f'evidence/{kind}.json', 'sha256': digest(path), 'status': value['status']})
    manifest = {'schema_version': '1.0', 'generated_at': now(), 'snapshot': snapshot(root), 'entries': entries}
    validate(manifest, 'manifest.schema.json')
    save(root / 'evidence/manifest.json', manifest)

if __name__ == '__main__':
    cli(run)
