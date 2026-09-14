"""Scan single literal class/method Spring mappings in the Golden Example."""
import re
from common import cli, config, evidence, resolve


def parse(text, source):
    # Reject unsupported mappings rather than silently claiming coverage.
    if '@RestController' not in text:
        return []
    if '/*' in text or re.search(r'^\s*//', text, re.M):
        raise ValueError(f'Golden scanner requires annotation source without comments: {source}')
    head, separator, body = text.partition('public class ')
    if not separator: raise ValueError(f'Unsupported controller declaration: {source}')
    bases = re.findall(r'@RequestMapping\(\s*"([^"\n]*)"\s*\)', head)
    if head.count('@RequestMapping') != len(bases) or len(bases) > 1 or '@RequestMapping' in body:
        raise ValueError(f'Unsupported RequestMapping expression: {source}')
    base = bases[0] if bases else ''
    pattern = r'@(Get|Post|Put|Delete|Patch)Mapping\(\s*"([^"\n]*)"\s*\)\s+public\s+([\w<>?, ]+)\s+(\w+)\s*\('
    matches = list(re.finditer(pattern, body))
    if len(matches) != len(re.findall(r'@(Get|Post|Put|Delete|Patch)Mapping\b', body)):
        raise ValueError(f'Unsupported mapping syntax: {source}')
    if not matches: raise ValueError(f'No supported endpoints: {source}')
    return [{'method': m[1].upper(), 'url': '/' + '/'.join(x.strip('/') for x in [base, m[2]] if x.strip('/')),
             'handler': m[4], 'source': source, 'roles': [], 'request': None, 'response': m[3].strip()} for m in matches]


def run(root):
    root = root.resolve()
    cfg, _ = config(root)
    files = sorted(resolve(root, cfg['paths']['backend']).glob('src/main/java/**/*.java'))
    endpoints, sources = [], []
    for path in files:
        found = parse(path.read_text(encoding='utf-8'), path.relative_to(root).as_posix())
        if found: endpoints.extend(found); sources.append(path)
    if not endpoints: raise ValueError('No supported Spring REST endpoints found')
    keys = [(e['method'], e['url']) for e in endpoints]
    if len(keys) != len(set(keys)): raise ValueError('Duplicate API mappings')
    evidence(root, 'api', {'endpoints': endpoints}, sources,
             limitations=['Literal mappings only. Request DTOs, role enforcement and runtime responses are not verified.'])

if __name__ == '__main__':
    cli(run)
