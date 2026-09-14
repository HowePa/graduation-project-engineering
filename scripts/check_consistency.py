"""Check evidence integrity/freshness; report full-delivery blockers separately."""
from common import KINDS, cli, digest, read, resolve, save, snapshot, validate, verify_record, now


def run(root):
    root = root.resolve()
    errors, blockers = [], []
    try:
        manifest = read(root / 'evidence/manifest.json')
        validate(manifest, 'manifest.schema.json')
        if manifest['snapshot'] != snapshot(root): errors.append('Project inputs changed; rerun upstream stages and reconfirm gates')
        kinds = [entry['kind'] for entry in manifest['entries']]
        if sorted(kinds) != sorted(KINDS): errors.append('Manifest must contain each of the 12 evidence kinds exactly once')
        for entry in manifest['entries']:
            try:
                if entry['path'] != f'evidence/{entry["kind"]}.json': raise ValueError('Unexpected evidence path')
                path = resolve(root, entry['path'])
                if digest(path) != entry['sha256']: raise ValueError('Manifest hash differs from record')
                value = verify_record(root, entry['kind'])
                if value['status'] != entry['status']: raise ValueError('Manifest status differs from record')
                if value['status'] == 'failed': errors.append(f'{entry["kind"]}: failed')
                if value['status'] != 'observed' and entry['kind'] != 'performance': blockers.append(f'{entry["kind"]}: {value["status"]}')
                if value['status'] == 'observed' and entry['kind'] == 'test-results':
                    data = value['data']
                    if data['exit_code'] != 0 or not data['cases'] or any(c['status'] != 'PASS' for c in data['cases']): errors.append('Test evidence is not successful')
            except Exception as exc:
                errors.append(f'{entry["kind"]}: {exc}')
    except Exception as exc:
        errors.append(str(exc))
    blockers.extend(['Live MySQL/schema and browser/role acceptance have not been automated in v0.1',
                     'Full thesis claim review, verified references and DOCX rendered review are required'])
    report = {'generated_at': now(), 'integrity': 'PASS' if not errors else 'FAIL',
              'delivery_status': 'blocked', 'errors': errors, 'delivery_blockers': blockers,
              'scope': 'Evidence schema, source hashes and current input snapshot only; not a full thesis semantic validator'}
    save(root / 'artifacts/consistency-report.json', report)
    if errors: raise ValueError('; '.join(errors))
    return report

if __name__ == '__main__':
    cli(run)
