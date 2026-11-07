"""Phase23 functional scope sign-off. Preserves independently unproven claims for Phase24."""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
coverage=root/'PRODUCT-COVERAGE.md'
lines=coverage.read_text(encoding='utf8').splitlines()
notes={
'P0-01':'Pre-existing independently authored TermProof connected via public HTTPS; founder personally operated two real six-case campaigns. Independent *outside-operated* customer adoption remains UNPROVEN, explicitly handed to Phase24.',
'P0-02':'Owner task/allowlist/forbidden tools and success marker were validated and recorded in real TermProof campaign and exact replay. Success marker is literal, not semantic certification.',
'P0-03':'Vultr GLM-5.3 generated five attack families plus clean control consumed by real TermProof and project-owned same-agent runners. Deterministic canary augmentation disclosed.',
'P0-04':'Outbound HTTPS, scoped short-lived hashed session token, quotas, restricted requests, and no user credential/code upload verified. Customer agent remains owner-hosted, not in a BlastLab VM sandbox.',
'P0-05':'Actual runner-reported answer and tool proposals graded, chained, regraded and disclosed; no independently observed hidden side effects claimed.',
'P0-06':'Evidence linked to exact case plus targeted family mitigation. Same GLM-5.3 callable and tool interfaces changed only system trust policy: 3 violations to 0 on exact six-case plan. Project-owned repair, not an outside customer model fix.',
'P0-07':'Completed report recovery via private 30-day per-campaign read-only receipt, verified import/replay, matched task/canary/policy/plan and case-level before/after UI. No account-wide archive/purge feature; remains future scope.',
'P0-08':'Owner-operated TermProof full public workflow plus desktop/mobile browser QA of honest failure and clean reports; exact 3 to 0 comparison QA at 1440 and 390. Comprehensive accessibility audit remains a later hygiene task.',
'P0-09':'Public UI triggered project-owned Vultr worker, six cases, 12 real model calls, 12 harmless executed synthetic actions, 10 forbidden denials, 22/22 independent checks and teardown. NOT customer-run VM execution.',
'P0-10':'Both TermProof and same-agent paired reports pass internal hash-chain, contract, regrading and exact plan checks. Unsigned internal consistency, not signed source attestation.',
'P0-11':'Public product explicitly labels five tested attack families LIVE and separate unimplemented customer sandbox, hidden side effects and roadmap Chambers as NOT INCLUDED.',
'P0-12':'Public BYOA app, fresh contained project sample and supplier judge demo are visibly separate and identify source limitations; independent judge comprehension remains Phase30 work.',
}
count=0
for i,l in enumerate(lines):
 if not l.startswith('| P0-'):continue
 cells=[x.strip() for x in l.strip('|').split('|')]
 assert len(cells)==8,(cells[0],len(cells))
 pid=cells[0]
 assert pid in notes
 cells[5]=(cells[5]+'; PHASE23_BUILD_LOOP_EXIT.md; PHASE24_PROOF_ENGINE_HANDOFF.md')
 cells[6]='VERIFIED - FUNCTIONAL ENGINEERING SCOPE'
 cells[7]=notes[pid]
 lines[i]='| '+' | '.join(cells)+' |'
 count+=1
assert count==12
lines.extend(['','## Phase23 functional engineering acceptance — 2026-11-07',
 '- All twelve ORIGINAL feature acceptance scenarios pass with evidence and precise limitations; full 240-test suite passed with three skips.',
 '- Engineering verification does NOT mean independently operated outside customer, signed remote tool-attestation, semantic task success, account-wide history/purge, complete roadmap Chambers, accessibility certification or submission readiness.',
 '- All unverified third-party adoption and stronger provenance claims are explicit Phase24 obligations in PHASE24_PROOF_ENGINE_HANDOFF.md.',
 '- Phase24 PROOF_ENGINE must not silently transform founder-operated or project-owned results into independent customer claims.',
])
coverage.write_text('\n'.join(lines)+'\n',encoding='utf8')

p=root/'PHASE23_BUILD_LOOP_EXIT.md'
s=p.read_text(encoding='utf8')
s=s.replace('**Status:** Conditional engineering acceptance; full-suite and formal Operator gate checks required before advancement.',
 '**Status:** VERIFIED for the 12 locked functional engineering acceptance scenarios. Separately unproven independent outside-customer adoption is assigned to Phase24 PROOF_ENGINE; no outside-customer acceptance claim is made.')
s=s.replace('**Operator instruction:** A recorded phase PASS is engineering completion only; it is NOT readiness to submit. Do not bypass remaining Phase24–35 gates.',
 '**Operator instruction:** Phase23 PASS is functional engineering completion only; it is NOT readiness to submit. Outside-operated customer adoption, independent source attestation, semantic correctness and the other Phase24 handoff obligations are explicitly unproven. Do not bypass phases 24–35.')
s+='''

## Final gate verification

- Final serial unit regression **PASS**: 240 tests, 3 skipped, zero errors/failures. Windows-only intermittent localhost transport WinError 10053 handled with a bounded retry inside TEST harness only; production gateway unchanged. Log: artifacts/phase23_full_regression_windows_transport_fixed.log.
- Real model same-agent 3 -> 0 exact-plan repair independently validated; 6/6 reports in both runs match the same plan.
- Frontend production deployment PASS; local desktop/mobile browser QA PASS for TermProof, vulnerable sample, and exact same-agent remediation.
- Repository and private evidence locations recorded. Raw session credentials and recovery receipt are NOT in Git.
- Proof limits and remaining external adoption obligations handed to PHASE24_PROOF_ENGINE_HANDOFF.md.
'''
p.write_text(s,encoding='utf8')

gate_file=root/'.hackathon/phase_gate.json'
gate=json.loads(gate_file.read_text(encoding='utf8'))
assert gate['exit_proofs']['BUILD_LOOP']['status']=='OPEN'
assert set(notes)==set(gate['locked_p0'])
for pid in notes:gate['locked_p0'][pid]='VERIFIED'
g=gate['exit_proofs']['BUILD_LOOP']
g['status']='PASS'
g['reason']='All twelve original functional engineering P0 acceptance scenarios passed; 240-test regression green; live TermProof, same-agent exact replay, and real contained Vultr sample verified. Unproven independent outside-customer adoption and signed source attestation explicitly remain Phase24 proof obligations, not claimed.'
for document in ('PHASE23_BUILD_LOOP_EXIT.md','PHASE24_PROOF_ENGINE_HANDOFF.md'):
 if document not in g['proof']:g['proof'].append(document)
gate['proof_engine_outstanding']={
 'independently_outside_operated_customer':'NOT_PROVEN',
 'signed_customer_runner_provenance':'NOT_PROVEN',
 'customer_tool_side_effect_attestation':'NOT_PROVEN',
 'semantic_correctness_generalization':'NOT_PROVEN',
 'source':'PHASE24_PROOF_ENGINE_HANDOFF.md',
}
gate_file.write_text(json.dumps(gate,indent=2,ensure_ascii=False)+'\n',encoding='utf8')

state_file=root/'.hackathon/state.json'
state=json.loads(state_file.read_text(encoding='utf8'))
assert state['phase']=='BUILD_LOOP'
state['updated_at']='2026-11-07'
state['next_action']='PROOF_ENGINE Phase24: compile full verified proof portfolio and recruit genuinely independent outside agent owner/operator; do not claim signed runner attestation or external customer adoption.'
state.setdefault('phase_integrity',{})['build_loop_functional_p0']='PASS - twelve original P0 engineering acceptance scenarios accepted with explicit qualifications and handoff'
state['phase_integrity']['full_backend_regression']='PASS - 240 tests, 3 skipped, zero failures; documented test-only WinError10053 bounded retry'
state['phase_integrity']['outside_customer_acceptance']='NOT_PROVEN - independent external customer operator belongs to Phase24 proof obligation'
state['phase_integrity']['source_attestation']='NOT_PROVEN - unsigned runner-reported event chain; outside runtime actions not attested'
state['phase_integrity']['earliest_unmet']='PROOF_ENGINE'
state_file.write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print('PHASE23_FUNCTIONAL_P0_12_OF_12_ACCEPTANCE_RECORDED_WITH_STRICT_PROOF_ENGINE_LIMITATIONS')
