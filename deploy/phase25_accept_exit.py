"""Record Phase25 exit only after actual hostile UI and full backend proof.

Do not touch Phase24's deferred independent external operator requirement.
"""
from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
report=root/"artifacts/phase25-redteam-regression/summary.json"
audit=root/"PHASE25_RED_TEAM_EXIT.md"
state_path=root/".hackathon/state.json"
gate_path=root/".hackathon/phase_gate.json"
summary=json.loads(report.read_text(encoding="utf8"))
assert summary["modules"]==20,summary
assert summary["tests"]==295,summary
assert summary["skipped"]==3,summary
assert summary["failures"]==[],summary
assert summary["method"]=="Every test module executed in a separate process, no test assertions mocked or bypassed"
for file in [
 "web/qa-phase25-redteam.cjs","web/qa-phase25-public.cjs",
 "web/qa-phase25-public/hostile-report-1440.png",
 "web/qa-phase25-public/hostile-report-390.png",
 "web/src/agent-lab.css",
 "deploy/phase25_policy_publish.py",
 "deploy/phase25_hostile_ui_publish.py",
]:
 assert (root/file).is_file(),file
txt=audit.read_text(encoding="utf8")
assert "FINAL RESULT TO BE INSERTED" not in txt
assert "pending final run summary at the time this audit draft was created" in txt
txt=txt.replace(
 "Full original regression plus added Phase25 tests: pending final run summary at the time this audit draft was created.",
 "Full original regression plus added Phase25 tests: **295 executable tests passed, 3 skipped, zero failures** across 20 runnable modules, each in an isolated Python process. Original test assertions unchanged."
)
txt=txt.replace(
 "Exit criterion: complete full backend regression and production browser verification before recording Phase25 PASS. Product Hygiene is Phase26 and must remain a separate independent Operator gate.",
 "Exit decision: **PHASE25 RED_TEAM PASS**, with two verified production repairs and scoped external-runner limitations. Advance only to the adjacent Phase26 PRODUCT_HYGIENE; subsequent phase gates remain independent."
)
txt+="""

## Final signed-off engineering acceptance — 2026-11-07

- Full isolated Python regression: 295 executed test cases, 3 documented skips, zero failed modules; the 2 zero-test support fixtures are excluded. Source summary: PHASE25_REGRESSION_SUMMARY.json.
- Separate hostile browser QA: 1440 and 390 passed against **locally built** UI and **live production-served** UI, with zero execution, external traffic or horizontal overflow. Screenshots were retained locally for operator inspection; malicious samples are synthetic.
- Prior original Phase24 production proof page retained intact with unchanged evidence SHA-256 after the CSS release.
- Two confirmed Red Team defects were fixed, and the production service/UI checks passed. No open reproducible high-severity vulnerability was observed within this **bounded** attack matrix.
- Limitations remain: external owner-run actions are runner reported; no source-signed attestation; independent outside developer not verified; no promise of universal attack coverage or large-scale multi-process DDoS protection.
- RED_TEAM PASS means reviewed scoped security surfaces are fit to enter Product Hygiene. It is not production penetration-test certification or submission approval.
"""
audit.write_text(txt,encoding="utf8")
sanitized={
 "schema":"blastlab.phase25.red-team-exit.v1",
 "date":"2026-11-07",
 "status":"PASS",
 "tests_executed":summary["tests"],
 "tests_skipped":summary["skipped"],
 "test_modules":summary["modules"],
 "test_failures":summary["failures"],
 "test_execution_method":summary["method"],
 "confirmed_issues":[
  {"id":"R25-01","summary":"malformed JSON tool-policy member raised uncaught TypeError","status":"FIXED_PRODUCTION","verification":"live invalid policy HTTP 400 after service restart"},
  {"id":"R25-02","summary":"long hostile runner text broke report layout","status":"FIXED_PRODUCTION","verification":"live desktop/mobile Chrome hostile payloads escaped, no overflow/errors/external traffic"}
 ],
 "browser_qa":{"local":{"1440":"PASS","390":"PASS"},"production_served":{"1440":"PASS","390":"PASS"},"outbound_attack_requests":0,"script_executed":False},
 "attestation_limit":"External agent behavior is runner-reported and unsigned; no independently authenticated customer execution.",
 "independent_outside_developer_status":"OPEN_DEFERRED_UNTIL_BEFORE_SUBMISSION_AUDIT",
 "proof":"PHASE25_RED_TEAM_EXIT.md",
}
(root/"PHASE25_REGRESSION_SUMMARY.json").write_text(json.dumps(sanitized,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
ledger=json.loads(gate_path.read_text(encoding="utf-8-sig"))
state=json.loads(state_path.read_text(encoding="utf-8-sig"))
assert state["phase"]=="RED_TEAM",state["phase"]
assert ledger["exit_proofs"]["RED_TEAM"]["status"]=="OPEN"
assert ledger["exit_proofs"]["PROOF_ENGINE"]["status"]=="CONDITIONAL_DEFERRED"
assert ledger["deferred_requirements"]["independent_outside_operator"]["status"]=="OPEN"
assert len(ledger["locked_p0"])==12 and all(v=="VERIFIED" for v in ledger["locked_p0"].values())
proof=[
 "PHASE25_RED_TEAM_EXIT.md",
 "PHASE25_REGRESSION_SUMMARY.json",
 "PHASE25_RED_TEAM_AUDIT.md",
 "test_phase25_redteam.py",
 "test_phase25_redteam_completion.py",
 "web/qa-phase25-redteam.cjs",
 "web/qa-phase25-public.cjs",
 "deploy/phase25_policy_install.sh",
 "deploy/phase25_hostile_ui_install.sh",
]
assert all((root/f).is_file() for f in proof),proof
ledger["exit_proofs"]["RED_TEAM"]={
 "status":"PASS",
 "proof":proof,
 "reason":"Two reproduced flaws fixed in live Vultr production; 295 executable unit tests PASS, 3 skipped, zero failed; malformed HTTP, concurrent quota, cross-session auth, recovery, forged reports and adapter metadata tested; real production-served hostile UI Chrome checks PASS at 1440/390. Runner-reported behavior and outside operator explicitly unproven, remain documented as separate debts."
}
ledger["exit_proofs"].setdefault("PRODUCT_HYGIENE",{
 "status":"OPEN","proof":[],"reason":"Phase26 has not yet completed its separate end-to-end Product Hygiene audit."
})
gate_path.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
state.setdefault("phase_integrity",{})["phase25_red_team"]="PASS - 295 executable tests; 3 skips; production policy crash and hostile overflow repaired; live Chrome QA 2 viewports"
state["next_action"]="Advance adjacent gate to PRODUCT_HYGIENE (Phase26); run dedicated end-to-end Product Hygiene, accessibility and real user-journey audit. Independent outside operator remains OPEN, mandatory before Submission Audit."
state_path.write_text(json.dumps(state,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
print("PHASE25_RED_TEAM_EXIT_RECORDED",json.dumps({"status":"PASS","tests":295,"skipped":3,"next":"PRODUCT_HYGIENE","external_dev":"OPEN"},ensure_ascii=False))
