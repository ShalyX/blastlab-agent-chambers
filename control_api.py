"""BlastLab trusted Chamber API.

Public users may replay evidence and launch severely bounded *scripted* Web
Chamber tests. Real model inference requires an operator token. No arbitrary
URLs, prompts, shell commands, model configuration or container parameters.
"""
from __future__ import annotations
import hmac
import json
import os
import re
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
from web_chamber import catalog, validate_config, DEFAULT_MISSION, DEFAULT_SCENARIO
from agent_lab_service import new_campaign, get_campaign, post_campaign, get_recovery_report
import contained_sample_service as contained_sample
from agent_lab import verify_import

ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get('BLASTLAB_PROOF_DIR', '/var/www/blastlab/data'))
RUNS_DIR = Path(os.environ.get('BLASTLAB_RUNS_DIR', '/var/lib/blastlab/runs'))
ENV_FILE = Path(os.environ.get('BLASTLAB_INFERENCE_ENV', '/etc/blastlab/inference.env'))
TOKEN_FILE = Path(os.environ.get('BLASTLAB_OPERATOR_TOKEN_FILE', '/etc/blastlab/operator.token'))
ALLOWED_ORIGIN = os.environ.get('BLASTLAB_ALLOWED_ORIGIN','https://blastlab.45-77-138-147.sslip.io').rstrip('/')
BIND_HOST = os.environ.get('BLASTLAB_HOST', '127.0.0.1')
BIND_PORT = int(os.environ.get('BLASTLAB_PORT','8123'))
JOB_LOCK = threading.RLock()
JOBS: dict[str,dict] = {}
LAST_STARTED: list[float] = []
PUBLIC_STARTED: list[float] = []
ACTIVE_JOB: str | None = None
MAX_JOBS_PER_HOUR = 8
MAX_PUBLIC_PER_HOUR = 4
MAX_PUBLIC_PER_DAY = 12
MAX_REQUEST_BYTES = 512
RUN_ID = re.compile(r'^(?:live|scripted)-[0-9a-f]{18}$')


def utc():
    return datetime.now(timezone.utc).isoformat()


def public_run(mode: str):
    if mode not in ('live','scripted'):
        raise ValueError('Unknown run mode')
    with (DATA_DIR/(mode+'.json')).open(encoding='utf-8') as handle:
        return json.load(handle)


def history_index():
    index=DATA_DIR/'history'/'index.json'
    try:
        entries=json.loads(index.read_text(encoding='utf-8'))
    except (OSError,json.JSONDecodeError):
        entries=[]
    return [e for e in entries if isinstance(e,dict) and RUN_ID.fullmatch(e.get('id',''))][:50]


def history_run(run_id):
    if not isinstance(run_id,str) or not RUN_ID.fullmatch(run_id):
        raise ValueError('Invalid run ID')
    with (DATA_DIR/'history'/(run_id+'.json')).open(encoding='utf-8') as source:
        return json.load(source)


def atomic_json(path:Path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name('.'+path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        tmp.replace(path)
    finally:
        if tmp.exists():tmp.unlink()


def record_run(clean:dict):
    data_dir=DATA_DIR/'history'
    data_dir.mkdir(parents=True,exist_ok=True)
    ident=clean['id']
    if not RUN_ID.fullmatch(ident):
        raise RuntimeError('Invalid sanitized run identifier')
    # Keep immutable addressable per-run snapshots as well as a latest alias.
    atomic_json(data_dir/(ident+'.json'), clean)
    atomic_json(DATA_DIR/(clean['origin']=='vultr-live' and 'live.json' or 'scripted.json'), clean)
    new={
        'id':ident,'origin':clean['origin'],'is_scripted':clean['is_scripted'],
        'mission_id':clean['mission_id'],'scenario':clean['scenario'],
        'timestamp':clean['timestamp'],'provider':clean['provider'],
        'completed':clean['summary']['acceptance_passed'],
        'value_cents':clean['summary']['value_cents'],
        'policy_denials':clean['summary']['denied_actions'],
        'public_digest':clean['proof']['public_sha256'],
    }
    index=[new]+[x for x in history_index() if x['id']!=ident]
    atomic_json(data_dir/'index.json',index[:50])


def authorized(raw: str|None)->bool:
    if not raw or not raw.startswith('Bearer '):
        return False
    try: token=TOKEN_FILE.read_text(encoding='utf-8').strip()
    except (OSError,UnicodeError):return False
    return len(token)>=25 and hmac.compare_digest(raw[7:].strip(),token)


def daily_public_usage_count():
    # Durable daily limiter avoids restart reset of billed public compute.
    today=datetime.now(timezone.utc).strftime('%Y%m%d')
    count_file=RUNS_DIR/('public-demo-usage-'+today+'.json')
    try:
        return int(json.loads(count_file.read_text()).get('count',0))
    except (OSError, ValueError, TypeError):
        return 0


def bump_daily_public_usage():
    today=datetime.now(timezone.utc).strftime('%Y%m%d')
    count_file=RUNS_DIR/('public-demo-usage-'+today+'.json')
    atomic_json(count_file,{'date':today,'count':daily_public_usage_count()+1})


def run_task(job_id:str, mode:str, mission:str=DEFAULT_MISSION,
             scenario:str=DEFAULT_SCENARIO):
    global ACTIVE_JOB
    with JOB_LOCK:
        JOBS[job_id]['status']='running'
        JOBS[job_id]['started_at']=utc()
    args=[sys.executable,str(ROOT/'agent_spike.py'),'run']
    if mode=='live':
        args+=['--env-file',str(ENV_FILE),'--provider','vultr']
    else:
        args+=['--provider','deterministic']
    args+=['--sandbox','docker','--output',str(RUNS_DIR),
           '--mission',mission,'--attack',scenario]
    error=None;out_dir=None
    try:
        before={p.name for p in RUNS_DIR.glob('agent-run-*') if p.is_dir()}
        finished=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',
                                timeout=260,check=False,
                                env={'PATH':os.environ.get('PATH','/usr/bin:/bin'),
                                     'HOME':'/tmp','LANG':'C.UTF-8'})
        if finished.returncode:
            raise RuntimeError('Agent acceptance failed (exit '+str(finished.returncode)+').')
        payload=json.loads(finished.stdout)
        candidate=Path(payload.get('run_dir',''))
        if not candidate.resolve().is_relative_to(RUNS_DIR.resolve()) or candidate.name in before:
            raise RuntimeError('Run output path not accepted.')
        if not (candidate/'result.json').is_file() or not (candidate/'trace.jsonl').is_file():
            raise RuntimeError('Run proof incomplete.')
        if not payload.get('acceptance_passed') or not payload.get('reset_verified'):
            raise RuntimeError('Acceptance or reset verification did not pass.')
        if (mode=='live')!=bool(payload.get('live_vultr_evidence')):
            raise RuntimeError('Provider/claim inconsistency.')
        if payload.get('mission_id')!=mission or payload.get('scenario')!=scenario:
            raise RuntimeError('Mission/scenario evidence mismatch.')
        out_dir=candidate
        clean=parse_run(candidate,mode)
        if not clean['proof']['hash_chain_valid'] or not clean['proof']['public_sha256']:
            raise RuntimeError('Original or sanitized chain verification failed.')
        if clean['mission_id']!=mission or clean['scenario']!=scenario:
            raise RuntimeError('Public proof configuration mismatch.')
        record_run(clean)
        with JOB_LOCK:
            JOBS[job_id].update(status='complete',completed_at=utc(),
                                run_id=clean['id'],summary=clean['summary'],
                                report=clean['report'],
                                public_sha256=clean['proof']['public_sha256'])
    except Exception as exc:
        # No private provider response, secret or shell invocation ever returned.
        reason=str(exc) if isinstance(exc,RuntimeError) else type(exc).__name__
        error=reason[:180]
        with JOB_LOCK:
            JOBS[job_id].update(status='failed',completed_at=utc(),error=error)
    finally:
        with JOB_LOCK: ACTIVE_JOB=None
        print(json.dumps({'event':'job_end','job_id':job_id,'mode':mode,
                          'mission':mission,'scenario':scenario,
                          'run_dir':str(out_dir) if out_dir else None,
                          'error':error}),flush=True)


class Handler(BaseHTTPRequestHandler):
    server_version='BlastLab-Chamber/2'
    sys_version=''

    def log_message(self, fmt,*args):
        # Logging only approved paths. Never request headers/body/secrets.
        print(json.dumps({'event':'http','method':self.command,
                          'path':urlparse(self.path).path[:85]}),flush=True)

    def send(self,status,body,cache=False):
        raw=json.dumps(body,ensure_ascii=False,separators=(',',':')).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(raw)))
        self.send_header('Cache-Control','public, max-age=5' if cache else 'no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('X-Frame-Options','DENY')
        self.send_header('Referrer-Policy','no-referrer')
        self.end_headers()
        try:self.wfile.write(raw)
        except (BrokenPipeError,ConnectionResetError):pass

    def origin_allowed(self,required=False):
        origin=self.headers.get('Origin')
        return bool(origin and origin.rstrip('/')==ALLOWED_ORIGIN) if required else (
            not origin or origin.rstrip('/')==ALLOWED_ORIGIN)

    def owner(self):
        if not authorized(self.headers.get('Authorization')):
            self.send(401,{'error':'Owner token required. Public scripted Chamber tests are available.'})
            return False
        if not self.origin_allowed():
            self.send(403,{'error':'Origin not permitted'})
            return False
        return True

    def read_body(self):
        max_size = 7500 if self.path.startswith('/api/agent-lab/') else MAX_REQUEST_BYTES
        if urlparse(self.path).path in ('/api/agent-lab/sessions', '/api/agent-lab/reports/verify'):
            max_size = 1100000  # Two bounded report exports plus the replay configuration.
        try:n=int(self.headers.get('Content-Length','0'))
        except ValueError:n=0
        if not 0<n<=max_size:
            self.send(413,{'error':'Invalid body size'})
            return None
        try:
            body=json.loads(self.rfile.read(n))
            if not isinstance(body,dict):raise ValueError()
            return body
        except (ValueError,UnicodeDecodeError):
            self.send(400,{'error':'Invalid JSON'})
            return None

    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/api/contained-sample/latest":
            code, data = contained_sample.latest()
            return self.send(code, data)
        fresh_job=re.fullmatch(r"/api/contained-sample/jobs/([a-f0-9]{32})",path)
        if fresh_job:
            code, data = contained_sample.get(fresh_job.group(1))
            return self.send(code, data)
        recovery_read=re.fullmatch(r'/api/agent-lab/sessions/([a-f0-9]{32})/recovery-report',path)
        if recovery_read:
            code, value = get_recovery_report(recovery_read.group(1), self.headers.get('Authorization'))
            return self.send(code, value)
        agent_read=re.fullmatch(r'/api/agent-lab/sessions/([a-f0-9]{32})/(status|next|report)',path)
        if agent_read:
            status,result=get_campaign(agent_read.group(1),self.headers.get('Authorization'),agent_read.group(2))
            return self.send(status,result)
        if path=='/api/health':
            return self.send(200,{'service':'BlastLab Web Chamber','status':'operational',
                                  'execution_mode':'public bounded scripted / owner live',
                                  'provider':'Vultr Serverless Inference',
                                  'chamber':'web','evidence':'real Vultr Docker traces'})
        if path=='/api/catalog':
            return self.send(200,catalog(),cache=True)
        if path in ('/api/runs/live','/api/runs/scripted'):
            try:return self.send(200,public_run(path.rsplit('/',1)[1]),cache=True)
            except (OSError,ValueError,json.JSONDecodeError):
                return self.send(503,{'error':'Recorded run unavailable'})
        if path=='/api/history':
            return self.send(200,{'runs':history_index()},cache=True)
        if path.startswith('/api/history/'):
            ident=path.rsplit('/',1)[1]
            try:return self.send(200,history_run(ident),cache=True)
            except (ValueError,FileNotFoundError,OSError,json.JSONDecodeError):
                return self.send(404,{'error':'Run not found'})
        if path.startswith('/api/demo-jobs/'):
            ident=path.rsplit('/',1)[1]
            if not re.fullmatch('[0-9a-f]{32}',ident):
                return self.send(404,{'error':'Job not found'})
            with JOB_LOCK: job=JOBS.get(ident)
            if not job or not job.get('public'):
                return self.send(404,{'error':'Job not found'})
            return self.send(200,{k:job.get(k) for k in
                ('job_id','status','mode','mission','scenario','error','run_id','summary','public_sha256')})
        if path.startswith('/api/jobs/'):
            if not self.owner():return
            ident=path.rsplit('/',1)[1]
            with JOB_LOCK: job=JOBS.get(ident)
            return self.send(200,dict(job)) if job else self.send(404,{'error':'Job not found'})
        return self.send(404,{'error':'Unknown endpoint'})

    def do_POST(self):
        global ACTIVE_JOB
        path=urlparse(self.path).path
        if path=="/api/contained-sample/jobs":
            if not self.origin_allowed(required=True):
                return self.send(403,{"error":"Origin not permitted"})
            body=self.read_body()
            if body is None:return
            code,data=contained_sample.start(
                owner=authorized(self.headers.get("Authorization")),requested=body)
            return self.send(code,data)
        if path=='/api/agent-lab/reports/verify':
            if not self.origin_allowed(required=True):
                return self.send(403,{'error':'Origin not permitted'})
            body=self.read_body()
            if body is None:return
            try:return self.send(200,verify_import(body))
            except ValueError as exc:return self.send(400,{'error':str(exc)})
        if path=='/api/agent-lab/sessions':
            if not self.origin_allowed(required=True):
                return self.send(403,{'error':'Origin not permitted'})
            body=self.read_body()
            if body is None:return
            # Owner-only QA allocation: authenticated using the existing
            # server-side operator token. Public clients cannot claim owner
            # privileges by adding a JSON field.
            is_operator=authorized(self.headers.get('Authorization'))
            status,result=new_campaign(body,owner=True) if is_operator else new_campaign(body)
            return self.send(status,result)
        agent_write=re.fullmatch(r'/api/agent-lab/sessions/([a-f0-9]{32})/response',path)
        if agent_write:
            body=self.read_body()
            if body is None:return
            status,result=post_campaign(agent_write.group(1),self.headers.get('Authorization'),body)
            return self.send(status,result)
        if path not in ('/api/runs','/api/demo-runs'):
            return self.send(404,{'error':'Unknown endpoint'})
        is_public=path=='/api/demo-runs'
        if is_public:
            if not self.origin_allowed(required=True):
                return self.send(403,{'error':'Origin not permitted'})
        elif not self.owner():
            return
        body=self.read_body()
        if body is None:return
        if is_public:
            if set(body)!={'mission','scenario'}:
                return self.send(400,{'error':'Exact mission and scenario required'})
            mode='scripted'
        else:
            if not set(body).issubset({'mode','mission','scenario'}) or 'mode' not in body:
                return self.send(400,{'error':'Unrecognized run fields'})
            mode=body['mode']
            if mode not in ('live','scripted') or type(mode) is not str:
                return self.send(400,{'error':'Unknown engine'})
        mission=body.get('mission',DEFAULT_MISSION)
        scenario=body.get('scenario',DEFAULT_SCENARIO)
        try:mission,scenario=validate_config(mission,scenario)
        except ValueError:
            return self.send(400,{'error':'Unknown safe mission/scenario'})
        with JOB_LOCK:
            now=time.monotonic()
            LAST_STARTED[:]=[t for t in LAST_STARTED if now-t<3600]
            PUBLIC_STARTED[:]=[t for t in PUBLIC_STARTED if now-t<3600]
            if ACTIVE_JOB:
                return self.send(409,{'error':'A Chamber is already running. Retry shortly.'})
            if len(LAST_STARTED)>=MAX_JOBS_PER_HOUR:
                return self.send(429,{'error':'Hourly compute budget exhausted'})
            if is_public:
                if len(PUBLIC_STARTED)>=MAX_PUBLIC_PER_HOUR or daily_public_usage_count()>=MAX_PUBLIC_PER_DAY:
                    return self.send(429,{'error':'Public test budget reached. Recorded evidence remains available.'})
                bump_daily_public_usage()
                PUBLIC_STARTED.append(now)
            ident=uuid.uuid4().hex
            LAST_STARTED.append(now)
            ACTIVE_JOB=ident
            JOBS[ident]={'job_id':ident,'mode':mode,'mission':mission,
                         'scenario':scenario,'status':'queued',
                         'public':is_public,'requested_at':utc()}
            threading.Thread(target=run_task,args=(ident,mode,mission,scenario),
                             daemon=True,name='chamber-'+ident[:8]).start()
            return self.send(202,{'job_id':ident,'mode':mode,'mission':mission,
                                  'scenario':scenario,'status':'queued',
                                  'poll_url':('/api/demo-jobs/' if is_public else '/api/jobs/')+ident})

def main():
    DATA_DIR.mkdir(parents=True,exist_ok=True)
    RUNS_DIR.mkdir(parents=True,exist_ok=True)
    if not TOKEN_FILE.exists():raise SystemExit('Missing protected owner token')
    server=ThreadingHTTPServer((BIND_HOST,BIND_PORT),Handler)
    print(json.dumps({'service':'blastlab-web-chamber','host':BIND_HOST,'port':BIND_PORT}),flush=True)
    try:server.serve_forever(.5)
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':main()
