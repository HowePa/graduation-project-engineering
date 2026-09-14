"""Compatibility entry point: Gate N now approves user Phase N."""
import argparse
from pathlib import Path
import workflow_state as workflow

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path,required=True)
    p.add_argument('--gate',type=int,choices=range(1,7),required=True)
    p.add_argument('--confirmed-by',required=True);p.add_argument('--note',required=True)
    p.add_argument('--artifact',action='append',default=[])
    p.add_argument('--automatic',action='store_true')
    a=p.parse_args();root=a.project.resolve()
    # Legacy extra artifacts must already have been reviewed by ready; no shortcut to approval.
    value=workflow.load(root)
    reviewed={x['path'] for x in value['phases'][str(a.gate)]['artifacts']}
    if set(a.artifact)-reviewed:raise ValueError('Additional artifacts must first be included in phase ready')
    workflow.approve(root,a.gate,a.confirmed_by,a.note,a.automatic)

if __name__=='__main__':main()
