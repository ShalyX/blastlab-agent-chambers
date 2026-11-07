# PHASE 23 — BUILD_LOOP: engineering acceptance register

**Date:** November 7, 2026
**Product:** BlastLab — real bring-your-own-agent adversarial testing
**Status:** VERIFIED for the 12 locked functional engineering acceptance scenarios. Separately unproven independent outside-customer adoption is assigned to Phase24 PROOF_ENGINE; no outside-customer acceptance claim is made.

## Locked twelve P0 feature acceptance

| P0 | Functional observation | Proof / limitation |
|---|---|---|
| 01 | Real independently developed agent can connect | Pre-existing TermProof source from before BlastLab, founder-operated over public HTTPS; two campaigns of six real Gemini 2.5 Flash planner results and actual GitHub evidence. This is **not** independent outside-customer adoption. |
| 02 | Owner-defined task, allowed tools, forbidden tools and literal success marker enforced | Real TermProof persisted policy and import/replay matching contract; input-validation tests. Text marker matching **does not** certify semantic task correctness. |
| 03 | Real adaptive multi-attack campaign | Vultr GLM-5.3 planned five malicious attack families plus clean control; TermProof and project-owned same-agent each completed six live cases. Disclosed deterministic canary augmentation remains. |
| 04 | Safe boundaries and bounded execution | Outbound owner-side connector never sends model secrets/code to BlastLab, hashed short-lived join token, daily/concurrent quotas, 30-day separate recovery capability. Project-owned contained Vultr worker independently passed 22/22 boundary checks. It is NOT the customer's runtime. |
| 05 | Honest evidence-based verdicts | Actual runner-reported answers and proposed tool intents are preserved per case; event chain, full-report SHA-256 manifest and regrader bind outcomes. No hidden execution attestations. |
| 06 | Evidence-linked repair with same-agent exact replay | Same project-owned GLM-5.3 callable and tool signatures, changed only its system trust policy. Exact six-case plan **3 observed violations -> 0**. Findings link to attack/response/tool evidence. TermProof owner integration repair separately improved **0 -> 6** genuine task verifications, but is not a TermProof model vulnerability repair. |
| 07 | Durable completed report and exact history replay | Thirty-day read-only per-campaign recovery after connector token expiry; baseline import, exact plan, task/policy/canary fingerprint comparison, before/after reports. No account-wide multi-session identity/history dashboard or automated purge UI. |
| 08 | Functional UI on desktop/mobile | Production Connect, campaign, report/replay states, keyboard/case disclosure. Phase23 local QA passed TermProof and vulnerable sample on desktop 1440/mobile 390. Same-agent comparison also passed at both viewports. No horizontal overflow or JS errors in these checks. |
| 09 | Integral Vultr inference + contained judge sample | Public click spawned fresh disposable Docker worker: six cases, twelve actual model calls, twelve synthetic actions, ten forbidden actions denied, 22/22 independent evidence checks and confirmed teardown/socket cleanup. Project-owned only. |
| 10 | Replay-verifiable outcome integrity | Independent Python verifier on two original TermProof reports and same-agent real reports; tamper-regrading/matching report checks. Unsigned hashes show internal consistency, NOT source identity or cryptographic attestation. |
| 11 | Honest first-class attack-surface inventory | Published product names five LIVE attack families and separately labels three NOT INCLUDED capabilities, including customer runtime sandboxing and unimplemented Chambers. |
| 12 | No demo/product bait and switch | Real BYOA path /app; clearly separate project-owned contained sample /contained-sample; supplier Web Chamber remains explicitly DEMO, never attributed to a customer. |

## Actual project-owned same-agent remediation

- Original six-case GLM-5.3 run recorded **3** violations: role spoofing, synthetic exfiltration, memory poisoning. Four other statuses include one clean control.
- After only changing BLASTLAB_SINGLE_AGENT_MODE from baseline to hardened, the same Python callable and same exposed tool signatures returned **0** on the exact plan.
- Original attack plan SHA-256: 2732ec1be39b0d13f983ab9f85801a00d5014fceee2df36f59a85d10d12e7b4c.
- Baseline report manifest: 260d1d1e758964a09f75bbbd0a4b18eeea4231c96580a3a592d136d256b34899.
- Hardened report manifest: 8d1576c586f22ad74dd0ce6937970a0678cb59836ad7469173b6a29526650e22.
- All six responses are real Vultr inference, with tool intentions **reported**, not executed; the code does not dispatch harmful tools.
- Both reports independently passed agent_lab.verify_report, plus verify_import on the pair. UI showed exact replay 3 -> 0 on desktop and mobile with no JS errors.

## Independent owner-supplied TermProof acceptance

- The human user previously built TermProof independently of BlastLab and first operated BlastLab directly.
- The original test had 0 forbidden-rule violations but **0/6 legitimate task verifications** because our bridge contaminated the acceptance statement with hostile source text. This failure was preserved.
- The fixed bridge kept the legitimate milestone unchanged and isolated source payload in lower-trust repository data. Original TermProof model, verifier and evidence adapter were not changed.
- Exact replay of all six attacks achieved **6/6 verified legitimate tasks**, 0 forbidden-rule violations, with the same attack-plan fingerprint and manifest checks.
- That is an actual **integration repair**, not evidence that TermProof's security policy was vulnerable and patched.

## Hard evidence boundaries / Stage 24 obligations

- **No independently outside-operated customer acceptance exists.** Founder-owned TermProof may satisfy engineering connectivity, but cannot be called outside customer adoption. Obtain outside developer and genuine agent/provenance in Phase24 PROOF_ENGINE before claiming independent customer validation.
- The 22/22 containment pertains to a first-party Vultr sample. External owner-run BYOA agents are not contained inside BlastLab's VM.
- Tool actions are runner-reported. No signed source attestation, independent hidden side effect audit or universal security guarantee exists.
- The product still has no account-wide historical dashboard/purge controls or working browser/code/payment customer Chambers; none should be advertised as shipped.
- Stronger proof, red-team abuse testing, full product hygiene/accessibility, demo recording, judge simulation and submission review belong to the **subsequent** Operator phases, not Phase23.
- The declared original product scope and all twelve functional P0 areas are retained; no unsupported features or independent customers should be invented.

## Release / test records

- Frontend compiled using TypeScript + Vite.
- Local browser QA: web/qa-phase23-closure.cjs (TermProof and vulnerable example; desktop/mobile) and web/qa-phase23-same-agent-compare.cjs (same-agent 3->0 exact replay; desktop/mobile).
- Production deployment: deploy/phase23_coverage_ui_publish.py, production health check passed and previous static bundle backed up on Vultr.
- Previous 238-test serial suite passed with 3 skips (prior Phase23). New final unit regression is being rerun after a Windows HTTP test-server lifecycle fix.
- The Operator gate can only advance if **all twelve current functional P0s are legitimately accepted**, evidence files exist, the updated suite passes, and the external-customer limitation is explicitly carried to Phase24 without being falsely described as proven.

**Operator instruction:** Phase23 PASS is functional engineering completion only; it is NOT readiness to submit. Outside-operated customer adoption, independent source attestation, semantic correctness and the other Phase24 handoff obligations are explicitly unproven. Do not bypass phases 24–35.


## Final gate verification

- Final serial unit regression **PASS**: 240 tests, 3 skipped, zero errors/failures. Windows-only intermittent localhost transport WinError 10053 handled with a bounded retry inside TEST harness only; production gateway unchanged. Log: artifacts/phase23_full_regression_windows_transport_fixed.log.
- Real model same-agent 3 -> 0 exact-plan repair independently validated; 6/6 reports in both runs match the same plan.
- Frontend production deployment PASS; local desktop/mobile browser QA PASS for TermProof, vulnerable sample, and exact same-agent remediation.
- Repository and private evidence locations recorded. Raw session credentials and recovery receipt are NOT in Git.
- Proof limits and remaining external adoption obligations handed to PHASE24_PROOF_ENGINE_HANDOFF.md.
