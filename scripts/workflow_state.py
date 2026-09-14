"""Interactive phase controller layered above the unchanged v0.1 tool pipeline."""
import argparse
import logging
from pathlib import Path
from common import SKILL, config, digest, inputs, now, read, resolve, save

PHASES = read(SKILL / 'config/phases.yaml')
IMPACTS = {
 'requirements': (1, ['design','database','api','backend','frontend','tests','screenshots','evidence','thesis']),
 'database': (1, ['database','api','backend','tests','evidence','thesis.ch3','thesis.ch4','thesis.ch5']),
 'ui': (2, ['frontend.styles','screenshots','thesis.ch4.images','docx.layout']),
 'implementation': (3, ['frontend','related.api','tests','screenshots','evidence','thesis.ch4','thesis.ch5']),
 'evidence': (4, ['tests','screenshots','diagrams','evidence','thesis']),
 'template': (5, ['docx','format-check','toc','pagination','figure-table-layout']),
}


def persist(root, value):
    save(root / '.workflow-state.json', value)
    save(root / 'decisions/approvals.yaml', {'schema_version':'0.2','history':value['history']})


def invalidate(value, change, note):
    first, affected = IMPACTS[change]
    for number in range(first, 7):
        entry = value['phases'][str(number)]
        if entry['status'] != 'DRAFT' or number == first:
            entry['status'] = 'STALE'
        entry.pop('approval', None)
        entry['invalidated_products'] = sorted(set(entry.get('invalidated_products', []) + affected))
    value['current_phase'] = min(first, next((n for n in range(1,7) if value['phases'][str(n)]['status'] != 'APPROVED'), first))
    value['history'].append({'action':'reopen','change':change,'phase':first,'note':note,'at':now(),'affected':affected})


def load(root):
    root = root.resolve()
    config(root,use_runtime=False)
    path = root / '.workflow-state.json'
    value = read(path) if path.exists() else {'schema_version':'0.2','current_phase':1,
        'phases':{str(n):{'status':'DRAFT','artifacts':[]} for n in range(1,7)},'history':[]}
    from common import validate
    validate(value, 'workflow-state.schema.json')
    # Only previously reviewed outputs and runtime source sets are watched. New later-phase
    # artifacts do not invalidate earlier approvals. Template controls never touch v0.1 evidence.
    for number in range(1,7):
        entry = value['phases'][str(number)]
        if entry['status'] not in ('WAITING_CONFIRMATION','APPROVED','COMPLETED'): continue
        changed = any(not resolve(root, a['path']).is_file() or digest(resolve(root,a['path'])) != a['sha256'] for a in entry['artifacts'])
        if number == 3 and entry.get('runtime_sources') != runtime_sources(root): changed = True
        if changed:
            invalidate(value, {1:'requirements',2:'ui',3:'implementation',4:'evidence',5:'template',6:'template'}[number], 'Reviewed inputs changed on disk')
            persist(root,value)
            break
    return value


def runtime_sources(root):
    cfg, _ = config(root,use_runtime=False)
    paths = cfg['paths']
    prefixes = [paths[k].rstrip('/')+'/' for k in ('frontend','backend','database')]
    return [x for x in inputs(root) if any(x['path'].startswith(p) for p in prefixes) or x['path'] == paths['compose']]


def predecessors(value, number):
    for n in range(1,number):
        if value['phases'][str(n)]['status'] != 'APPROVED':
            raise ValueError(f'Phase {n} must be APPROVED before Phase {number}')


def start(root, number):
    value = load(root); predecessors(value,number)
    entry = value['phases'][str(number)]
    if entry['status'] not in ('DRAFT','STALE'): raise ValueError('Phase must be DRAFT or STALE; reopen before revision')
    entry['status'] = 'IN_PROGRESS'
    value['current_phase'] = number
    persist(root,value)
    return value


def review_artifacts(root, number, extra=()):
    paths = list(dict.fromkeys(PHASES[str(number)]['artifacts'] + list(extra) + (['project.yaml'] if number == 1 else [])))
    result=[]
    for path in paths:
        file=resolve(root,path)
        if not file.is_file() or file.stat().st_size == 0: raise ValueError(f'Missing/empty Gate {number} artifact: {path}')
        result.append({'path':path,'sha256':digest(file)})
    if number == 2:
        from common import validate
        design=read(root/'ui-design.yaml');validate(design,'ui.schema.yaml')
        decision=read(root/'decisions/ui-design.yaml')
        if decision['sha256'] != digest(root/'ui-design.yaml'): raise ValueError('UI changed without an explicit selection decision')
        result.append({'path':'decisions/ui-design.yaml','sha256':digest(root/'decisions/ui-design.yaml')})
    if number == 4:
        from common import verify_record
        import check_consistency
        check_consistency.run(root)
        for kind in ('test-results','screenshots','diagrams'):
            item=verify_record(root,kind)
            if item['status'] != 'observed' or not item['data'].get('cases',item['data'].get('items')):
                raise ValueError(f'Gate 4 requires actual nonempty {kind}')
    if number == 5:
        from resolve_thesis_template import verify
        lock=verify(root)
        if lock['needs_format_review']: raise ValueError('Template formatting must be reviewed/extracted before Gate 5')
        for item in lock['files']:
            result.append({'path':item['path'],'sha256':item['sha256']})
    if number == 6:
        report=read(root/'artifacts/consistency-report.json')
        if report.get('delivery_status') != 'complete': raise ValueError('Final delivery checks are still blocked')
    return result


def ready(root, number, extra=()):
    value=load(root);predecessors(value,number)
    entry=value['phases'][str(number)]
    if entry['status'] != 'IN_PROGRESS': raise ValueError('Start phase before requesting confirmation')
    entry['artifacts']=review_artifacts(root,number,extra)
    if number == 3: entry['runtime_sources']=runtime_sources(root)
    entry['status']='WAITING_CONFIRMATION'
    persist(root,value)
    return value


def approve(root, number, who, note, automatic=False):
    if not who.strip() or not note.strip(): raise ValueError('Approval identity and user instruction are required')
    value=load(root);predecessors(value,number)
    entry=value['phases'][str(number)]
    if entry['status'] != 'WAITING_CONFIRMATION': raise ValueError('Phase must be ready and WAITING_CONFIRMATION')
    if automatic and not (config(root)[0]['workflow']['auto_approve_gates'] or value.get('automation',{}).get('enabled')):
        raise ValueError('Automatic approval is disabled in project configuration')
    # Recheck semantic readiness; review artifacts may include additional source files.
    review_artifacts(root,number,[a['path'] for a in entry['artifacts']])
    entry['status']='COMPLETED' if number == 6 else 'APPROVED'
    entry['invalidated_products']=[]
    entry['approval']={'confirmed_by':who,'note':note,'at':now(),'automatic':automatic}
    value['history'].append({'action':'approve','phase':number,**entry['approval']})
    value['current_phase']=min(number+1,6)
    persist(root,value)
    return value


def reopen(root, change, note):
    if not note.strip(): raise ValueError('Revision reason is required')
    value=load(root);invalidate(value,change,note);persist(root,value)
    save(root/f'decisions/{"requirements" if change in ("requirements","database") else "revision"}.yaml',
         {'change':change,'note':note,'at':now(),'status':'revision_requested'})
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,required=True)
    parser.add_argument('command',choices=['status','start','ready','approve','reopen','authorize-auto','disable-auto'])
    parser.add_argument('--phase',type=int,choices=range(1,7))
    parser.add_argument('--change',choices=IMPACTS)
    parser.add_argument('--note',default='')
    parser.add_argument('--confirmed-by',default='')
    parser.add_argument('--automatic',action='store_true')
    parser.add_argument('--artifact',action='append',default=[])
    args=parser.parse_args();root=args.project.resolve()
    try:
        if args.command=='status': result=load(root);persist(root,result)
        elif args.command in ('authorize-auto','disable-auto'):
            if not args.confirmed_by.strip() or not args.note.strip():raise ValueError('Record the explicit user instruction')
            result=load(root)
            result['automation']={'enabled':args.command=='authorize-auto','confirmed_by':args.confirmed_by,'note':args.note,'at':now()}
            result['history'].append({'action':args.command,**result['automation']})
            persist(root,result)
        elif args.command=='reopen':
            change=args.change or {1:'requirements',2:'ui',3:'implementation',4:'evidence',5:'template',6:'template'}.get(args.phase)
            if not change: raise ValueError('Specify --change or --phase')
            result=reopen(root,change,args.note)
        else:
            if not args.phase: raise ValueError('--phase is required')
            if args.command=='start': result=start(root,args.phase)
            elif args.command=='ready': result=ready(root,args.phase,args.artifact)
            else: result=approve(root,args.phase,args.confirmed_by,args.note,args.automatic)
        print(__import__('json').dumps(result,ensure_ascii=False,indent=2))
    except Exception:
        logging.exception('Phase operation failed');return 1
    return 0

if __name__=='__main__': raise SystemExit(main())
