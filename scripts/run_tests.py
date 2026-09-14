"""Execute configured test argv and collect fresh JUnit reports, never synthetic passes."""
import subprocess
import time
import uuid
import xml.etree.ElementTree as ET
from common import cli, config, evidence, resolve, stage, snapshot


def run(root):
    root = root.resolve()
    cfg, _ = config(root)
    before_snapshot = snapshot(root)
    settings = cfg['workflow']
    command = settings['test_command']
    pattern = settings['test_report_glob']
    # Existing reports are not trusted; require a new output directory per invocation.
    run_id = uuid.uuid4().hex
    report_dir = resolve(root, f'artifacts/test-runs/{run_id}')
    report_dir.mkdir(parents=True)
    command = [part.replace('{report_dir}', str(report_dir)) for part in command]
    if not any(str(report_dir) in part for part in command):
        raise ValueError('test_command must include {report_dir} so old reports cannot be reused')
    log = report_dir / 'execution.log'
    started = time.monotonic()
    exit_code = -1
    try:
        with log.open('w', encoding='utf-8') as output:
            result = subprocess.run(command, cwd=resolve(root, settings['test_cwd']), stdout=output,
                                    stderr=subprocess.STDOUT, timeout=settings['timeout_seconds'], check=False)
        exit_code = result.returncode
    except (OSError, subprocess.TimeoutExpired) as exc:
        with log.open('a', encoding='utf-8') as output: output.write('\n' + str(exc))
    cases, reports, parse_errors = [], [], []
    for report in sorted(root.glob(pattern.replace('{run_id}', run_id))):
        report = resolve(root, str(report.relative_to(root)))
        if not report.is_relative_to(report_dir):
            raise ValueError('JUnit reports must be inside this invocation report directory')
        reports.append(report)
        try:
            xml = ET.parse(report)
            for suite in xml.getroot().iter('testsuite'):
                if any(int(suite.get(attr, '0')) > 0 for attr in ('errors', 'failures', 'skipped')):
                    parse_errors.append('JUnit suite reports errors, failures or skipped tests')
                if suite.get('tests') is not None and int(suite.get('tests')) != len(suite.findall('.//testcase')):
                    parse_errors.append('JUnit suite test count differs from actual cases')
            for case in xml.findall('.//testcase'):
                failure = case.find('failure')
                if failure is None: failure = case.find('error')
                skipped = case.find('skipped') is not None
                actual = ((failure.get('message', '') + '\n' + (failure.text or '')).strip() if failure is not None else 'JUnit reports success; response details not recorded')
                cases.append({'id': case.get('classname', '') + '.' + case.get('name', ''),
                              'module': case.get('classname', 'unknown'), 'feature': case.get('name', 'unknown'),
                              'input': 'JUnit 未记录', 'expected': 'test assertions pass',
                              'actual': 'Skipped' if skipped else actual,
                              'status': 'SKIP' if skipped else 'FAIL' if failure is not None else 'PASS'})
        except ET.ParseError as exc:
            parse_errors.append(str(exc))
    if snapshot(root) != before_snapshot: parse_errors.append('Project inputs changed during test execution')
    success = exit_code == 0 and cases and all(c['status'] == 'PASS' for c in cases) and not parse_errors
    if len({c['id'] for c in cases}) != len(cases): success = False; parse_errors.append('Duplicate test IDs')
    sources = [root / 'project.yaml', log] + reports
    evidence(root, 'test-results', {'command': settings['test_command'], 'exit_code': exit_code,
             'duration_seconds': round(time.monotonic() - started, 3), 'cases': cases,
             'log': log.relative_to(root).as_posix()}, sources, status='observed' if success else 'failed',
             limitations=['JUnit pass does not establish browser/MySQL runtime acceptance.'] + parse_errors)
    stage(root, 'test', 'complete' if success else 'failed', f'{len(cases)} real JUnit test cases; exit={exit_code}')
    if not success: raise RuntimeError(f'Tests failed, skipped, or produced no valid current JUnit report; see {log}')

if __name__ == '__main__':
    cli(run)
