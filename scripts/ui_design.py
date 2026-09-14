"""Persist explicit UI selection. Recommendation never selects a design."""
import argparse
from pathlib import Path
from copy import deepcopy
from common import SKILL, config, digest, now, read, save, validate
import workflow_state as workflow


def merge(base, override):
    value=deepcopy(base)
    for key,item in override.items():
        if isinstance(item,dict) and isinstance(value.get(key),dict):value[key]=merge(value[key],item)
        else:value[key]=deepcopy(item)
    return value


def recommend():
    presets=read(SKILL/'templates/ui-presets.yaml')
    return {k:presets['presets'][k] for k in presets['recommended']}


def select(root,preset,who,note,overrides=None,dashboard=None):
    root=root.resolve();config(root)
    value=workflow.load(root);workflow.predecessors(value,2)
    if value['phases']['2']['status'] != 'IN_PROGRESS':raise ValueError('UI selection requires active Phase 2')
    if not who.strip() or not note.strip():raise ValueError('Record the explicit user selection')
    presets=read(SKILL/'templates/ui-presets.yaml')['presets']
    design=deepcopy(presets[preset])
    if dashboard:design['dashboard']=deepcopy(presets[dashboard]['dashboard'])
    design=merge(design,overrides or {});validate(design,'ui.schema.yaml')
    save(root/'ui-design.yaml',design)
    decision={'preset':preset,'dashboard_preset':dashboard,'confirmed_by':who,'note':note,'at':now(),'sha256':digest(root/'ui-design.yaml')}
    save(root/'decisions/ui-design.yaml',decision)
    # Auxiliary decision evidence, intentionally outside the existing 12-kind manifest.
    save(root/'evidence/ui-design.json',{'schema_version':'0.2','kind':'ui-design','status':'planned','source':'ui-design.yaml',**decision,'data':design})
    return design


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['recommend','select']);p.add_argument('--project',type=Path)
    p.add_argument('--preset',choices=list('ABCD'));p.add_argument('--dashboard',choices=list('ABCD'));p.add_argument('--overrides',type=Path)
    p.add_argument('--confirmed-by',default='');p.add_argument('--note',default='');a=p.parse_args()
    if a.command=='recommend':result=recommend()
    else:
        if not a.project or not a.preset:p.error('--project and --preset are required')
        result=select(a.project,a.preset,a.confirmed_by,a.note,read(a.overrides) if a.overrides else {},a.dashboard)
    print(__import__('json').dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
