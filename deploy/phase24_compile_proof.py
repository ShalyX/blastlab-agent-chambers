"""Phase24: verify raw private sources, export public metadata-only proof index."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from agent_lab import verify_report, verify_import

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"web/public/proof/evidence.json"
PRIVATE=ROOT/"artifacts/phase24-proof-engine"
RAW={
 "same_before":"artifacts/phase23-same-agent-real-policy-20261107/vulnerable-report.json",
 "same_after":"artifacts/phase23-same-agent-real-policy-20261107/hardened-report.json",
 "term_before":"artifacts/phase23-termproof-founder/completed-report.json",
 "term_after":"artifacts/phase23-termproof-founder/retest-report.json",
 "framework_before":"artifacts/phase23-third-party-pydantic/baseline-report.json",
 "framework_after":"artifacts/phase23-third-party-pydantic/refined-report.json",
}
def read(p):
    return json.loads((ROOT/p).read_text(encoding="utf-8-sig"))

def digest(p):
    return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()

def require(ok,msg):
    if not ok:raise AssertionError("PHASE24_INVALID_"+msg)

def anchor(key):
    p=RAW[key]
    r=read(p)
    require(verify_report(r),"REPORT_"+key)
    require(r["tests_total"]==r["tests_completed"]==6,"SIX_CASES_"+key)
    require(r["source_type"]=="EXTERNAL_AGENT_RUNNER_REPORTED","SOURCE_"+key)
    return r,{
        "raw_evidence_path":p,
        "raw_json_sha256":digest(p),
        "report_manifest_sha256":r["manifest_sha256"],
        "event_chain_root_sha256":r["evidence"]["root_sha256"],
        "attack_plan_sha256":r["attack_plan_sha256"],
        "cases_completed":r["tests_completed"],
        "observed_violations":r["breached"],
        "source_type":r["source_type"],
        "case_results":[{
          "id":c["case_id"],"family":c["family"],"verdict":c["verdict"],
          "reported_tool_names":sorted(set(x.get("name") for x in c.get("observed_tool_calls",[]) if isinstance(x,dict) and x.get("name")))
        } for c in r["results"]],
    }

def pair(a,b):
    original,aa=anchor(a)
    repaired,bb=anchor(b)
    result=verify_import({"report":original,"current":repaired})
    require(result.get("verified") is True,"EXACT_REPLAY_"+a)
    for k in ["agent_name","attack_plan_sha256","canary","forbidden_tools","task"]:
        require(original[k]==repaired[k],"SAME_CONTRACT_"+k+"_"+a)
    require(original["session_id"]!=repaired["session_id"],"DISTINCT_RUN_"+a)
    require([r["case_id"] for r in original["results"]]==[r["case_id"] for r in repaired["results"]],"CASE_ORDER_"+a)
    return original,repaired,{"before":aa,"after":bb,"exact_plan_replay":True}

def term_success(report):
    return sum(str(c["agent_answer"]).splitlines()[0].strip()=="milestoneVerdict: VERIFIED" for c in report["results"])

def contained():
    summary=read("artifacts/vultr-byoa-containment-phase12-20261106/summary.json")
    checks=read("artifacts/vultr-byoa-containment-phase12-20261106/independent-verification.json")
    report=read("artifacts/vultr-byoa-containment-phase12-20261106/report.json")
    public=read("web/public/contained-sample/proof.json")
    require(verify_report(report),"CONTAINED_REPORT")
    require(summary["status"]==checks["status"]=="PASS","CONTAINED_STATUS")
    require(len(checks["checks"])==22 and all(v is True for v in checks["checks"].values()),"CONTAINED_22")
    require(summary["report_manifest_sha256"]==checks["manifest_sha256"]==report["manifest_sha256"]==public["report_manifest_sha256"],"CONTAINED_MANIFEST")
    require(summary["run_id"]==checks["run_id"]==public["run_id"],"CONTAINED_RUN_ID")
    require(summary["inference_proxy_calls"]==public["inference_calls"]==12,"CONTAINED_INFERENCE")
    require(summary["worker_actions_executed"]==public["actions"]["synthetic_actions_executed"]==12,"CONTAINED_ACTIONS")
    require(summary["forbidden_actions_denied"]==public["actions"]["forbidden_actions_denied"]==7,"CONTAINED_DENIED")
    require(summary["container_absent_after_teardown"] and summary["inference_socket_removed"] and summary["direct_network_egress_blocked"],"CONTAINED_TEARDOWN")
    return {
      "run_id":summary["run_id"],"cases_completed":6,"model_calls":12,
      "actions_executed":12,"forbidden_actions_denied":7,
      "boundary_checks_passed":22,"boundary_checks_total":22,
      "check_names":sorted(checks["checks"]),
      "container_and_socket_removed":True,
      "manifest_sha256":report["manifest_sha256"],
      "attack_plan_sha256":report["attack_plan_sha256"],
      "raw_report_sha256":digest("artifacts/vultr-byoa-containment-phase12-20261106/report.json"),
      "source":"PROJECT_OWNED_HOST_OBSERVED_ARCHIVE",
      "archive":"/contained-sample/proof.json",
      "limitation":"November 6 archive, separate from November 7 on-demand fresh worker. Neither executes a customer's submitted agent.",
    }

def compile_proof():
    before,after,same=pair("same_before","same_after")
    t0,t1,term=pair("term_before","term_after")
    p0,p1,framework=pair("framework_before","framework_after")
    require((before["breached"],after["breached"])==(3,0),"SAME_AGENT_3_TO_0")
    require((term_success(t0),term_success(t1))==(0,6),"TERMPROOF_0_TO_6")
    require((t0["breached"],t1["breached"])==(0,0),"TERMPROOF_NO_RULE_VIOLATIONS")
    term["task_outcomes"]=[{"id":a["case_id"],"before":a["agent_answer"].splitlines()[0].removeprefix("milestoneVerdict: ").strip(),"after":b["agent_answer"].splitlines()[0].removeprefix("milestoneVerdict: ").strip()}
       for a,b in zip(t0["results"],t1["results"])]
    require((p0["breached"],p1["breached"])==(0,0),"FRAMEWORK_0_TO_0")
    config=read("artifacts/phase23-same-agent-real-policy-20261107/summary.json")
    require(config["result"]=="PASS" and config["same_python_module"]=="examples.vultr_vulnerable_agent:respond","SAME_AGENT_CALLABLE")
    require(config["same_inference_model"]=="glm-5.3" and config["same_exposed_tool_signatures"] is True,"SAME_AGENT_MODEL_TOOLS")
    require(config["vulnerable_manifest_sha256"]==before["manifest_sha256"] and config["hardened_manifest_sha256"]==after["manifest_sha256"],"SAME_AGENT_MANIFESTS")
    published_frame=read("web/public/third-party-pydantic/proof.json")
    require(published_frame["baseline_report_manifest"]==p0["manifest_sha256"] and published_frame["retest_report_manifest"]==p1["manifest_sha256"],"FRAMEWORK_MANIFESTS")
    regression=read("artifacts/phase23_isolated_full_regression/verified-summary.json")
    require(regression["passed_test_cases"]==240 and regression["skipped_test_cases"]==3 and regression["failed_test_modules"]==[],"REGRESSION")
    return {
      "schema":"blastlab.phase24.proof-index.v1",
      "created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
      "status":"FOUR_TECHNICAL_PROOFS_VERIFIED",
      "source_contract":"Sanitized metadata from full privately retained reports; hashes prove consistency, not third-party operator identity.",
      "claims":{
       "same_agent":{
        "title":"Same agent: real security mitigation",
        "metric":"3 to 0","before":3,"after":0,
        "metric_type":"observed forbidden-rule violations (six exact attack cases)",
        "model":"Vultr GLM-5.3",
        "ownership":"PROJECT_OWNED",
        "change":"Only system trust policy changed; same callable, task and tool signatures.",
        "scope":"A controlled real-model test, not external customer adoption or harmful tool execution.",
        "evidence":same,
       },
       "termproof":{
        "title":"Preexisting agent: legitimate task recovery",
        "metric":"0 to 6","before":0,"after":6,
        "metric_type":"TermProof deterministic VERIFIED outcomes across six cases",
        "model":"Gemini 2.5 Flash (reported by TermProof)",
        "ownership":"FOUNDER_OPERATED_PREEXISTING_CODEBASE",
        "repository":"https://github.com/ShalyX/termproof",
        "change":"Corrected BlastLab connector untrusted-input placement; TermProof security policy and model unchanged.",
        "scope":"This is integration repair, NOT a TermProof model security patch or independent outside-customer validation.",
        "evidence":term,
       },
       "contained":{
        "title":"Vultr worker: contained execution",
        "metric":"22 / 22","metric_type":"host-observed independent boundary/evidence checks",
        "ownership":"PROJECT_OWNED_WORKER",
        "scope":"Actual first-party Docker worker; not a customer agent sandbox.",
        "evidence":contained(),
       },
       "framework":{
        "title":"Third-party runtime compatibility",
        "metric":"0 to 0","before":0,"after":0,
        "metric_type":"observed violations under PydanticAI exact replay",
        "model":"Vultr GLM-5.3",
        "ownership":"PROJECT_OPERATED_PYDANTICAI",
        "scope":"Framework compatibility only, not customer adoption and NOT a security improvement.",
        "evidence":framework,
       },
      },
      "regression":{"executed":240,"skipped":3,"failed":0,
        "method":"16 separate Python test-module processes on Windows, original assertions unchanged",
        "caveat":"Monolithic Windows run had intermittent local connection-aborted errors; not claimed green."},
      "proof_debts":[
        "Independent non-founder agent owner/operator acceptance: not obtained.",
        "External tool execution is runner-reported; no independent attestation of hidden side effects.",
        "SHA-256 report/event manifests are unsigned; they do not prove operator identity.",
        "No universal task-correctness guarantee from literal answer markers.",
        "Contained worker is project-owned and does not run customer-submitted code.",
        "Account-wide authenticated history/purge, full Chamber inventory and formal accessibility audit are not delivered.",
      ],
      "links":{"app":"/app","contained":"/contained-sample",
       "framework_proof":"/third-party-pydantic/proof.json",
       "contained_archive":"/contained-sample/proof.json"},
    }

def export(proof):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    PRIVATE.mkdir(parents=True,exist_ok=True)
    blob=json.dumps(proof,indent=2,ensure_ascii=False,sort_keys=True)+"\n"
    low=blob.lower()
    for word in ["recovery_key","join_token","api_key","private_key","-----begin","password="]:
        require(word not in low,"SENSITIVE_PUBLIC_DATA_"+word)
    OUT.write_text(blob,encoding="utf8")
    (PRIVATE/"verified-index.json").write_text(blob,encoding="utf8")
    rows=[]
    for name,entry in proof["claims"].items():
        ev=entry["evidence"]
        if name=="contained":
            plan=ev["attack_plan_sha256"]; manifest=ev["manifest_sha256"]
        else:
            plan=ev["before"]["attack_plan_sha256"];manifest=ev["after"]["report_manifest_sha256"]
        rows.append("| "+entry["title"]+" | "+entry["metric"]+" | "+plan+" | "+manifest+" | "+entry["ownership"]+" |")
    register=ROOT/"PHASE24_PROOF_REGISTER.md"
    md="# Phase 24 — BlastLab Proof Engine verified evidence register\n\n"
    md+="Verified directly against locally retained raw reports via agent_lab.verify_report and verify_import. This is **not** independent customer attestation.\n\n"
    md+="| Evidence lane | Measurement | Attack plan SHA-256 | Final report manifest | Source provenance |\n|---|---|---|---|---|\n"
    md+="\n".join(rows)+"\n\n"
    md+="## Reproduction\n\nRun from a checkout with private local artifacts available:\n\n"
    md+="    python -m deploy.phase24_compile_proof\n    python -m unittest -q test_phase24_proof_engine\n\n"
    md+="The public file at /proof/evidence.json contains only derived metrics, exact six-case verdicts and digest anchors, not the raw prompts/recovery receipts.\n"
    md+="Without privately held full reports, the public index alone cannot reproduce event-chain verification. To verify privately, run the compiler against the retained raw source files.\n\n"
    md+="## Strict limits and remaining Phase 24 proof obligations\n\n"
    md+="\n".join("- "+x for x in proof["proof_debts"])+"\n\n"
    md+="Phase 24 remains OPEN until independent external operator proof and any necessary source-attribution improvements are documented. Do not claim runner-reported hidden actions are sandbox-observed.\n"
    register.write_text(md,encoding="utf8")
    print("PHASE24_PROOF_INDEX_VALIDATED",json.dumps({
      "lanes":{k:v["metric"] for k,v in proof["claims"].items()},
      "regression":240,"public_json_sha256":hashlib.sha256(OUT.read_bytes()).hexdigest(),
      "public_file":str(OUT)},ensure_ascii=False),flush=True)

if __name__=="__main__":
    export(compile_proof())
