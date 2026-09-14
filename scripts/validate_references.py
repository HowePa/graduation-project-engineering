"""Validate recorded bibliographic verification and configured quotas; no web truth claim."""
from datetime import datetime, timezone
from common import cli, config, resolve, save, verify_record, now


def run(root):
    root = root.resolve()
    cfg, thesis = config(root)
    record = verify_record(root, 'references')
    errors = []
    if record['status'] != 'observed':
        errors.append('Reference evidence has not been collected and verified')
    items = record['data'].get('items', [])
    valid, seen = [], set()
    source_paths = {item['path'] for item in record['sources']}
    for item in items:
        key = item['title'].strip().casefold()
        if key in seen: errors.append(f'Duplicate reference: {item["id"]}'); continue
        seen.add(key)
        verification = item.get('verification')
        if not item.get('verified') or not verification:
            errors.append(f'Unverified reference: {item["id"]}'); continue
        artifact = verification['artifact']
        if artifact not in source_paths or not resolve(root, artifact).is_file():
            errors.append(f'Missing hashed verification artifact: {item["id"]}'); continue
        if not item['source'].startswith(('https://', 'http://')):
            errors.append(f'Missing retrievable source URL: {item["id"]}'); continue
        valid.append(item)
    policy = thesis['references']
    year = datetime.now(timezone.utc).year
    counts = {'minimum': len(valid), 'journals': sum(i['type'] == 'J' for i in valid),
              'foreign': sum(not i['language'].lower().startswith('zh') for i in valid),
              'dissertations': sum(i['type'] == 'D' for i in valid), 'books': sum(i['type'] == 'M' for i in valid)}
    for key, actual in counts.items():
        minimum = max(policy[key], cfg['thesis']['references_min']) if key == 'minimum' else policy[key]
        if actual < minimum: errors.append(f'{key}: {actual} < {minimum}')
    recent = sum(year - policy['recent_years'] + 1 <= i['year'] <= year for i in valid)
    if any(i['year'] > year for i in valid): errors.append('Future publication year requires correction')
    if valid and recent / len(valid) < policy['recent_ratio']: errors.append('Recent-reference ratio below configured minimum')
    save(root / 'artifacts/reference-report.json', {'generated_at': now(), 'status': 'FAIL' if errors else 'PASS',
         'counts': counts, 'errors': errors, 'scope': 'Recorded verification and quotas; human must verify source content'})
    if errors: raise ValueError('; '.join(errors))

if __name__ == '__main__':
    cli(run)
