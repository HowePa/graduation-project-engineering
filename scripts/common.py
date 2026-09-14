"""Shared contracts. Every persisted path is relative to the target project."""
from __future__ import annotations
import hashlib
import json
import logging
import os
from pathlib import Path
from datetime import datetime, timezone
import yaml
from jsonschema import Draft202012Validator, FormatChecker

SKILL = Path(__file__).resolve().parents[1]
KINDS = ('project', 'requirements', 'architecture', 'database', 'api', 'modules', 'routes',
         'screenshots', 'diagrams', 'test-results', 'performance', 'references')
EXCLUDED = {'.git', '.venv', 'node_modules', 'target', 'dist', '__pycache__', 'evidence', 'artifacts', 'thesis'}


def now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def resolve(root, relative):
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError(f'Project path must be relative without traversal: {relative}')
    full = (root / p).resolve()
    if not full.is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes project: {relative}')
    return full


def read(path):
    with Path(path).open(encoding='utf-8') as f:
        return yaml.safe_load(f)


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temp, path)


def validate(value, name):
    schema = read(SKILL / 'config' / name)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)


def config(root, use_runtime=True):
    cfg = read(root / 'project.yaml')
    validate(cfg, 'project.schema.yaml')
    thesis_path = root / 'thesis.yaml'
    thesis = read(thesis_path if thesis_path.exists() else SKILL / 'config/defaults.yaml')
    validate(thesis, 'thesis.schema.yaml')
    if use_runtime and (root / '.thesis-template-lock.yaml').exists():
        from resolve_thesis_template import verify
        verify(root)
        thesis = read(root / 'thesis-runtime.yaml')
    for path in list(cfg['paths'].values()) + [cfg['workflow']['test_cwd'], cfg['thesis']['template']]:
        resolve(root, path)
    resolve(root, cfg['workflow']['test_report_glob'])
    ids = [f['id'] for f in cfg['features']]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate feature IDs')
    for feature in cfg['features']:
        if not feature['roles'] or set(feature['roles']) - set(cfg['roles']):
            raise ValueError(f'Unknown or empty roles for {feature["id"]}')
    return cfg, thesis


def inputs(root):
    result = []
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        # v0.2 control-plane files carry their own hashes and do not change system facts.
        control = relative.as_posix()
        if control in {'.workflow-state.json', '.thesis-template-lock.yaml', 'thesis-runtime.yaml', 'ui-design.yaml'} or control.startswith(('decisions/', 'inputs/thesis-template/')):
            continue
        if any(part in EXCLUDED for part in relative.parts) or relative.name == '.project-state.json':
            continue
        if path.is_file():
            resolve(root, str(relative))
            result.append({'path': relative.as_posix(), 'sha256': digest(path)})
    return result


def snapshot(root):
    return hashlib.sha256(json.dumps(inputs(root), sort_keys=True).encode()).hexdigest()


def source(root, path):
    relative = Path(path).relative_to(root).as_posix()
    return {'path': relative, 'sha256': digest(resolve(root, relative))}


def evidence(root, kind, data=None, sources=(), status='observed', limitations=()):
    value = {'schema_version': '1.0', 'kind': kind, 'status': status, 'generated_at': now(),
             'producer': 'graduation-project-engineering/0.1', 'input_snapshot': snapshot(root),
             'sources': [source(root, Path(p)) for p in sorted(set(sources))],
             'limitations': list(limitations), 'data': data or {}}
    validate(value, 'evidence.schema.json')
    save(root / 'evidence' / f'{kind}.json', value)
    return value


def verify_record(root, kind):
    path = root / 'evidence' / f'{kind}.json'
    value = read(path)
    validate(value, 'evidence.schema.json')
    if value['input_snapshot'] != snapshot(root):
        raise ValueError(f'Stale project snapshot: {kind}')
    if value['kind'] != kind:
        raise ValueError(f'Evidence kind mismatch: {path}')
    if value['status'] == 'observed' and not value['sources']:
        raise ValueError(f'Observed evidence has no source: {kind}')
    for item in value['sources']:
        file = resolve(root, item['path'])
        if not file.is_file() or digest(file) != item['sha256']:
            raise ValueError(f'Stale or missing source: {kind}: {item["path"]}')
    return value


def state(root):
    path = root / '.project-state.json'
    current = snapshot(root)
    value = read(path) if path.exists() else {'schema_version': '1.0', 'stages': {}, 'gates': {}}
    if value.get('snapshot') != current:
        value['stages'] = {}
        value['gates'] = {}
        value['completed'] = []
        value['pending'] = ['inspect', 'test', 'evidence', 'check']
        value.pop('current_stage', None)
    value['snapshot'] = current
    validate(value, 'state.schema.json')
    return value


def stage(root, name, status, detail=''):
    value = state(root)
    order = ['inspect', 'test', 'evidence', 'check']
    if name in order:
        for downstream in order[order.index(name) + 1:]:
            value['stages'].pop(downstream, None)
    value['current_stage'] = name
    value['stages'][name] = {'status': status, 'updated_at': now(), 'detail': detail}
    value['completed'] = [k for k, v in value['stages'].items() if v['status'] == 'complete']
    value['pending'] = [k for k in ('inspect', 'test', 'evidence', 'check') if k not in value['completed']]
    save(root / '.project-state.json', value)


def cli(action):
    import argparse
    parser = argparse.ArgumentParser(description=action.__doc__)
    parser.add_argument('--project', type=Path, required=True)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
    try:
        root = args.project.resolve()
        config(root)
        action(root)
    except Exception:
        logging.exception('Stage failed')
        raise SystemExit(1)
