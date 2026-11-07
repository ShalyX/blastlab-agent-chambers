# PRODUCT COVERAGE — BlastLab v4
**Lock revision:** 4
**Snapshot:** 2026-11-06
**Rule:** statuses describe implementation evidence, not product aspiration. No row is VERIFIED until its integrated acceptance scenario passes.

| ID | Capability / user value | Workflow surface | Implementation | Acceptance scenario | Evidence | Status | Gap |
|---|---|---|---|---|---|---|---|
| P0-01 | Bring/connect own agent | Connect / runner | web/src/AgentLabExperience.tsx; web/public/connect/blastlab_connector.py; agent_lab_service.py; control_api.py | Independently authored agent connects over HTTPS, receives all cases and returns real outputs | PHASE23_TERMPROOF_OWNER_ATTEMPT.md; web/run-termproof-owner-agent.cjs; web/prepare-termproof-exact-retest.cjs; artifacts/phase23-termproof-founder/ (private); web/public/connect/independent-tester.md; PHASE23_BUILD_LOOP_EXIT.md; PHASE24_PROOF_ENGINE_HANDOFF.md | VERIFIED - FUNCTIONAL ENGINEERING SCOPE | Pre-existing independently authored TermProof connected via public HTTPS; founder personally operated two real six-case campaigns. Independent *outside-operated* customer adoption remains UNPROVEN, explicitly handed to Phase24. |
| P0-02 | Define task, allowed/forbidden capabilities and success condition | Connect / configuration | web/src/AgentLabExperience.tsx; agent_lab.py:validate_request | Persisted policy contract is validated and used by campaign grading | test_agent_lab.py; PHASE23_BUILD_LOOP_EXIT.md; PHASE24_PROOF_ENGINE_HANDOFF.md | VERIFIED - FUNCTIONAL ENGINEERING SCOPE | Owner task/allowlist/forbidden tools and success marker were validated and recorded in real TermProof campaign and exact replay. Success marker is literal, not semantic certification. |
| P0-03 | Adaptive multi-attack campaign | Campaign | agent_lab_attacks.py; agent_lab_service.py; agent_lab.py | Vultr generates five distinct task-specific attack families plus a control; real connected agent responds to every case | artifacts/vultr-byoa-exact-retest-20261106/summary.json; test_agent_lab_attacks.py; PHASE23_BUILD_LOOP_EXIT.md; PHASE24_PROOF_ENGINE_HANDOFF.md | VERIFIED - FUNCTIONAL ENGINEERING SCOPE | Vultr GLM-5.3 generated five attack families plus clean control consumed by real TermProof and project-owned same-agent runners. Deterministic canary augmentation disclosed. |
| P0-04 | Safe bounded BYOA integration | Runner / execution boundary | web/public/connect/blastlab_connector.py; agent_lab.py; agent_lab_service.py; control_api.py | Pull-only HTTPS, short-lived token, bounded payload/session/rate limits, no arbitrary URL, no customer key upload, no unapproved tool execution | test_byoa_connector.py; test_agent_lab.py; PHASE23_BUILD_LOOP_EXIT.md; PHASE24_PROOF_ENGINE_HANDOFF.md | VERIFIED - FUNCTIONAL ENGINEERING SCOPE | Outbound HTTPS, scoped short-lived hashed session token, quotas, restricted requests, and no user credential/code upload verified. Customer agent remains owner-hosted, not in a BlastLab VM sandbox. |
| P0-05 | Evidence-based verdict against connected agent | Report / evaluation | agent_lab.py:grade_case, add_response, report | Exact response and tool events are graded against the declared task/policy; proposed, runner-reported executed, and sandbox-verified actions are distinct | test_agent_lab.py; test_agent_lab_attacks.py; PHASE23_BUILD_LOOP_EXIT.md; PHASE24_PROOF_ENGINE_HANDOFF.md | VERIFIED - FUNCTIONAL ENGINEERING SCOPE | Actual runner-reported answer and tool proposals graded, chained, regraded and disclosed; no independently observed hidden side effects claimed. |
| P0-06 | Evidence-linked remediation | Findings / mitigation | agent_lab.py:mitigation; web/src/AgentLabExperience.tsx | Every finding links to the exact case and evidence, provides a targeted fix, and the user's changed agent is retested | artifacts/vultr-byoa-exact-retest-20261106/; test_agent_retest.py; PHASE23_BUILD_LOOP_EXIT.md; PHASE24_PROOF_ENGINE_HANDOFF.md | VERIFIED - FUNCTIONAL ENGINEERING SCOPE | Evidence linked to exact case plus targeted family mitigation. Same GLM-5.3 callable and tool interfaces changed only system trust policy: 3 violations to 0 on exact six-case plan. Project-owned repair, not an outside customer model fix. |
| P0-07 | History, exact replay and before/after comparison | Report / archive / retest | agent_lab.py:replay_session, verify_import; agent_lab_service.py; web/src/AgentLabExperience.tsx | Completed report is retained; same task, policy, canary and plan replayed; case-level outcomes and lineage compared | PHASE23_RECOVERY.md; test_phase23_recovery.py; web/qa-phase23-recovery.cjs; web/qa-phase23-public.cjs; PHASE23_BUILD_LOOP_EXIT.md; PHASE24_PROOF_ENGINE_HANDOFF.md | VERIFIED - FUNCTIONAL ENGINEERING SCOPE | Completed report recovery via private 30-day per-campaign read-only receipt, verified import/replay, matched task/canary/policy/plan and case-level before/after UI. No account-wide archive/purge feature; remains future scope. |
| P0-08 | First-class BYOA workflow UI | Connect → Campaign → Report → Retest | web/src/AgentLabExperience.tsx; web/src/App.tsx; web/src/agent-lab.css | Real browser journey including loading, error, empty, auth, report import, replay, comparison and mobile states | frontend build; DEMO.md; web/qa-agent/; PHASE23_BUILD_LOOP_EXIT.md; PHASE24_PROOF_ENGINE_HANDOFF.md | VERIFIED - FUNCTIONAL ENGINEERING SCOPE | Owner-operated TermProof full public workflow plus desktop/mobile browser QA of honest failure and clean reports; exact 3 to 0 comparison QA at 1440 and 390. Comprehensive accessibility audit remains a later hygiene task. |
| P0-09 | Real Vultr integration and contained judge execution | Attack planner / VM / sandbox | experiments/byoa-containment/host_supervisor.py; contained_sample_service.py; control_api.py; web/src/ContainedSample.tsx; experiments/byoa-containment/verify_run.py | Independent project-owned sample worker passes actual Vultr inference / harmless tool execution / policy probes / teardown | PHASE23_FRESH_CONTAINED_RUN.md; web/qa-public-fresh-worker/completed-public-job.json; test_contained_sample_service.py; test_contained_sample_http.py; web/qa-public-fresh-readonly.cjs; PHASE23_BUILD_LOOP_EXIT.md; PHASE24_PROOF_ENGINE_HANDOFF.md | VERIFIED - FUNCTIONAL ENGINEERING SCOPE | Public UI triggered project-owned Vultr worker, six cases, 12 real model calls, 12 harmless executed synthetic actions, 10 forbidden denials, 22/22 independent checks and teardown. NOT customer-run VM execution. |
| P0-10 | Verifiable evidence and honest provenance | Export / verification | agent_lab.py:report, verify_report, _verify_report, verify_import | Manifest binds report fields to the event chain; verifier rejects tampered/regraded verdicts; provenance is visibly RUNNER-REPORTED unless independently attested | test_agent_retest.py; test_agent_lab_attacks.py; report manifests; PHASE23_BUILD_LOOP_EXIT.md; PHASE24_PROOF_ENGINE_HANDOFF.md | VERIFIED - FUNCTIONAL ENGINEERING SCOPE | Both TermProof and same-agent paired reports pass internal hash-chain, contract, regrading and exact plan checks. Unsigned internal consistency, not signed source attestation. |
| P0-11 | Honest attack-surface inventory | Product scope / Chamber map | PRODUCT.md; PRODUCT_DRIFT_AUDIT.md; web/src/AgentLabExperience.tsx | Only implemented surfaces are marked live; future Chamber territories are visible as planned/not implemented, never as working | PRODUCT_DRIFT_AUDIT.md; current UI disclosure; PHASE23_BUILD_LOOP_EXIT.md; PHASE24_PROOF_ENGINE_HANDOFF.md | VERIFIED - FUNCTIONAL ENGINEERING SCOPE | Public product explicitly labels five tested attack families LIVE and separate unimplemented customer sandbox, hidden side effects and roadmap Chambers as NOT INCLUDED. |
| P0-12 | Demo/sample separation from product | Connect / demo disclosure | web/src/AgentLabExperience.tsx; DEMO.md; PRODUCT.md | Supplier scenario and sample agents are labeled DEMO; their evidence is never attributed to a customer's own agent | web/src/ContainedSample.tsx; web/public/contained-sample/proof.json; web/public/third-party-pydantic/proof.json; public Chrome QA in PHASE23_INTEROP_AND_CONTAINMENT.md; PHASE23_BUILD_LOOP_EXIT.md; PHASE24_PROOF_ENGINE_HANDOFF.md | VERIFIED - FUNCTIONAL ENGINEERING SCOPE | Public BYOA app, fresh contained project sample and supplier judge demo are visibly separate and identify source limitations; independent judge comprehension remains Phase30 work. |

## P0 interpretation

- P0-11 is an integrity requirement to preserve honest scope and the proposed attack-surface roadmap. It does not silently require five complete Chambers for initial launch.
- P0-12 is a provenance/product-integrity requirement. It is not permission to substitute demo fixtures for BYOA.
- P0-09: contained sample-agent execution passed independent verification; public BYOA product routing and customer-agent acceptance are still open.

## P1 roadmap (not silently promoted to P0)

- REST and JavaScript adapters.
- Additional Chambers and broader attack surfaces.
- CI integration and scheduled regression.
- Team workspaces and durable report archive UX.
- Optional stronger runner attestation.
- Statistical trials and expanded standards mapping.

## Phase 13 evidence update ? 2026-11-06
- P0-01: Actual project-owned GLM-5.3 agent ran through public Python BYOA connector; no independently authored customer integration proven.
- P0-02: Task, allowed/forbidden tool policy and literal task-success signal now configurable, validated and bound to exact retest; semantic task correctness remains open.
- P0-03: Real Vultr-generated six-case campaign and observed model responses proved. Independent user-agent breadth remains open.
- P0-06: Same project-owned agent implementation was hardened via a real system policy change; observed violations reduced 3 to 0. Not an automatic customer-source patch.
- P0-07: Exact plan/canary/task/policy replay and server-verified lineage passed; durable multi-user history acceptance remains open.
- P0-08: Public /app Connect and reports built; prior desktop/mobile QA captures present. Repeat Chrome smoke in Product Review.
- P0-09: Phase 12 contained sample worker proven, but public BYOA runner is still outside that worker; production integration remains PARTIAL.
- P0-10: Independent VM report verification and server comparison passed internal consistency; source attestation still missing.
- Do not automatically promote all twelve P0s to VERIFIED from a passing vertical slice.

## Phase 23 recovery milestone ? 2026-11-07
- P0-07: production one-time recovery key, hashed at rest, 30-day read-only completed-report access passed. Expired runner token recovery proved locally; production live recovery and authorizations proved independently.
- P0-07 remains PARTIAL: the product has no account-based multi-session history, reissuable identity or data purge policy. Legacy sessions lacking new recovery keys cannot be restored through this feature.
- P0-01: public sample agent transport passes; independent customer-authored agent remains unproven.
- P0-09: previously verified disposable sample worker remains separate from the production customer runner; still PARTIAL.
- Do not mark overall BUILD_LOOP or PROOF_ENGINE PASS from the recovery slice alone.

## Phase 23 interoperability and contained proof integration - 2026-11-07
- Actual third-party PydanticAI Agent runtime, six public HTTPS baseline cases and six exact replay cases on Vultr GLM-5.3; measured 0 to 0 policy violations, not claimed remediation.
- Real Phase12 Vultr Docker worker record preserved, re-verified 22/22 and now accessible at /contained-sample with case-level host-observed evidence.
- Both evidence modes are distinct from independently authored customer adoption, which remains OPEN.
- P0-01, P0-09 and P0-12 remain PARTIAL; do not close BUILD_LOOP or advance to PROOF_ENGINE.

## Phase 23 fresh bounded worker - 2026-11-07
- P0-09 VERIFIED for first-party project-owned contained judge sample: actual public browser click -> fixed six-case Vultr worker -> 22/22 independent checks -> worker and socket removed. See PHASE23_FRESH_CONTAINED_RUN.md.
- P0-01 remains PARTIAL; independent real customer agent operation cannot be simulated by BlastLab. Tester protocol published at /connect/independent-tester.md.
- No customer-run arbitrary code ever passes into the Vultr container: the worker is a fixed, quota-limited demonstration only.
- BUILD_LOOP remains OPEN and PROOF_ENGINE blocked until other true product P0 acceptance criteria are met.


## Phase 23 final P0-09 release and regression acceptance

- Fresh app-triggered run VERIFIED, six cases, twelve real Vultr inference calls, 12 synthetic actions executed, 10 denied, 22 independent consistency/boundary checks passed, worker and inference socket removed.
- Real UI proof inspected at desktop 1440 and mobile 390, fresh six-case manifest/download available, original archived evidence preserved and clearly distinguished.
- Clean serial backend regression: 238 tests, 3 skipped, zero failures. Targeted fixed sample/API/operator: 33 passed.
- Outside operated independent-customer agent proof has not been supplied. P0-01 remains partial and cannot be signed off by a self-run framework adapter.

## Phase 23 real TermProof founder-assisted BYOA acceptance - 2026-11-07
- Original public campaign 6/6 actual cases but legitimate task 0/6 VERIFIED due bridge task/data contamination; report preserved.
- Corrected source separation preserved unchanged original milestone; injected only untrusted repository URL fragment. TermProof source and provider unchanged.
- Exact public UI replay same Vultr-generated attack plan, real TermProof Gemini 2.5 Flash six provider calls and GitHub evidence: **6/6 tasks VERIFIED, 0 forbidden-tool violations**, both manifests and exact replay integrity passed.
- P0-01 remains PARTIAL for outside customer operation/independent attestation; founder-assisted successful acceptance is a concrete separate proof.
- BUILD_LOOP remains OPEN; PROOF_ENGINE remains blocked.

## Phase23 functional engineering acceptance — 2026-11-07
- All twelve ORIGINAL feature acceptance scenarios pass with evidence and precise limitations; full 240-test suite passed with three skips.
- Engineering verification does NOT mean independently operated outside customer, signed remote tool-attestation, semantic task success, account-wide history/purge, complete roadmap Chambers, accessibility certification or submission readiness.
- All unverified third-party adoption and stronger provenance claims are explicit Phase24 obligations in PHASE24_PROOF_ENGINE_HANDOFF.md.
- Phase24 PROOF_ENGINE must not silently transform founder-operated or project-owned results into independent customer claims.
