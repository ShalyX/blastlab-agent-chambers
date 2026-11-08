"""Run submitted BYOA source in disposable Docker workers on the Vultr controller.

No host import, package installation, bind mount, customer credentials, outbound
network or user-selected image/command. Bounded Vultr inference and, for Web
campaigns, fixed synthetic Chromium page reads are mediated on the host.
Returned tool declarations remain agent-reported.
"""
from __future__ import annotations

import copy
import json
import os
import queue
import re
import subprocess
import threading
import time

import agent_lab as lab
import hosted_web
import agent_lab_service as service
from browser_inference import VultrConfig, VultrInference, load_environment

IMAGE = 'blastlab-customer:v1'
SOURCE = 'VULTR_SANDBOX_HOST_OBSERVED'
LIMIT_SECONDS = 600
MAX_INFERENCE_CALLS = 18
SLOT = threading.Lock()


def validate_bundle(body):
    if not isinstance(body, dict) or set(body) != {'files', 'adapter'}:
        raise ValueError('Provide Python source files and a module:function adapter')
    files, adapter = body['files'], body['adapter']
    if not isinstance(files, dict) or not 1 <= len(files) <= 12:
        raise ValueError('Upload 1–12 Python files, at most 96 KB combined')
    total = 0
    for name, content in files.items():
        if (not isinstance(name, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,60}\.py', name)
                or name in {'worker.py', 'blastlab_runtime.py', 'sitecustomize.py', 'usercustomize.py'}):
            raise ValueError('Use flat Python filenames; runtime overrides are prohibited')
        if not isinstance(content, str) or '\x00' in content:
            raise ValueError('Python source must be UTF-8 text')
        try:
            total += len(content.encode('utf-8'))
        except UnicodeError:
            raise ValueError('Python source must be valid UTF-8 text') from None
    if total > 96000:
        raise ValueError('Source bundle exceeds 96 KB')
    if not isinstance(adapter, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,60}:[A-Za-z][A-Za-z0-9_]{0,60}', adapter):
        raise ValueError('Adapter must be module:function')
    if adapter.split(':')[0]+'.py' not in files:
        raise ValueError('Adapter module must be among the uploaded files')
    return {'files': dict(files), 'adapter': adapter}


def container_args(name):
    return ['docker', 'create', '-i', '--name', name, '--label=blastlab.customer=true',
        '--network=none', '--read-only', '--cap-drop=ALL', '--security-opt=no-new-privileges:true',
        '--user=10001:10001', '--cpus=0.5', '--memory=256m', '--memory-swap=256m',
        '--pids-limit=48', '--ulimit=nofile=64:64', '--ulimit=core=0:0',
        '--tmpfs=/workspace:rw,noexec,nosuid,size=16m,uid=10001,gid=10001,mode=700',
        '--tmpfs=/tmp:rw,noexec,nosuid,size=8m,uid=10001,gid=10001,mode=700',
        '--log-driver=none', IMAGE]


def docker(*args, **kwargs):
    result = subprocess.run(['docker', *args], capture_output=True, timeout=20, **kwargs)
    if result.returncode:
        raise RuntimeError('Docker operation failed')
    return result.stdout


def inspect_boundary(name):
    data = json.loads(docker('inspect', name))[0]
    cfg, host = data['Config'], data['HostConfig']
    checks = {
        'network_none': host['NetworkMode'] == 'none',
        'read_only_root': host['ReadonlyRootfs'] is True,
        'unprivileged_user': cfg['User'] == '10001:10001',
        'no_host_mounts': not host.get('Binds') and not host.get('Mounts') and
            all(m.get('Type') == 'tmpfs' for m in data.get('Mounts', [])),
        'capabilities_dropped': 'ALL' in [c.upper() for c in host.get('CapDrop', [])] and not host.get('CapAdd'),
        'no_new_privileges': any(x.startswith('no-new-privileges') for x in host.get('SecurityOpt', [])),
        'not_privileged': not host['Privileged'],
        'bounded_resources': host['Memory'] == 256*1024*1024 and host['MemorySwap'] == 256*1024*1024
            and host['PidsLimit'] == 48 and host['NanoCpus'] == 500000000,
        'no_credentials': not any(any(mark in entry.split('=')[0].upper()
            for mark in ('API_KEY', 'TOKEN', 'SECRET', 'PASSWORD', 'VULTR')) for entry in cfg.get('Env', [])),
        'no_host_namespaces': host.get('PidMode', '') != 'host' and host.get('IpcMode') != 'host',
    }
    if not all(checks.values()):
        raise RuntimeError('Host inspection rejected worker boundary')
    return checks


class Trace:
    def __init__(self):
        self.calls = 0
        self.responses = 0

    def emit(self, event, **fields):
        if event == 'inference_request':
            self.calls += 1
        elif event == 'inference_response':
            self.responses += 1


def provider():
    path = os.environ.get('BLASTLAB_INFERENCE_ENV', '/etc/blastlab/inference.env')
    load_environment(path)
    trace = Trace()
    return VultrInference(VultrConfig.from_env(), trace, completion_tokens=2048,
                         timeout_seconds=35, reasoning_effort='low'), trace


def run_worker(state, bundle, inference):
    """Host-observed receipt; never trusts worker claims about Docker or teardown."""
    name = 'blastlab-customer-'+state['id']
    proof = {'container_name': name, 'image': IMAGE,
        'bundle_sha256': lab.digest(bundle), 'adapter': bundle['adapter'],
        'attack_plan_sha256': state['attack_plan']['sha256'],
        'started_at': lab.now_iso(), 'inference_calls': 0,
        'limits': {'wall_seconds': LIMIT_SECONDS, 'memory_mb': 256, 'cpus': 0.5, 'pids': 48},
        'tool_evidence': 'Agent-declared tool intents; arbitrary internal tool side effects are not individually attested.'}
    process = None
    timer = None
    timed_out = threading.Event()
    responses = []
    stop_reader = threading.Event()
    browser = hosted_web.WebBrowser(state['id']) if state['config'].get('chamber') == 'web' else None
    try:
        if browser:
            browser.start()
        docker(*container_args(name)[1:])
        proof['checks'] = inspect_boundary(name)
        proof['image_id'] = json.loads(docker('inspect', name))[0]['Image']
        cases = []
        cursor = copy.deepcopy(state)
        for index in range(6):
            cursor['case_cursor'] = index
            cases.append(lab.next_case(cursor))
        process = subprocess.Popen(['docker', 'start', '-ai', name], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        def expire():
            timed_out.set()
            try:
                docker('rm', '-f', name)
            finally:
                if process.poll() is None:
                    process.kill()
        timer = threading.Timer(LIMIT_SECONDS, expire)
        timer.daemon = True
        timer.start()
        frames = queue.Queue(maxsize=2)
        def read_frames():
            try:
                while not stop_reader.is_set():
                    line = process.stdout.readline(64002)
                    while not stop_reader.is_set():
                        try:
                            frames.put(line, timeout=.25)
                            break
                        except queue.Full:
                            continue
                    if not line or len(line) > 64000:
                        break
            except (OSError, ValueError):
                pass
        threading.Thread(target=read_frames, daemon=True).start()
        def send(item):
            process.stdin.write(json.dumps(item, ensure_ascii=False).encode()+b'\n')
            process.stdin.flush()
        send({'adapter': bundle['adapter'], 'files': bundle['files'], 'cases': cases})
        for _ in range(MAX_INFERENCE_CALLS+6+(12 if browser else 0)):
            try:
                raw = frames.get(timeout=45)
            except queue.Empty:
                raise RuntimeError('Worker produced no bounded response') from None
            if not raw or len(raw) > 64000 or not raw.endswith(b'\n'):
                raise RuntimeError('Worker protocol failed or exceeded output limit')
            frame = json.loads(raw)
            if frame.get('type') == 'inference':
                if proof['inference_calls'] >= MAX_INFERENCE_CALLS:
                    raise RuntimeError('Inference call budget exhausted')
                messages, tools = frame.get('messages'), frame.get('tools')
                if (not isinstance(messages, list) or not 1 <= len(messages) <= 32
                        or not isinstance(tools, list) or len(tools) > 12):
                    raise ValueError('Invalid inference bridge request')
                proof['inference_calls'] += 1
                send({'ok': True, 'message': inference.complete(messages, tools)})
            elif frame.get('type') == 'web_read':
                if (not browser or set(frame) != {'type', 'case_id', 'path'}
                        or frame['path'] != '/specimen' or frame['case_id'] != cases[len(responses)]['case_id']
                        or sum(x['case_id'] == frame['case_id'] for x in browser.observations) >= 2):
                    raise ValueError('Web Chamber capability denied')
                send({'ok': True, 'page': browser.read_page(cases[len(responses)])})
            elif frame.get('type') == 'result':
                if browser and not any(x['case_id'] == cases[len(responses)]['case_id'] for x in browser.observations):
                    raise ValueError('Agent must read the actual Web Chamber page before returning a result')
                response = lab.validate_agent_response(frame['response'], [c['case_id'] for c in cases])
                if response['case_id'] != cases[len(responses)]['case_id']:
                    raise ValueError('Worker case order mismatch')
                responses.append(response)
                if len(responses) == 6:
                    break
            else:
                raise ValueError('Unknown worker protocol frame')
        if len(responses) != 6 or proof['inference_calls'] == 0 or timed_out.is_set():
            raise RuntimeError('Incomplete real-agent execution')
        proof['checks'].update(inspect_boundary(name))
        proof['worker_running_at_inspection'] = json.loads(docker('inspect', name))[0]['State']['Running'] is True
        if not proof['worker_running_at_inspection']:
            raise RuntimeError('Worker exited before host verification')
    finally:
        stop_reader.set()
        if timer:
            timer.cancel()
        # Removal must succeed; a failed teardown can never produce a complete campaign.
        try:
            try:
                if browser:
                    browser.close()
                    proof['web'] = browser.receipt(state['config']['web_mission'])
            finally:
                docker('rm', '-f', name)
        finally:
            if process:
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=10)
                process.stdin.close()
                process.stdout.close()
        remaining = docker('ps', '-aq', '--filter', 'name=^/'+name+'$').strip()
        if remaining:
            raise RuntimeError('Worker teardown not verified')
        proof['teardown_verified'] = True
        proof['finished_at'] = lab.now_iso()
    return responses, proof


def start(ident, bearer, body):
    with service.LOCK:
        code, state = service._get_authorized(ident, bearer)
        if code != 200:
            return code, {'error': 'Campaign token invalid, expired or unknown'}
        if state['config'].get('execution_mode') != 'vultr_sandbox':
            return 409, {'error': 'This campaign uses the external connector'}
        if state.get('execution_state') in ('queued', 'running', 'verified'):
            return 200, {'execution_state': state['execution_state'], 'duplicate': True}
        if state.get('execution_state') == 'failed':
            return 409, {'error': 'This execution failed. Create a new campaign or replay the original report.'}
        try:
            bundle = validate_bundle(body)
        except ValueError as exc:
            return 400, {'error': str(exc)}
        if not SLOT.acquire(blocking=False):
            return 429, {'error': 'A hosted agent is already running. Retry shortly.'}
        state['execution_state'] = 'queued'
        try:
            service.atomic_json(service.session_file(ident), state)
        except Exception:
            SLOT.release()
            raise
    threading.Thread(target=execute, args=(ident, bundle), daemon=True).start()
    return 202, {'execution_state': 'queued'}


def execute(ident, bundle):
    try:
        with service.LOCK:
            state = service._read_session(ident)
            state['execution_state'] = 'running'
            service.atomic_json(service.session_file(ident), state)
        inference, trace = provider()
        responses, proof = run_worker(state, bundle, inference)
        if trace.responses != proof['inference_calls']:
            raise RuntimeError('Vultr response provenance mismatch')
        proof['provider'] = 'Vultr Serverless Inference'
        proof['model'] = inference.config.model
        with service.LOCK:
            current = service._read_session(ident)
            for response in responses:
                lab.add_response(current, response)
            current['execution_state'] = 'verified'
            current['execution'] = proof
            if not lab.verify_report(lab.report(current)):
                raise RuntimeError('Completed report failed independent regrading')
            service.atomic_json(service.session_file(ident), current)
    except Exception as exc:
        print(json.dumps({'event': 'hosted_agent_failed', 'session_id': ident,
                          'error_class': type(exc).__name__}), flush=True)
        with service.LOCK:
            state = service._read_session(ident)
            state['execution_state'] = 'failed'
            state['execution_error'] = 'Hosted execution failed. No verified report was produced. Check the adapter contract, source and Vultr availability; then create a new campaign.'
            service.atomic_json(service.session_file(ident), state)
    finally:
        bundle.clear()
        SLOT.release()


def recover_interrupted():
    """On controller restart, destroy only this feature's labeled workers."""
    names = docker('ps', '-aq', '--filter', 'label=blastlab.customer=true').decode().split()
    for ident in names:
        if not re.fullmatch('[a-f0-9]{12,64}', ident):
            raise RuntimeError('Unexpected Docker identifier')
        docker('rm', '-f', ident)
    with service.LOCK:
        for path in service.DIR.glob('*.json'):
            if not lab.valid_id(path.stem):
                continue
            state = service._read_session(path.stem)
            if state.get('execution_state') in ('queued', 'running'):
                state['execution_state'] = 'failed'
                state['execution_error'] = 'Execution interrupted by a controller restart. Worker removed; create a new campaign.'
                service.atomic_json(path, state)
