"""v0.2 integration tests use the Golden Example in isolated temporary directories."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import common
import workflow_state as wf
import ui_design as ui
import resolve_thesis_template as resolver
import inspect_project, inspect_database, inspect_api, build_evidence, check_consistency


class Interactive(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=(Path(self.tmp.name)/'golden').resolve()
        shutil.copytree(ROOT/'examples/research-achievement-system',self.root,
            ignore=shutil.ignore_patterns('evidence','artifacts','.project-state.json','.workflow-state.json','decisions','inputs','thesis-runtime.yaml','.thesis-template-lock.yaml','__pycache__'))

    def tearDown(self):self.tmp.cleanup()

    def artifacts(self,number):
        for path in wf.PHASES[str(number)]['artifacts']:
            file=self.root/path;file.parent.mkdir(parents=True,exist_ok=True)
            file.write_text('Isolated controller test fixture; not real acceptance evidence.\n')

    def phase1(self):
        wf.start(self.root,1);self.artifacts(1);wf.ready(self.root,1);wf.approve(self.root,1,'test reviewer','确认当前测试设计')

    def phase2(self):
        self.phase1();wf.start(self.root,2)
        ui.select(self.root,'A','test reviewer','选择 A')
        (self.root/'docs/06-implementation-plan.md').write_text('Isolated implementation plan fixture')
        wf.ready(self.root,2);wf.approve(self.root,2,'test reviewer','确认 UI 和实现计划')

    def test_A_default_no_prompt_and_idempotent(self):
        before=common.snapshot(self.root)
        lock=resolver.run(self.root)
        self.assertEqual('skill-default',lock['source'])
        self.assertFalse(lock['needs_format_review'])
        self.assertEqual(before,common.snapshot(self.root))
        self.assertEqual(lock,resolver.run(self.root))
        self.assertTrue((self.root/lock['template']).is_file())

    def test_B_conversation_docx_persisted_over_project(self):
        doc=Path(self.tmp.name)/'thesis.docx'
        with zipfile.ZipFile(doc,'w') as z:z.writestr('word/document.xml','<document/>')
        project=common.read(self.root/'thesis.yaml');project['template']='project-format.yaml'
        common.save(self.root/'project-format.yaml',common.read(ROOT/'templates/default-thesis.yaml'))
        common.save(self.root/'thesis.yaml',project)
        lock=resolver.run(self.root,template=doc,overrides={'references':{'minimum':20}})
        self.assertEqual('conversation',lock['source']);self.assertTrue(lock['needs_format_review'])
        doc.unlink()  # Subsequent use must not depend on chat attachment remaining accessible.
        self.assertEqual(lock,resolver.run(self.root))
        self.assertEqual(20,common.config(self.root)[1]['references']['minimum'])
        self.assertEqual(lock['template'],common.read(self.root/'thesis-runtime.yaml')['template'])

    def test_template_priority_and_custom_chapters(self):
        project=common.read(self.root/'thesis.yaml');project['template']='project-format.yaml'
        common.save(self.root/'project-format.yaml',{'references':{'minimum':18}});common.save(self.root/'thesis.yaml',project)
        self.assertEqual('project',resolver.run(self.root)['source'])
        conversation=Path(self.tmp.name)/'format.yaml'
        common.save(conversation,{'references':{'minimum':19},'chapters':['概述','相关技术','需求分析','系统设计','系统实现','测试']})
        resolver.run(self.root,template=conversation,overrides={'references':{'minimum':20}})
        runtime=common.read(self.root/'thesis-runtime.yaml')
        self.assertEqual(20,runtime['references']['minimum']);self.assertEqual(6,len(runtime['chapters']))

    def test_unreadable_attachment_no_false_lock(self):
        with self.assertRaises(ValueError):resolver.run(self.root,template=Path(self.tmp.name)/'missing.docx')
        self.assertFalse((self.root/'.thesis-template-lock.yaml').exists())

    def test_C_requirements_revision_blocks_development(self):
        self.phase2();wf.start(self.root,3)
        state=wf.reopen(self.root,'requirements','科研秘书增加批量审核功能')
        self.assertEqual(1,state['current_phase']);self.assertEqual('STALE',state['phases']['3']['status'])
        self.assertIn('database',state['phases']['3']['invalidated_products'])
        with self.assertRaises(ValueError):wf.start(self.root,3)
        wf.start(self.root,1);wf.ready(self.root,1)
        self.assertEqual('WAITING_CONFIRMATION',wf.load(self.root)['phases']['1']['status'])
        with self.assertRaises(ValueError):wf.start(self.root,2)

    def test_D_custom_ui_and_no_implicit_selection(self):
        self.phase1();wf.start(self.root,2)
        self.assertEqual(3,len(ui.recommend()));self.assertFalse((self.root/'ui-design.yaml').exists())
        (self.root/'docs/06-implementation-plan.md').write_text('plan')
        with self.assertRaises(ValueError):wf.ready(self.root,2)
        result=ui.select(self.root,'A','reviewer','选 A，主色改为 #1677FF，不要阴影',{'theme':{'primary':'#1677FF'},'components':{'shadow':'none'}},dashboard='D')
        self.assertEqual('#1677FF',result['theme']['primary']);self.assertEqual('none',result['components']['shadow'])
        self.assertIn('area',result['dashboard']['charts'])
        wf.ready(self.root,2)
        with self.assertRaises(ValueError):wf.start(self.root,3)
        wf.approve(self.root,2,'reviewer','确认实现计划');wf.start(self.root,3)

    def test_E_system_revision_requires_new_confirmation(self):
        self.phase2();wf.start(self.root,3);self.artifacts(3);wf.ready(self.root,3);wf.approve(self.root,3,'reviewer','确认演示')
        state=wf.reopen(self.root,'implementation','统计首页增加两个卡片')
        self.assertEqual('APPROVED',state['phases']['2']['status'])
        self.assertEqual('STALE',state['phases']['3']['status'])
        self.assertIn('screenshots',state['phases']['3']['invalidated_products'])
        with self.assertRaises(ValueError):wf.start(self.root,4)

    def test_ui_change_does_not_invalidate_backend_products(self):
        self.phase2()
        value=wf.reopen(self.root,'ui','卡片取消阴影')
        self.assertEqual('APPROVED',value['phases']['1']['status'])
        self.assertNotIn('backend',value['phases']['3']['invalidated_products'])
        self.assertIn('frontend.styles',value['phases']['3']['invalidated_products'])

    def test_F_template_change_preserves_actual_evidence_and_system_approval(self):
        self.phase2();wf.start(self.root,3);self.artifacts(3);wf.ready(self.root,3);wf.approve(self.root,3,'reviewer','确认系统测试夹具')
        for collector in (inspect_project,inspect_database,inspect_api):collector.run(self.root)
        build_evidence.run(self.root)
        evidence={p.name:common.digest(p) for p in (self.root/'evidence').glob('*.json')}
        before=common.snapshot(self.root)
        resolver.run(self.root)
        template=Path(self.tmp.name)/'new.yaml';common.save(template,{'format':{'body_pt':11}})
        resolver.run(self.root,template=template)
        self.assertEqual(before,common.snapshot(self.root))
        self.assertEqual(evidence,{p.name:common.digest(p) for p in (self.root/'evidence').glob('*.json')})
        self.assertEqual('APPROVED',wf.load(self.root)['phases']['3']['status'])
        self.assertEqual('PASS',check_consistency.run(self.root)['integrity'])
        self.assertNotIn('evidence',wf.load(self.root)['phases']['5']['invalidated_products'])

    def test_file_edits_invalidate_review_without_reopen_command(self):
        self.phase2()
        (self.root/'docs/02-requirement-analysis.md').write_text('Changed requirements')
        with self.assertRaises(ValueError):wf.start(self.root,3)
        self.assertEqual('STALE',wf.load(self.root)['phases']['1']['status'])

    def test_runtime_new_source_file_invalidates_approval(self):
        self.phase2();wf.start(self.root,3);self.artifacts(3);wf.ready(self.root,3);wf.approve(self.root,3,'reviewer','确认')
        (self.root/'frontend/src/new.js').write_text('export const x = 1;')
        self.assertEqual('STALE',wf.load(self.root)['phases']['3']['status'])

    def test_reset_recovers_from_stale_conversation_attachment(self):
        template=Path(self.tmp.name)/'custom.yaml';common.save(template,{'references':{'minimum':20}})
        lock=resolver.run(self.root,template=template)
        (self.root/lock['template']).write_text('{}')
        result=resolver.run(self.root,reset=True)
        self.assertEqual('skill-default',result['source'])
        resolver.verify(self.root)

    def test_template_tampering_detected(self):
        lock=resolver.run(self.root)
        (self.root/lock['template']).write_text('{}')
        with self.assertRaises(ValueError):resolver.verify(self.root)

    def test_gates_cli_cannot_bypass_ready(self):
        result=subprocess.run([sys.executable,str(ROOT/'scripts/gates.py'),'--project',str(self.root),'--gate','1','--confirmed-by','reviewer','--note','确认'],capture_output=True)
        self.assertNotEqual(0,result.returncode)

    def test_binary_review_blocks_gate5_until_extracted(self):
        doc=Path(self.tmp.name)/'thesis.docx'
        with zipfile.ZipFile(doc,'w') as z:z.writestr('word/document.xml','<document/>')
        resolver.run(self.root,template=doc)
        (self.root/'thesis').mkdir(exist_ok=True)
        (self.root/'thesis/outline.md').write_text('Outline test fixture')
        (self.root/'docs/thesis-material-plan.md').write_text('Material plan test fixture')
        with self.assertRaises(ValueError):wf.review_artifacts(self.root,5)
        resolver.run(self.root,template_rules={'format':{'body_pt':12},'chapters':['概述','分析','设计','实现','测试']},reviewed_by='test reviewer')
        self.assertTrue(wf.review_artifacts(self.root,5))

    def test_template_replacement_revokes_old_binary_format_review(self):
        first=Path(self.tmp.name)/'first.docx';second=Path(self.tmp.name)/'second.docx'
        for file,text in [(first,'first'),(second,'second')]:
            with zipfile.ZipFile(file,'w') as z:z.writestr('word/document.xml',text)
        resolver.run(self.root,template=first,template_rules={'format':{'body_pt':11}},reviewed_by='test reviewer')
        self.assertTrue(resolver.run(self.root,template=second)['needs_format_review'])
        self.assertEqual(12,common.read(self.root/'thesis-runtime.yaml')['format']['body_pt'])

    def test_later_auto_authorization_does_not_invalidate_design(self):
        self.phase1();before=common.snapshot(self.root)
        result=subprocess.run([sys.executable,str(ROOT/'scripts/workflow_state.py'),'--project',str(self.root),'authorize-auto','--confirmed-by','test reviewer','--note','自动执行后续阶段'],capture_output=True)
        self.assertEqual(0,result.returncode,result.stderr)
        self.assertEqual('APPROVED',wf.load(self.root)['phases']['1']['status'])
        self.assertEqual(before,common.snapshot(self.root))
        self.assertTrue(wf.load(self.root)['automation']['enabled'])

    def test_gate4_rejects_unimplemented_screenshots(self):
        self.phase2();wf.start(self.root,3);self.artifacts(3);wf.ready(self.root,3);wf.approve(self.root,3,'reviewer','确认测试夹具')
        wf.start(self.root,4)
        with self.assertRaises(ValueError):wf.ready(self.root,4)
        with self.assertRaises(ValueError):wf.start(self.root,5)

    def test_auto_mode_still_requires_ready_and_ui_choice(self):
        cfg=common.read(self.root/'project.yaml');cfg['workflow']['auto_approve_gates']=True;common.save(self.root/'project.yaml',cfg)
        with self.assertRaises(ValueError):wf.approve(self.root,1,'auto','explicit configured mode',True)
        wf.start(self.root,1);self.artifacts(1);wf.ready(self.root,1);wf.approve(self.root,1,'auto','explicit configured mode',True)
        wf.start(self.root,2)
        with self.assertRaises(ValueError):wf.ready(self.root,2)

if __name__=='__main__':unittest.main()
