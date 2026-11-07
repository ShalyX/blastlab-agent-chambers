"""Bounded fixed demonstration on the Vultr host.

This is NOT customer code execution. Public callers can trigger only a locked,
project-owned six-case worker. One public run per UTC day, two owner runs per day,
one active run globally, durable reservations across service restarts.
"""
from __future__ import annotations
import json
import os
import re
import secrets
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parent
STORE=Path(os.environ.get("BLASTLAB_SAMPLE_JOB_DIR","/var/lib/blastlab/sample-jobs"))
ARTIFACT_ROOT=Path(os.environ.get("BLASTLAB_SAMPLE_ARTIFACT_DIR","/var/lib/blastlab/experiments"))
SUPERVISOR=ROOT/"experiments/byoa-containment/host_supervisor.py"
VERIFIER=ROOT/"experiments/byoa-containment/verify_run.py"
SOCKET_ROOT=Path(os.environ.get("BLASTLAB_SOCKET_ROOT","/run/blastlab"))
ID=re.compile(r"^[a-f0-9]{32}$")
LOCK=threading.RLock()
MAX_RUNTIME=1000
DAILY_PUBLIC=1
DAILY_OWNER=2

def now()->str:
    return datetime.now(timezone.utc).isoformat()

def path_for(run_id:str)->Path:
    if not isinstance(run_id,str) or not ID.fullmatch(run_id):
        raise ValueError("Bad fixed sample job id")
    return STORE/(run_id+".json")

def atomic_json(path:Path, data:dict)->None:
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    try:path.parent.chmod(0o700)
    except OSError:pass
    tmp=path.with_name(path.name+"."+secrets.token_hex(4)+".tmp")
    try:
        with tmp.open("x",encoding="utf8") as f:
            json.dump(data,f,ensure_ascii=False,separators=(",",":"))
            f.write("\n")
        tmp.chmod(0o600)
        os.replace(tmp,path)
    finally:
        tmp.unlink(missing_ok=True)

def _load(run_id:str)->dict:
    return json.loads(path_for(run_id).read_text(encoding="utf8"))

def _public(job:dict)->dict:
    fields=("job_id","status","created_at","finished_at","stage","error","summary")
    return {k:job[k] for k in fields if k in job}

def _quota_path(owner:bool)->Path:
    today=datetime.now(timezone.utc).strftime("%Y%m%d")
    return STORE/f"budget-{today}-{'owner' if owner else 'public'}.json"

def _usage(owner:bool)->int:
    try:
        d=json.loads(_quota_path(owner).read_text(encoding="utf8"))
        return len(d.get("jobs",[]))
    except (OSError,ValueError,TypeError):
        return 0

def latest()->tuple[int,dict]:
    with LOCK:
        try:
            d=json.loads((STORE/"latest.json").read_text(encoding="utf8"))
            if not ID.fullmatch(d.get("job_id","")):raise ValueError()
            return get(d["job_id"])
        except (OSError,ValueError,TypeError,KeyError):
            return 200,{"status":"none","available_public_runs_today":max(0,DAILY_PUBLIC-_usage(False))}

def get(run_id:str)->tuple[int,dict]:
    try:
        if not ID.fullmatch(run_id):return 404,{"error":"Fixed sample run not found"}
        d=_load(run_id)
    except (OSError,ValueError,TypeError):
        return 404,{"error":"Fixed sample run not found"}
    # A server restart cannot silently retry an interrupted worker.
    if d.get("status") in ("queued","running"):
        try:
            age=(datetime.now(timezone.utc)-datetime.fromisoformat(d["created_at"])).total_seconds()
            if age>MAX_RUNTIME+90:
                d={**d,"status":"interrupted","error":"Worker did not complete within its safety window"}
        except (KeyError,ValueError,TypeError):pass
    return 200,{**_public(d),"available_public_runs_today":max(0,DAILY_PUBLIC-_usage(False))}

def start(*, owner:bool=False, requested:Any=None)->tuple[int,dict]:
    # No caller-selected task, code, model, URLs or credentials: fixed sample only.
    if requested != {"mode":"fixed-project-sample"}:
        return 400,{"error":"Only the fixed project-owned sample is supported"}
    with LOCK:
        quota=DAILY_OWNER if owner else DAILY_PUBLIC
        if _usage(owner)>=quota:
            return 429,{"error":"Daily fixed-sample compute allowance reached; archived evidence remains available"}
        try:
            current=json.loads((STORE/"latest.json").read_text(encoding="utf8"))
            if ID.fullmatch(current.get("job_id","")):
                running=_load(current["job_id"])
                if running.get("status") in ("queued","running"):
                    age=(datetime.now(timezone.utc)-datetime.fromisoformat(running["created_at"])).total_seconds()
                    if age<MAX_RUNTIME+90:
                        return 409,{"error":"A fixed sample is already executing","job_id":running["job_id"]}
        except (OSError,ValueError,KeyError,TypeError):pass
        run_id=secrets.token_hex(16)
        job={"job_id":run_id,"status":"queued","stage":"queued","created_at":now(),"public":not owner}
        STORE.mkdir(parents=True,exist_ok=True,mode=0o700)
        budget=_quota_path(owner)
        jobs=[]
        try:jobs=json.loads(budget.read_text(encoding="utf8")).get("jobs",[])
        except (OSError,ValueError,TypeError):pass
        # Atomic update protected within this process; durable across restarts.
        atomic_json(budget,{"date":datetime.now(timezone.utc).strftime("%Y%m%d"),
                            "jobs":jobs+[run_id]})
        atomic_json(path_for(run_id),job)
        atomic_json(STORE/"latest.json",{"job_id":run_id})
        threading.Thread(target=_execute,args=(run_id,),daemon=True,name="fixed-sample-"+run_id[:8]).start()
        return 202,{"job_id":run_id,"status":"queued",
                    "poll_url":"/api/contained-sample/jobs/"+run_id}

def _capture_evidence(artifact:Path)->dict:
    d=json.loads((artifact/"summary.json").read_text(encoding="utf8"))
    r=json.loads((artifact/"report.json").read_text(encoding="utf8"))
    v=json.loads((artifact/"independent-verification.json").read_text(encoding="utf8"))
    checks=v.get("checks",{})
    assert d.get("status")=="PASS" and v.get("status")=="PASS"
    assert len(checks)==22 and all(value is True for value in checks.values())
    assert d.get("run_id")==v.get("run_id")
    assert d.get("report_manifest_sha256")==r.get("manifest_sha256")==v.get("manifest_sha256")
    assert d.get("tests_completed")==r.get("tests_completed")==6
    return {
      "mode":"FRESH_PROJECT_OWNED_VULTR_CONTAINED_SAMPLE",
      "run_id":d["run_id"],"recorded_at":d["timestamp"],
      "cases_completed":d["tests_completed"],"observed_violations":r["breached"],
      "model":"glm-5.3","inference_calls":d["inference_proxy_calls"],
      "synthetic_actions_executed":d["worker_actions_executed"],
      "forbidden_actions_denied":d["forbidden_actions_denied"],
      "checks_passed":len(checks),"checks_total":22,
      "worker_absent_after_teardown":d["container_absent_after_teardown"],
      "inference_socket_removed":d["inference_socket_removed"],
      "network_egress_blocked":d["direct_network_egress_blocked"],
      "report_manifest_sha256":r["manifest_sha256"],
      "attack_plan_sha256":r["attack_plan_sha256"],
      "origin":"PROJECT_OWNED_HOST_OBSERVED_NOT_CUSTOMER",
      "limitations":"Host-observed sample, not a customer agent or cryptographically signed source attestation. Model responses/intent are runner-reported.",
      "case_results":[{"case_id":c["case_id"],"family":c["family"],"verdict":c["verdict"]}
                      for c in r["results"]],
    }

def _execute(run_id:str)->None:
    with LOCK:
        job=_load(run_id)
        job.update({"status":"running","stage":"launching_fixed_worker"})
        atomic_json(path_for(run_id),job)
    env={**os.environ,"BLASTLAB_SAMPLE_RUN_ID":run_id,"BLASTLAB_SOCKET_ROOT":str(SOCKET_ROOT)}
    process=None
    try:
        process=subprocess.Popen([sys.executable,str(SUPERVISOR)],cwd=ROOT,env=env,
              stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
        try:
            out,err=process.communicate(timeout=MAX_RUNTIME)
        except subprocess.TimeoutExpired:
            if process.poll() is None:
                try:os.killpg(process.pid,signal.SIGTERM)
                except (OSError,AttributeError):process.terminate()
                try:process.communicate(timeout=15)
                except subprocess.TimeoutExpired:process.kill();process.communicate(timeout=5)
            subprocess.run(["docker","rm","-f","blastlab-byoa-p12-"+run_id[:12]],
                           capture_output=True,timeout=15,check=False)
            raise RuntimeError("Fixed worker exceeded bounded execution time")
        if process.returncode!=0:
            raise RuntimeError("Fixed contained worker did not finish successfully")
        matches=list(ARTIFACT_ROOT.glob("byoa-containment-*-"+run_id[:8]))
        if len(matches)!=1:
            raise RuntimeError("Worker evidence directory unavailable")
        evidence=matches[0]
        check=subprocess.run([sys.executable,str(VERIFIER),str(evidence)],
              cwd=ROOT,env=env,capture_output=True,text=True,timeout=60,check=False)
        if check.returncode!=0:raise RuntimeError("Independent containment checks did not pass")
        result=_capture_evidence(evidence)
        with LOCK:
            job=_load(run_id)
            job.update({"status":"complete","stage":"verified","summary":result,"finished_at":now()})
            atomic_json(path_for(run_id),job)
    except Exception as exc:
        # Never expose secret material, raw model completion or provider traceback.
        print(json.dumps({"event":"contained_sample_failed","job_id":run_id,
                          "error_class":type(exc).__name__}),flush=True)
        with LOCK:
            job=_load(run_id)
            job.update({"status":"blocked","stage":"verification_failed",
                        "error":"The fixed contained sample could not be independently verified. Archived proof is still available.",
                        "finished_at":now()})
            atomic_json(path_for(run_id),job)
