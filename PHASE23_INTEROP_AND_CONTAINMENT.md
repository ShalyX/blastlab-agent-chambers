# PHASE 23 — Third-Party Framework + Contained Sample Integration

**Date:** 2026-11-07
**Operator phase:** 23 BUILD_LOOP — OPEN (two verified product slices, remaining P0 blockers).
**Locked product:** BlastLab BYOA adversarial testing, evidence-linked remediation, exact retest. Supplier Web Chamber remains secondary.

## 1. Real third-party agent framework over PUBLIC HTTPS — PASS

Agent execution is implemented using PydanticAI `Agent` from the independently maintained Pydantic open-source package (pydantic-ai-slim 2.66.0). The thin BlastLab adapter, credentials, campaign definition and testing account are **project-owned**; this is not a customer-authored application or independent customer adoption.

- Source: `examples/third_party_pydantic_agent.py` uses `pydantic_ai.Agent`, `OpenAICompatibleProvider` pointing to Vultr's GLM-5.3 chat endpoint, and a harmless synthetic-record tool. Model responses and framework-proposed tool calls are captured by the outbound Python connector.
- Real single-case probe completed and invoked the PydanticAI-registered `read_synthetic_record` tool.
- Public run: `python -m deploy.phase23_third_party_pydantic` completed two authenticated six-case sessions over `https://blastlab.45-77-138-147.sslip.io`. Attack plans were Vultr-generated, same task/tool rules/canary/attack plan used before and after the actual system-prompt policy change.
- Baseline **0 observed rule violations / 6**, refined **0 / 6**. This is real interoperability/regression success, **not** a fabricated 3-to-0 or proof that previously observed weaknesses were fixed.
- Both report manifests verified, exact retest report comparison verified, connector completed all **12** case submissions. Source provenance remains `EXTERNAL_AGENT_RUNNER_REPORTED`, not VM-attested.
- Original reports: `artifacts/phase23-third-party-pydantic/baseline-report.json`, `refined-report.json`, `summary.json`.
- Independent-verifier-backed sanitized public summary: `web/public/third-party-pydantic/proof.json`; source `deploy/export_third_party_proof.py`.

## 2. Vultr-contained worker proof integrated in judge product — PASS for archived evidence, not on-demand execution

- Proof is from the actual **2026-11-06** Phase12 disposable Docker worker on the Vultr VM, not a browser-only simulation. `artifacts/vultr-byoa-containment-phase12-20261106/` contains VM evidence.
- Exporter `deploy/export_contained_sample.py` re-validated the original report's manifest using `agent_lab.verify_report`, compared independent verifier manifest hashes, and required all **22/22** recorded boundary/consistency checks.
- Recorded: **6 cases**, **12 inference requests and responses**, **12 worker-executed harmless synthetic actions**, **7 forbidden actions denied**, `--network=none`, read-only root, unprivileged user, no Docker socket, no worker inference credentials, and verified worker/socket removal after completion.
- The attack plan was replayed from an already approved **Vultr-generated** plan with a rotated test canary; not a fresh planning run in the public UI.
- Public first-party page `/contained-sample` (also linked from `/app` and `/judge-demo`) renders the six actual case responses, 22 independent checks, host/worker boundary, runtime aggregate counts and provenance limitations. It also shows the separate PydanticAI public HTTPS test, explicitly project-owned.
- Static sources: `web/public/contained-sample/proof.json`, `web/public/third-party-pydantic/proof.json`. UI: `web/src/ContainedSample.tsx` and `web/src/contained-sample.css`.
- Browser QA: `node web/qa-contained-sample.cjs` passed on desktop 1440px and mobile 390px **locally and on the deployed public HTTPS page**. All six case rows and all 22 checks rendered, framework evidence 0-to-0 rendered, zero browser errors and no horizontal overflow.
- First contained-sample deployment: `deploy/phase23_contained_publish.py` and `phase23_contained_install.sh`, production PASS with backup `/opt/blastlab/backups/20261107-phase23-contained-ui`.
- Second deployment adds framework evidence: `deploy/phase23_evidence_v2_publish.py` and LF-normalized `artifacts/phase23_evidence_v2_install.lf.sh`. A first SSH attempt timed out **before making production changes** (read-only VM inspection proved backup and proof absent). Staged Windows CRLF script then failed at line 2, also before changes; LF-normalized script was re-uploaded. Final `PHASE23_EVIDENCE_V2_PUBLIC_PASS` and public Chrome QA PASS. Backup `/opt/blastlab/backups/20261107-phase23-evidence-v2`.
- No user credentials, model keys, original session storage, API code, containers, or DNS were changed during the static evidence deployments.

## 3. Product-integrity limits that remain OPEN

- P0-01: Third-party **framework** works but independently authored **customer agent** onboarding remains unaccepted. No claim of third-party customer adoption.
- P0-09: Original contained worker truly executed on Vultr and is now discoverable in the public product, but the UI currently opens **archived** verified evidence. There is no safe on-demand public job dispatch or customer-agent execution inside that worker. Customer agent runs on its **owner's** machine by design.
- P0-07: Previously delivered 30-day, per-campaign recovery key works, but account-based multi-session history, legacy session recovery and automated retention/purge are still incomplete.
- P0-05/P0-10: Runner-reported tool intents do not become independently verified external side effects. Internal hashes alone do not attest to customer runtime identity.
- The Phase13 real project-owned GLM-5.3 matched 3-to-0 same-agent policy-edit result remains separately valid and is not replaced by this PydanticAI 0-to-0 framework test.
- A full production customer onboarding and release hygiene/QA gate remain to be completed. No Judge Demo or Product P0s are silently promoted to VERIFIED from these slices.

**Milestone verdict:** PASS for public third-party framework interoperability and judge-facing archived contained-worker evidence. **BUILD_LOOP remains OPEN; PROOF_ENGINE Phase24 remains blocked** until the remaining independently testable product acceptance gates are satisfied.
