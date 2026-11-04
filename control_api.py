"""BlastLab trusted demo gateway.

Read-only evidence replay is public. Running a fixed scenario is operator-only.
Untrusted browser clients cannot send arbitrary tasks, URLs, shell commands,
environment variables or host paths to the sandbox controller.
"""
from __future__ import annotations

import hmac
import json
import os
import secrets
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from evidence_export import parse_run

ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get('BLASTLAB_PROOF_DIR', '/var/www/blastlab/data'))
RUNS_DIR = Path(os.environ.get('BLASTLAB_RUNS_DIR', '/var/lib/blastlab/runs'))
ENV_FILE = Path(os.environ.get('BLASTLAB_INFERENCE_ENV', '/etc/blastlab/inference.env'))
TOKEN_FILE = Path(os.environ.get('BLASTLAB_OPERATOR_TOKEN_FILE', '/etc/blastlab/operator.token'))
ALLOWED_ORIGIN = os.environ.get('BLASTLAB_ALLOWED_ORIGIN', 'https://blastlab.45-77-138-147.sslip.io').rstrip('/')
BIND_HOST = os.environ.get('BLASTLAB_HOST', '127.0.0.1')
BIND_PORT = int(os.environ.get('BLASTLAB_PORT', '8123'))
JOB_LOCK = threading.RLock()
JOBS: dict[str, dict] = {}
LAST_STARTED: list[float] = []
ACTIVE_JOB: str | None = None
MAX_JOBS_PER_HOUR = 8
MAX_REQUEST_BYTES = 512

def public_run(mode: str):
    if mode not in ('live', 'scripted'):
        raise ValueError('Unknown recorded run')
    path = DATA_DIR / (mode + '.json')
    with path.open(encoding='utf-8') as handle:
        return json.load(handle)

def authorized(raw: str | None) -> bool:
    if not raw or not raw.startswith('Bearer '):
        return False
    try:
        token = TOKEN_FILE.read_text(encoding='utf-8').strip()
    except (OSError, UnicodeError):
        return False
    return len(token) >= 25 and hmac.compare_digest(raw[len('Bearer '):].strip(), token)

def run_task(job_id: str, mode: str):
    global ACTIVE_JOB
    with JOB_LOCK:
        JOBS[job_id]['status'] = 'running'
        JOBS[job_id]['started_at'] = datetime.now(timezone.utc).isoformat()
    args = [sys.executable, str(ROOT / 'agent_spike.py'), 'run']
    if mode == 'live':
        args += ['--env-file', str(ENV_FILE), '--provider', 'vultr']
    else:
        args += ['--provider', 'deterministic']
    args += ['--sandbox', 'docker', '--output', str(RUNS_DIR)]
    error = None
    output_dir = None
    try:
        before = {x.name for x in RUNS_DIR.glob('agent-run-*') if x.is_dir()}
        # subprocess uses fixed args from trusted code; no shell, no client text in argv.
        finished = subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                                  encoding='utf-8', timeout=260, check=False,
                                  env={'PATH': os.environ.get('PATH', '/usr/bin:/bin'),
                                       'HOME': '/tmp', 'LANG': 'C.UTF-8'})
        if finished.returncode != 0:
            raise RuntimeError('Agent run did not pass acceptance (exit ' + str(finished.returncode) + ').')
        payload = json.loads(finished.stdout)
        candidate = Path(payload.get('run_dir', ''))
        if not candidate.is_relative_to(RUNS_DIR.resolve()) or candidate.name in before:
            raise RuntimeError('Run output path could not be verified.')
        if not (candidate / 'result.json').is_file() or not (candidate / 'trace.jsonl').is_file():
            raise RuntimeError('Run proof was incomplete.')
        if not payload.get('acceptance_passed') or not payload.get('reset_verified'):
            raise RuntimeError('Run did not pass the real acceptance gate.')
        if mode == 'live' and not payload.get('live_vultr_evidence'):
            raise RuntimeError('Vultr inference evidence absent.')
        if mode != 'live' and payload.get('live_vultr_evidence'):
            raise RuntimeError('Mode evidence contradiction.')
        output_dir = candidate
        clean = parse_run(candidate, mode)
        if not clean['proof']['hash_chain_valid']:
            raise RuntimeError('Hash-chain verification failed.')
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        target = DATA_DIR / (mode + '.json')
        temporary = DATA_DIR / ('.' + mode + '-' + job_id + '.tmp')
        temporary.write_text(json.dumps(clean, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        temporary.replace(target)
        with JOB_LOCK:
            JOBS[job_id].update(status='complete', completed_at=datetime.now(timezone.utc).isoformat(),
                                summary=clean['summary'], trace_sha256=clean['proof']['trace_sha256'])
    except Exception as exc:
        # No arbitrary transport response bodies or private credentials returned to clients.
        allowed = str(exc) if isinstance(exc, RuntimeError) else type(exc).__name__
        error = allowed[:220]
        with JOB_LOCK:
            JOBS[job_id].update(status='failed', completed_at=datetime.now(timezone.utc).isoformat(),
                                error=error)
    finally:
        with JOB_LOCK:
            ACTIVE_JOB = None
        # Complete job metadata is maintained only in RAM; traces stay on the Vultr VM.
        print(json.dumps({'event':'job_completed','job_id':job_id,'mode':mode,
                          'run_dir':str(output_dir) if output_dir else None,'error':error}), flush=True)

class Handler(BaseHTTPRequestHandler):
    server_version = 'BlastLab-Gateway/1'
    sys_version = ''

    def log_message(self, fmt, *args):
        # No credentials in logs. URLs are fixed and bounded by handlers.
        print(json.dumps({'event':'http','method':getattr(self, 'command',''),
                          'path':self.path.split('?')[0][:90],'status':str(args[1]) if len(args)>1 else ''}), flush=True)

    def _send(self, status: int, body: dict, cache: bool=False):
        raw = json.dumps(body, ensure_ascii=False, separators=(',',':')).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'public, max-age=10' if cache else 'no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('X-Frame-Options','DENY')
        self.send_header('X-Robots-Tag','noindex')
        self.end_headers()
        try:
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _origin_allowed(self):
        origin = self.headers.get('Origin')
        # curl clients may omit Origin. Browsers must match the exact public host.
        return not origin or origin.rstrip('/') == ALLOWED_ORIGIN

    def _require_operator(self):
        if not authorized(self.headers.get('Authorization')):
            self._send(401, {'error':'Operator token required; public evidence replay is still available.'})
            return False
        if not self._origin_allowed():
            self._send(403, {'error':'Origin is not permitted.'})
            return False
        return True

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/health':
            return self._send(200, {'service':'BlastLab trusted controller','status':'operational',
                                    'execution_mode':'operator-only','provider':'Vultr Serverless Inference',
                                    'evidence':'recorded real VM traces'})
        if path in ('/api/runs/live', '/api/runs/scripted'):
            mode = path.rsplit('/',1)[1]
            try:
                return self._send(200, public_run(mode),cache=True)
            except (ValueError, FileNotFoundError, OSError, json.JSONDecodeError):
                return self._send(503, {'error':'Recorded evidence is temporarily unavailable.'})
        if path.startswith('/api/jobs/'):
            if not self._require_operator():return
            job_id = path.rsplit('/',1)[1]
            with JOB_LOCK:
                job = JOBS.get(job_id)
                return self._send(200, dict(job)) if job else self._send(404, {'error':'Job not found.'})
        return self._send(404, {'error':'Unknown endpoint.'})

    def do_POST(self):
        global ACTIVE_JOB
        if urlparse(self.path).path != '/api/runs':
            return self._send(404, {'error':'Unknown endpoint.'})
        if not self._require_operator():return
        try:
            size = int(self.headers.get('Content-Length','0'))
        except ValueError:
            size = 0
        if not (0 < size <= MAX_REQUEST_BYTES):
            return self._send(413, {'error':'Invalid request body size.'})
        try:
            body=json.loads(self.rfile.read(size))
        except (ValueError, UnicodeDecodeError):
            return self._send(400, {'error':'Invalid request body.'})
        if not isinstance(body,dict) or set(body)!={'mode'} or body.get('mode') not in ('live','scripted'):
            return self._send(400, {'error':'Only a fixed live or scripted scenario can run.'})
        mode = body['mode']
        with JOB_LOCK:
            now=time.monotonic()
            LAST_STARTED[:] = [t for t in LAST_STARTED if now-t<3600]
            if ACTIVE_JOB:
                return self._send(409, {'error':'Another sandbox run is already in progress.'})
            if len(LAST_STARTED)>=MAX_JOBS_PER_HOUR:
                return self._send(429, {'error':'Hourly operator limit reached; protect inference costs.'})
            job_id=uuid.uuid4().hex
            LAST_STARTED.append(now)
            ACTIVE_JOB=job_id
            JOBS[job_id]={'job_id':job_id,'mode':mode,'status':'queued',
                          'requested_at':datetime.now(timezone.utc).isoformat()}
            threading.Thread(target=run_task,args=(job_id,mode),daemon=True,name='blastlab-run-'+job_id[:7]).start()
            return self._send(202, {'job_id':job_id,'status':'queued','mode':mode})

def main():
    DATA_DIR.mkdir(parents=True,exist_ok=True)
    RUNS_DIR.mkdir(parents=True,exist_ok=True)
    if not TOKEN_FILE.exists():
        print('Missing protected operator token; refusing to start.', file=sys.stderr)
        raise SystemExit(2)
    server=ThreadingHTTPServer((BIND_HOST,BIND_PORT),Handler)
    print(json.dumps({'event':'gateway_ready','host':BIND_HOST,'port':BIND_PORT,
                      'proof_directory':str(DATA_DIR),'run_mode':'owner_only'}),flush=True)
    try:
        server.serve_forever(poll_interval=.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__=='__main__':
    main()
