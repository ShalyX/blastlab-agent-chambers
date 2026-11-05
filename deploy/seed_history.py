"""Seed a browseable public history from actual old and new VM run evidence.

Only sanitized proof JSON is published. Original log remains private.
"""
from pathlib import Path
from control_api import record_run, history_index, RUNS_DIR
from evidence_export import parse_run

RUNS=[
 ('agent-run-pn6mlhdr','live'),
 ('agent-run-ve47wfrx','scripted'),
 ('agent-run-b_5sq4jz','scripted'),
 ('agent-run-diiyvn4t','live'),
]
for directory,origin in RUNS:
    path=RUNS_DIR/directory
    if not path.is_dir():
        print('MISSING_HISTORICAL_CASE',directory)
        continue
    evidence=parse_run(path,origin)
    if not evidence['proof']['hash_chain_valid']:
        raise RuntimeError('Original log chain invalid: '+directory)
    record_run(evidence)
    print('HISTORY_SEEDED',evidence['id'],evidence['mission_id'],
          evidence['scenario'],'denials',evidence['summary']['denied_actions'])
print('HISTORY_COUNT',len(history_index()))
