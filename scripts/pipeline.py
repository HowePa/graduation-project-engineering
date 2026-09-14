"""First runnable slice: inspect -> test -> evidence -> integrity check."""
import argparse
import logging
from pathlib import Path
import inspect_project
import inspect_database
import inspect_api
import run_tests
import build_evidence
import check_consistency
from common import config, stage, read, snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('command', choices=['inspect', 'test', 'evidence', 'check', 'all'])
    parser.add_argument('--resume', action='store_true', help='Skip successful stages only while all inputs and evidence remain valid')
    args = parser.parse_args()
    root = args.project.resolve()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
    current = args.command
    try:
        config(root)
        steps = ['inspect', 'test', 'evidence', 'check'] if args.command == 'all' else [args.command]
        can_resume = False
        if args.resume and (root / '.project-state.json').exists():
            old = read(root / '.project-state.json')
            if old['snapshot'] == snapshot(root):
                try:
                    check_consistency.run(root)
                    can_resume = True
                except Exception:
                    logging.info('Resume cache invalid; rerunning stages')
        for current in steps:
            if can_resume and current != 'check' and old.get('stages', {}).get(current, {}).get('status') == 'complete':
                logging.info('Current verified outputs: skipping %s', current)
                continue
            logging.info('Running %s', current)
            if current == 'inspect':
                for collector in (inspect_project, inspect_database, inspect_api): collector.run(root)
            elif current == 'test': run_tests.run(root)
            elif current == 'evidence': build_evidence.run(root)
            else: check_consistency.run(root)
            stage(root, current, 'complete')
        logging.info('Requested slice complete. Full graduation delivery remains gated; see consistency report.')
    except Exception as exc:
        if (root / 'project.yaml').exists(): stage(root, current, 'failed', str(exc))
        logging.exception('Pipeline stopped; no downstream execution')
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
