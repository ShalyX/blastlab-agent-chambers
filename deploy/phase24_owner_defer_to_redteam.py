"""One-time, explicit owner-approved Phase24 independent developer deferral.
Never reports that independent customer testing occurred.
"""
from pathlib import Path
import json
from datetime import datetime,timezone

root=Path(__file__).resolve().parents[1]
gate=root/"deploy/phase_gate.py"
s=gate.read_text(encoding="utf8")
anchor='''    if status != "PASS" and not validation_modify:
        raise ValueError("UNMET_GATE: " + current + " has no verified PASS or eligible Validation MODIFY")
'''
replace='''    # A specific, human-approved deferral may advance ONLY Proof Engine ->
    # Red Team. It is never accepted as a proof PASS and must be discharged
    # before Submission Audit. Other phase skips/deferrals remain blocked.
    proof_deferred = (
        current == "PROOF_ENGINE"
        and target == "RED_TEAM"
        and status == "CONDITIONAL_DEFERRED"
        and approval.get("owner_approved") is True
        and approval.get("deferred_proof_id") == "independent_outside_operator"
        and approval.get("completion_requirement") == "before_submission_audit"
        and ledger.get("deferred_requirements", {}).get("independent_outside_operator", {}).get("status") == "OPEN"
    )
    if status != "PASS" and not validation_modify and not proof_deferred:
        raise ValueError("UNMET_GATE: " + current + " has no verified PASS or eligible documented deferral")
'''
assert s.count(anchor)==1,"cannot locate gate check"
s=s.replace(anchor,replace,1)
anchor='''    if target in ORDER[stage_index("SUBMISSION_AUDIT"):]:
        if ledger.get("judge_simulation_v3") != "PASS":
            raise ValueError("JUDGE_SIMULATION_NOT_PASSED")
'''
replace='''    if target in ORDER[stage_index("SUBMISSION_AUDIT"):]:
        # Phase24 owner-approved deferral is a sequencing decision only:
        # independent outside-operator proof is still a hard submission gate.
        deferred = ledger.get("deferred_requirements", {}).get("independent_outside_operator")
        if deferred is not None:
            if deferred.get("status") != "VERIFIED" or not deferred.get("proof"):
                raise ValueError("DEFERRED_OUTSIDE_OPERATOR_PROOF_NOT_COMPLETE")
            for ref in deferred["proof"]:
                if not isinstance(ref, str) or not (ROOT / ref).is_file():
                    raise ValueError("MISSING_EXTERNAL_OPERATOR_PROOF " + str(ref))
        if ledger.get("judge_simulation_v3") != "PASS":
            raise ValueError("JUDGE_SIMULATION_NOT_PASSED")
'''
assert s.count(anchor)==1
s=s.replace(anchor,replace,1)
# Fix existing main action implementation's literal "\\n" when serializing
s=s.replace('STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\\\\n", encoding="utf-8")',
            'STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")')
gate.write_text(s,encoding="utf8")

defer_doc=root/"PHASE24_OWNER_DEFERRAL.md"
defer_doc.write_text("""# Owner-directed Phase 24 deferral / Phase 25 sequence authorization

Date: 2026-11-07 (Africa/Lagos)
User instruction: "Move to next phase, we'd find exter dev later"

## Approved decision

The founder explicitly approves proceeding to RED_TEAM (Phase 25) while
temporarily deferring the requirement for a genuinely independent outside
developer to operate a preexisting agent through BlastLab.

The action is a sequencing choice only. It does NOT assert that the deferred
independent developer has been recruited, authenticated, tested, or approved.

Phase 24's four technical proof lanes were independently regraded and published:
- Same project-owned Vultr agent, exact six-case trust-policy repair: 3 -> 0
  observed violations.
- Founder-operated preexisting TermProof: 0 -> 6 deterministic legitimate-task
  verifications after correcting BlastLab's input boundary.
- First-party contained Vultr worker: 22/22 independently checked host evidence.
- Project-operated PydanticAI framework: 0 -> 0 violations, interoperability only.

Full raw reports remain privately held. The public proof index consists of
unsigned SHA-256 consistency anchors and safe metadata. The proof page and
offline verification bundle passed production and tamper-negative tests.

## Non-negotiable deferred requirement

A genuinely non-founder developer must personally operate their real agent,
grant attribution consent, provide an independently checkable agent source
reference, run all six real cases through the public connector, retain source
provenance and the report manifest, and provide a reproducible retest if
a genuine finding is found. Founder's TermProof is NOT a substitute.

The deferred requirement remains OPEN, must be recorded in all future
operator audits, and **must be satisfied before Submission Audit (Phase 33)**.
The gate enforces this condition. Red Team may begin without it.

Other proof limitations also remain OPEN or explicitly scoped:
external runner tool actions are runner-reported, not independent runtime
attestations; no signed external agent identity, no universal task-success
guarantee, no broad Chamber coverage or full account-wide history.

Status: PROOF_ENGINE = CONDITIONAL_DEFERRED (not PASS).
Next phase: RED_TEAM.
Scope: one exact adjacent transition, not a general bypass of Operator gates.
""",encoding="utf8")

ledger_path=root/".hackathon/phase_gate.json"
state_path=root/".hackathon/state.json"
ledger=json.loads(ledger_path.read_text(encoding="utf-8-sig"))
state=json.loads(state_path.read_text(encoding="utf-8-sig"))
assert state.get("phase")=="PROOF_ENGINE"
entry=ledger["exit_proofs"]["PROOF_ENGINE"]
assert entry["status"]=="OPEN"
assert ledger["exit_proofs"]["BUILD_LOOP"]["status"]=="PASS"
assert all(v=="VERIFIED" for v in ledger.get("locked_p0",{}).values()) and len(ledger["locked_p0"])==12
entry.update({
 "status":"CONDITIONAL_DEFERRED",
 "owner_approved":True,
 "approved_at":"2026-11-07",
 "deferred_proof_id":"independent_outside_operator",
 "completion_requirement":"before_submission_audit",
 "reason":"Owner explicitly requested progression to Red Team and to find an outside developer later. Four technical evidence lanes were verified; independent non-founder operator not yet recruited or accepted. This is NOT a Proof Engine PASS.",
})
entry.setdefault("proof",[])
if "PHASE24_OWNER_DEFERRAL.md" not in entry["proof"]:entry["proof"].append("PHASE24_OWNER_DEFERRAL.md")
ledger["deferred_requirements"]={
 "independent_outside_operator":{
  "status":"OPEN",
  "proof":[],
  "required_before":"SUBMISSION_AUDIT",
  "source_phase":"PROOF_ENGINE",
  "reason":"Owner-approved sequencing deferral; outside-owned/operated six-case agent acceptance still unproven."
 }}
ledger_path.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
state.setdefault("phase_integrity",{})["independent_outside_agent"]="DEFERRED_BY_OWNER_TO_BE_DONE_BEFORE_SUBMISSION_AUDIT_NOT_VERIFIED"
state["phase_integrity"]["phase24_status"]="CONDITIONAL_DEFERRED_NOT_PASS"
state["next_action"]="Advance one adjacent stage to RED_TEAM Phase25. Keep genuine outside operator proof OPEN and mandatory before Submission Audit."
state_path.write_text(json.dumps(state,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
print("PHASE24_EXPLICIT_OWNER_DEFERRAL_RECORDED",entry["status"],"REQUIREMENT_OPEN",ledger["deferred_requirements"]["independent_outside_operator"]["status"])
