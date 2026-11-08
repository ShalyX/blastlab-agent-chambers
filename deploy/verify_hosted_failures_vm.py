"""Actual Docker fail-closed tests, no paid inference or success substitutions."""
import json
import sys
from pathlib import Path

sys.path.insert(0, '/opt/blastlab')
sys.path.insert(0, str(Path(__file__).resolve().parent))
import hosted_byoa as hosted
import agent_lab as lab

def main():
    findings = []
    hosted.LIMIT_SECONDS = 3
    for label, source in [
        ('timeout', 'def respond(case):\n while True: pass\n'),
        ('invalid_result', 'def respond(case):\n return [1,2,3]\n'),
        ('oversized_output', 'import os\ndef respond(case):\n os.write(1,b"x"*70000)\n return {}\n'),
        ('no_model_fallback', 'def respond(case):\n return {"answer":"fake success","tool_calls":[]}\n'),
    ]:
        state, _ = lab.create_session({'agent_name': 'Negative execution test',
            'task': 'Summarize a synthetic document.', 'forbidden_tools': ['send_http'],
            'execution_mode': 'vultr_sandbox'})
        try:
            hosted.run_worker(state, {'files': {'agent.py': source}, 'adapter': 'agent:respond'}, None)
        except Exception:
            pass
        else:
            raise AssertionError('Invalid worker returned a success receipt: '+label)
        name = 'blastlab-customer-'+state['id']
        assert not hosted.docker('ps', '-aq', '--filter', 'name=^/'+name+'$').strip()
        findings.append({'scenario': label, 'failed_closed': True, 'worker_absent': True})
    print(json.dumps({'status': 'PASS', 'negative_real_docker_checks': findings}))

if __name__ == '__main__':
    main()
