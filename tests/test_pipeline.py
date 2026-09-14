import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import common
import inspect_database
import inspect_api
import inspect_project
import run_tests
import build_evidence
import check_consistency
import validate_references


class Contracts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'project'
        shutil.copytree(ROOT / 'examples/research-achievement-system', self.root,
                        ignore=shutil.ignore_patterns('evidence', 'artifacts', '.project-state.json', '__pycache__'))

    def tearDown(self):
        self.tmp.cleanup()

    def inspect(self):
        for collector in (inspect_project, inspect_database, inspect_api): collector.run(self.root)

    def test_configuration_and_path_boundary(self):
        cfg, _ = common.config(self.root)
        cfg['paths']['backend'] = '../escape'
        common.save(self.root / 'project.yaml', cfg)
        with self.assertRaises(ValueError): common.config(self.root)

    def test_unknown_role_and_field_rejected(self):
        cfg, _ = common.config(self.root)
        cfg['features'][0]['roles'] = ['unknown']
        common.save(self.root / 'project.yaml', cfg)
        with self.assertRaises(ValueError): common.config(self.root)
        cfg['unknown'] = True
        with self.assertRaises(Exception): common.validate(cfg, 'project.schema.yaml')

    def test_ddl_metadata(self):
        tables = inspect_database.parse((self.root / 'database/schema.sql').read_text())
        self.assertEqual(2, len(tables))
        table = tables[1]
        self.assertEqual('sys_user', table['foreign_keys'][0]['references_table'])
        self.assertEqual(['owner_id', 'status'], table['indexes'][0]['columns'])
        status = next(c for c in table['columns'] if c['name'] == 'status')
        self.assertEqual("'DRAFT'", status['default'])
        self.assertFalse(status['nullable'])
        self.assertEqual('32', status['length'])

    def test_ddl_unknown_syntax_never_silently_ignored(self):
        for sql in ['CREATE TABLE a (id JSON);', 'CREATE TABLE a(id BIGINT); ALTER TABLE a ADD b INT;', 'CREATE TABLE a (id INT, FOREIGN KEY(id) REFERENCES missing(id));']:
            with self.subTest(sql=sql), self.assertRaises(ValueError): inspect_database.parse(sql)

    def test_ddl_quoted_punctuation(self):
        tables = inspect_database.parse("CREATE TABLE a (id INT PRIMARY KEY, value VARCHAR(30) DEFAULT 'a,b;c' COMMENT 'it''s valid');")
        self.assertEqual("'a,b;c'", tables[0]['columns'][1]['default'])
        self.assertEqual("it's valid", tables[0]['columns'][1]['comment'])

    def test_api_literal_mapping(self):
        src = (self.root / 'backend/src/main/java/example/StatusController.java').read_text()
        items = inspect_api.parse(src, 'controller.java')
        self.assertEqual('/api/status', items[0]['url'])
        self.assertEqual([], items[0]['roles'])
        with self.assertRaises(ValueError): inspect_api.parse(src.replace('"/status"', 'ROUTE_CONSTANT'), 'controller.java')

    def test_missing_is_not_observed(self):
        self.inspect()
        build_evidence.run(self.root)
        report = check_consistency.run(self.root)
        self.assertEqual('PASS', report['integrity'])
        self.assertEqual('blocked', report['delivery_status'])
        self.assertIn('test-results: missing', report['delivery_blockers'])
        self.assertEqual('not_run', common.read(self.root / 'evidence/performance.json')['status'])

    def test_new_source_invalidates_manifest_and_cannot_be_resealed(self):
        self.inspect(); build_evidence.run(self.root)
        (self.root / 'backend/new-source.java').write_text('class NewSource {}')
        with self.assertRaises(ValueError): check_consistency.run(self.root)
        with self.assertRaises(ValueError): build_evidence.run(self.root)

    def test_evidence_tampering_detected(self):
        self.inspect(); build_evidence.run(self.root)
        path = self.root / 'evidence/api.json'
        data = common.read(path); data['data']['endpoints'][0]['url'] = '/invented'; common.save(path, data)
        with self.assertRaises(ValueError): check_consistency.run(self.root)

    def test_snapshot_invalidates_gate(self):
        common.save(self.root / '.project-state.json', {'schema_version':'1.0','snapshot':common.snapshot(self.root),'stages':{'test':{'status':'complete'}},'gates':{'1':{'note':'old'}}})
        (self.root / 'database/schema.sql').write_text('CREATE TABLE a (id INT);')
        state = common.state(self.root)
        self.assertEqual({}, state['gates']); self.assertEqual({}, state['stages'])

    def configure_test(self, body):
        cfg, _ = common.config(self.root)
        script = self.root / 'tests/fixture_runner.py'
        script.write_text(body)
        cfg['workflow']['test_command'] = [sys.executable, 'tests/fixture_runner.py', '{report_dir}']
        common.save(self.root / 'project.yaml', cfg)

    def test_zero_exit_without_reports_is_failure(self):
        self.configure_test('print("no tests executed")\n')
        with self.assertRaises(RuntimeError): run_tests.run(self.root)
        self.assertEqual('failed', common.read(self.root / 'evidence/test-results.json')['status'])
        with self.assertRaises(ValueError): build_evidence.run(self.root)

    def test_failed_and_skipped_junit_not_passed(self):
        for child in ['<failure message="real failure"/>', '<skipped/>']:
            self.configure_test('from pathlib import Path\nimport sys\nPath(sys.argv[1],"junit.xml").write_text(' + repr('<testsuite><testcase name="case" classname="fixture">'+child+'</testcase></testsuite>') + ')\n')
            with self.assertRaises(RuntimeError): run_tests.run(self.root)

    def test_real_golden_java_pipeline_and_resume(self):
        if not shutil.which('java') or not shutil.which('javac'): self.skipTest('JDK required for Golden Example')
        command = [sys.executable, str(ROOT/'scripts/pipeline.py'), '--project', str(self.root), 'all']
        result = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        test = common.read(self.root/'evidence/test-results.json')
        self.assertEqual(10, len(test['data']['cases']))
        self.assertTrue(all(c['status'] == 'PASS' for c in test['data']['cases']))
        old_hash = common.digest(self.root/'evidence/test-results.json')
        result = subprocess.run(command+['--resume'], text=True, capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(old_hash, common.digest(self.root/'evidence/test-results.json'))
        report = common.read(self.root/'artifacts/consistency-report.json')
        self.assertEqual('blocked', report['delivery_status'])

    def test_test_source_change_during_run_is_rejected(self):
        self.configure_test('''from pathlib import Path
import sys
Path("new-input.txt").write_text("changed")
Path(sys.argv[1], "junit.xml").write_text('<testsuite><testcase name="ok" classname="fixture"/></testsuite>')
''')
        with self.assertRaises(RuntimeError): run_tests.run(self.root)

    def test_missing_references_block(self):
        self.inspect(); build_evidence.run(self.root)
        with self.assertRaises(ValueError): validate_references.run(self.root)
        self.assertEqual('FAIL', common.read(self.root/'artifacts/reference-report.json')['status'])

    def test_observed_requires_typed_data_and_source(self):
        with self.assertRaises(Exception): common.evidence(self.root, 'database', {'made_up': []}, [])


if __name__ == '__main__': unittest.main()
