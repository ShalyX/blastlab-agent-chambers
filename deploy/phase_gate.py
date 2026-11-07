"""Hackathon Operator phase gate. Prevents accidental skipping and fake completion.

Gate evidence is kept in .hackathon/phase_gate.json. This is an auditable
process guard, not a substitute for an independent examination of the proof.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ORDER = (
    "INTAKE", "RUBRIC_DECODE", "RESEARCH", "IDEATION", "HUMAN_IDEA_GATE",
    "VALIDATION", "PRODUCT_LOCK", "NAME_LOCK", "DEMO_ARCHITECTURE", "EVIDENCE_PLAN",
    "DEPENDENCY_ATTACK", "TECHNICAL_DERISK", "BUILD_VERTICAL_SLICE", "PRODUCT_REVIEW",
    "BRAND_KIT", "ART_DIRECTION", "REFERENCE_BOARD", "VISUAL_ASSET_STRATEGY",
    "MOTION_STORYBOARD", "DESIGN_LOCK", "DESIGN_ENGINEERING", "VISUAL_QA", "BUILD_LOOP",
    "PROOF_ENGINE", "RED_TEAM", "PRODUCT_HYGIENE", "DEMO_PRODUCTION", "DEMO_QA",
    "PITCH", "JUDGE_SIMULATION", "PRIORITIZED_FIXES", "FEATURE_FREEZE",
    "SUBMISSION_AUDIT", "READY_TO_SUBMIT", "SUBMITTED"
)
ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".hackathon" / "state.json"
LEDGER = ROOT / ".hackathon" / "phase_gate.json"


def stage_index(name):
    if name not in ORDER:
        raise ValueError("Unknown Operator phase: " + str(name))
    return ORDER.index(name)


def check_transition(state, ledger, target):
    current = state.get("phase")
    if not isinstance(current, str):
        raise ValueError("Current phase missing")
    at = stage_index(current)
    if at == len(ORDER) - 1:
        raise ValueError("Already at final phase")
    if ORDER[at + 1] != target:
        raise ValueError("PHASE_SKIP_DENIED: expected " + ORDER[at + 1] + " after " + current)

    approval = ledger.get("exit_proofs", {}).get(current, {})
    status = approval.get("status")
    validation_modify = (
        current == "VALIDATION"
        and status == "MODIFY"
        and approval.get("thesis_unchanged") is True
        and approval.get("modifications_recorded") is True
    )
    # A specific, human-approved deferral may advance ONLY Proof Engine ->
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

    evidence = approval.get("proof", [])
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("NO_EXIT_PROOF for " + current)
    for ref in evidence:
        if not isinstance(ref, str) or not ref or not (ROOT / ref).is_file():
            raise ValueError("MISSING_EXIT_ARTIFACT " + str(ref))

    if target in ORDER[stage_index("PROOF_ENGINE"):]:
        p0 = ledger.get("locked_p0", ledger.get("v3_locked_p0", {}))
        ids = ["P0-" + str(n).zfill(2) for n in range(1, 13)]
        unverified = [ident for ident in ids if p0.get(ident) != "VERIFIED"]
        if unverified:
            raise ValueError("FULL_PRODUCT_BLOCKED: " + ",".join(unverified))
    if target in ORDER[stage_index("SUBMISSION_AUDIT"):]:
        # Phase24 owner-approved deferral is a sequencing decision only:
        # independent outside-operator proof is still a hard submission gate.
        deferred = ledger.get("deferred_requirements", {}).get("independent_outside_operator")
        if deferred is not None:
            # A deferral note is NOT independent customer evidence. Require a
            # separately authored acceptance audit, operator attribution and
            # six-case report manifest before treating the proof debt as met.
            proofs = deferred.get("proof")
            if (deferred.get("status") != "VERIFIED"
                or not isinstance(proofs, list)
                or "PHASE24_EXTERNAL_OPERATOR_ACCEPTANCE.md" not in proofs
                or not deferred.get("outside_operator_reference")
                or not deferred.get("agent_source_reference")
                or not deferred.get("six_case_report_manifest_sha256")
                or deferred.get("consent_to_cite") is not True):
                raise ValueError("DEFERRED_OUTSIDE_OPERATOR_PROOF_NOT_COMPLETE")
            for ref in proofs:
                if not isinstance(ref, str) or not (ROOT / ref).is_file():
                    raise ValueError("MISSING_EXTERNAL_OPERATOR_PROOF " + str(ref))
        if ledger.get("judge_simulation_v3") != "PASS":
            raise ValueError("JUDGE_SIMULATION_NOT_PASSED")
    return target


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("check", "advance"))
    parser.add_argument("--to", default=None)
    args = parser.parse_args()
    state = json.loads(STATE.read_text(encoding="utf-8-sig"))
    ledger = json.loads(LEDGER.read_text(encoding="utf-8-sig"))
    current = state.get("phase")
    next_stage = ORDER[stage_index(current) + 1] if current != "SUBMITTED" else None
    print("PHASE", current, "EXPECTED_NEXT", next_stage)
    try:
        selected = args.to or next_stage
        check_transition(state, ledger, selected)
    except ValueError as exc:
        print("GATE_BLOCKED", str(exc))
        raise SystemExit(2)
    if args.action == "advance":
        state["phase"] = selected
        STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("ADVANCED", selected)
    else:
        print("GATE_READY", selected)


if __name__ == "__main__":
    main()
