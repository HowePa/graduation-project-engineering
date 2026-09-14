"""Inspect dependency declarations; do not infer successful implementation."""
import xml.etree.ElementTree as ET
from common import cli, config, evidence, inputs, read, resolve, save, state


def run(root):
    root = root.resolve()
    cfg, _ = config(root)
    files = [s['path'] for s in inputs(root)]
    technologies, sources = [], [root / 'project.yaml']
    pom = resolve(root, cfg['paths']['backend']) / 'pom.xml'
    if pom.exists():
        tree = ET.parse(pom)
        ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
        artifacts = [x.text for x in tree.findall('.//m:artifactId', ns)]
        for name, artifact in [('Spring Boot', 'spring-boot-starter-web'), ('MyBatis-Plus', 'mybatis-plus-boot-starter'), ('MySQL', 'mysql-connector-j')]:
            if artifact in artifacts:
                technologies.append({'name': name, 'path': pom.relative_to(root).as_posix(), 'basis': f'declared dependency: {artifact}'})
        sources.append(pom)
    package = resolve(root, cfg['paths']['frontend']) / 'package.json'
    if package.exists():
        deps = read(package).get('dependencies', {})
        if 'vue' in deps:
            technologies.append({'name': 'Vue', 'path': package.relative_to(root).as_posix(), 'basis': f'declared dependency: {deps["vue"]}'})
        sources.append(package)
    compose = resolve(root, cfg['paths']['compose'])
    if compose.exists():
        read(compose)
        sources.append(compose)
        technologies.append({'name': 'Docker', 'path': compose.relative_to(root).as_posix(), 'basis': 'compose file exists; runtime not checked'})
    evidence(root, 'project', {'files': files, 'technologies': technologies}, sources,
             limitations=['Dependency declarations do not prove runtime use or successful startup.'])
    evidence(root, 'requirements', {'roles': cfg['roles'], 'features': cfg['features']}, [root / 'project.yaml'], status='planned', limitations=['Configured requirements are not implementation evidence.'])
    value = state(root)
    value['inventory'] = {name: ('present' if resolve(root, path).exists() else 'missing') for name, path in cfg['paths'].items()}
    value['inventory'].update({name: ('present' if (root / path).exists() else 'missing') for name, path in {'design':'docs/03-system-design.md','thesis':'thesis/thesis.md', 'screenshots':'artifacts/screenshots'}.items()})
    value['inventory']['tests'] = 'present' if any(p.startswith('tests/') or '/src/test/' in p for p in files) else 'missing'
    save(root / '.project-state.json', value)

if __name__ == '__main__':
    cli(run)
