"""Persist conversational template selection and effective rules without claiming PDF/DOCX layout extraction."""
import argparse
import hashlib
import logging
from pathlib import Path
import shutil
import zipfile
from common import SKILL, config, digest, now, read, resolve, save, validate
from ui_design import merge


def inspect_file(path):
    suffix=path.suffix.lower()
    if suffix=='.docx':
        with zipfile.ZipFile(path) as archive:
            if 'word/document.xml' not in archive.namelist():raise ValueError('Invalid Word template')
    elif suffix=='.pdf':
        if not path.read_bytes().startswith(b'%PDF-'):raise ValueError('Invalid PDF guide')
    elif suffix in ('.yaml','.yml','.json'):
        if not isinstance(read(path),dict):raise ValueError('Formatting template must be a mapping')
    else:raise ValueError('Supported templates/guides: DOCX, PDF, YAML, JSON')


def copy_input(root,path):
    path=Path(path).resolve()
    if not path.is_file():raise ValueError(f'Cannot access supplied attachment: {path}; place it in the project inputs directory')
    inspect_file(path)
    # Content-addressed files preserve earlier conversational decisions.
    dest=resolve(root,'inputs/thesis-template/'+digest(path)+path.suffix.lower())
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest != path:shutil.copyfile(path,dest)
    return dest.relative_to(root).as_posix()


def verify(root):
    lock=read(root/'.thesis-template-lock.yaml')
    if lock.get('schema_version') != '0.2':raise ValueError('Unsupported template lock')
    for item in lock['files']:
        path=resolve(root,item['path'])
        if not path.is_file() or digest(path)!=item['sha256']:raise ValueError(f'Template input changed: {item["path"]}; resolve again')
    if digest(root/'thesis-runtime.yaml')!=lock['runtime_sha256']:raise ValueError('Runtime formatting changed without resolving template')
    validate(read(root/'thesis-runtime.yaml'),'thesis.schema.yaml')
    return lock


def run(root,template=None,guide=None,overrides=None,template_rules=None,reviewed_by=None,reset=False):
    root=root.resolve();cfg,project_rules=config(root,use_runtime=False)
    old=read(root/'.thesis-template-lock.yaml') if (root/'.thesis-template-lock.yaml').exists() else None
    prior=read(root/'decisions/thesis-template.yaml') if (root/'decisions/thesis-template.yaml').exists() else {}
    supplied=bool(template or guide)
    if template:
        selected=copy_input(root,template);source='conversation'
    elif not reset and old and old['source']=='conversation':
        # A later conversation still uses the persisted explicit choice unless reset.
        selected=old['template'];source='conversation';inspect_file(resolve(root,selected))
    elif project_rules.get('template'):
        selected=copy_input(root,resolve(root,project_rules['template']));source='project'
    elif resolve(root,cfg['thesis']['template']).is_file():
        selected=copy_input(root,resolve(root,cfg['thesis']['template']));source='project-legacy'
    else:
        selected=copy_input(root,SKILL/'templates/default-thesis.yaml');source='skill-default'
    guide_path=copy_input(root,guide) if guide else (None if reset or template else prior.get('format_guide'))
    effective=read(SKILL/'templates/default-thesis.yaml')
    effective=merge(effective,project_rules)
    selected_path=resolve(root,selected)
    binary=selected_path.suffix in ('.docx','.pdf') or bool(guide_path and Path(guide_path).suffix in ('.docx','.pdf'))
    if selected_path.suffix in ('.yaml','.yml','.json'):
        # Default file is a base, not a higher-priority override over project formatting.
        if source!='skill-default':effective=merge(effective,read(selected_path))
    if guide_path and Path(guide_path).suffix in ('.yaml','.yml','.json'):
        effective=merge(effective,read(resolve(root,guide_path)))
    selection_changed = bool(old and (old['template'] != selected or old.get('format_guide') != guide_path))
    if old and not supplied and not reset and old['source']=='conversation':
        for item in old['files']:
            if not resolve(root,item['path']).is_file() or digest(resolve(root,item['path'])) != item['sha256']:
                raise ValueError('Persisted attachment changed; explicitly reselect it for a new review')
    extracted = template_rules if template_rules is not None else ({} if supplied or reset or selection_changed else prior.get('template_rules',{}))
    if extracted:effective=merge(effective,extracted)
    conversation_overrides=merge({} if reset else prior.get('overrides',{}),overrides or {})
    effective=merge(effective,conversation_overrides)
    effective['template']=selected
    validate(effective,'thesis.schema.yaml')
    previous_review = None if supplied or reset or selection_changed else prior.get('reviewed_by')
    reviewer=reviewed_by or previous_review
    if reviewed_by and not extracted:raise ValueError('Record extracted template rules before confirming binary formatting review')
    files=[{'path':p,'sha256':digest(resolve(root,p))} for p in dict.fromkeys([selected]+([guide_path] if guide_path else []))]
    decision={'source':source,'template':selected,'format_guide':guide_path,'overrides':conversation_overrides,
              'template_rules':extracted,'reviewed_by':reviewer}
    # Only effective selection changes invalidate Phase 5/6. No mutation of system evidence.
    runtime_hash=hashlib.sha256((__import__('json').dumps(effective,ensure_ascii=False,indent=2)+'\n').encode()).hexdigest()
    changed=not old or old['runtime_sha256']!=runtime_hash or old['files']!=files or prior!=decision
    if not changed:
        verify(root);return old
    import workflow_state
    if (root/'.workflow-state.json').exists():workflow_state.reopen(root,'template','Thesis template or explicit format requirements changed')
    save(root/'thesis-runtime.yaml',effective)
    lock={'schema_version':'0.2','source':source,'template':selected,'format_guide':guide_path,'files':files,
          'runtime_sha256':digest(root/'thesis-runtime.yaml'),'needs_format_review':bool(binary and not reviewer),'resolved_at':now()}
    save(root/'.thesis-template-lock.yaml',lock)
    save(root/'decisions/thesis-template.yaml',decision)
    return lock


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',type=Path,required=True)
    p.add_argument('--template',type=Path);p.add_argument('--guide',type=Path);p.add_argument('--overrides',type=Path)
    p.add_argument('--template-rules',type=Path);p.add_argument('--reviewed-by');p.add_argument('--reset',action='store_true')
    a=p.parse_args()
    try:
        result=run(a.project,a.template,a.guide,read(a.overrides) if a.overrides else None,read(a.template_rules) if a.template_rules else None,a.reviewed_by,a.reset)
        print(__import__('json').dumps(result,ensure_ascii=False,indent=2))
    except Exception:logging.exception('Template resolution failed');return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
