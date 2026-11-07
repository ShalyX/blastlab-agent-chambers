# Phase 24 — Proof Engine status / verified evidence and outstanding gate

**Date:** November 7, 2026
**Operator stage:** PROOF_ENGINE (24 of 35)
**Status:** OPEN — technical proof portfolio built, independently checked and deployed; outside-owned/operated customer verification not yet obtained.

## Deployed judge evidence

Live URL: https://blastlab.45-77-138-147.sslip.io/proof
Sanitized JSON: https://blastlab.45-77-138-147.sslip.io/proof/evidence.json
Public JSON SHA-256: ebea606f79346929a89c614bfdd8888a071f7a67b4a78e449872f0ee47c4d208

Four distinct proof lanes, grounded in locally retained actual reports:

| Lane | Measurement | Grounded scope | What it does NOT show |
|---|---|---|---|
| Same source agent, trust-policy repair | **3 → 0** observed configured violations | Vultr GLM-5.3, same callable, tool signatures, task and attack plan; real model baseline/retest reports verified | No executed malicious actions, and not a customer-owned repaired agent |
| TermProof legitimate-task repair | **0 → 6** deterministic VERIFIED task outcomes | Existing owner-authored TermProof's genuine Gemini API/ GitHub adapter, unchanged model and verifier; BlastLab connector fixed | Not a TermProof model security improvement or independent third-party customer |
| Vultr isolated sample | **22/22** independent boundary checks | Archived project-owned Docker worker: 12 actual model calls, 12 harmless actions, 7 denied, network blocked and teardown observed | Does not contain customer-submitted code; distinct from November 7's fresh worker with 10 denied actions |
| PydanticAI interoperability | **0 → 0** configured violations | Project-operated real PydanticAI framework through public outbound connector | No claimed security improvement and not independent customer adoption |

The public page includes each six-case result, before/after report manifests, event chain roots, same attack-plan SHA-256, source class and limitations. No raw synthetic attacks, canaries, access tokens or recovery receipts are included in the public file.

## Proof Engine machinery completed

- Compiler: deploy/phase24_compile_proof.py — reloads six original privately retained raw reports, checks each with agent_lab.verify_report and three real before/after pairs with verify_import, cross-checks the archived Docker host verification and the 240-test regression.
- Integrity tests: test_phase24_proof_engine.py — **7 PASS** on the authorized evidence machine; deliberate verdict and event hash tampering is rejected. Clean checkouts without private raw reports explicitly SKIP and must not be described as having independently reverified the raw reports.
- Offline bundle: artifacts/phase24-proof-engine/private-judge-verification.zip, SHA-256 be75735a8bff7e484f5225d6bf7d51487a917785217cc8135adfc4b5c6704178. Contains the unredacted six raw reports and archived worker proof, source verifier and file manifest. Extracted fresh Python environment **PASS**. Tampering the original report **FAILS CLOSED**. **PRIVATE LOCAL ONLY**; intentionally not uploaded or committed.
- Frontend: web/src/ProofEngine.tsx, web/src/proof-engine.css. TypeScript/Vite build PASS. Public proof is discoverable from Connect and the project-owned contained sample.
- UI QA: web/qa-phase24-proof.cjs and web/qa-phase24-public.cjs — 4 proof lanes at both desktop 1440 and mobile 390, **8 checks PASS** for each environment. Downloaded JSON hash matches the exact local published file. Zero JS errors, zero overflow.
- Deployment: deploy/phase24_proof_publish.py and deploy/phase24_proof_install.sh. VM backup at /opt/blastlab/backups/20261107-phase24-proof-v1. Static UI/data only; existing API/model/secrets untouched. VM release returned PHASE24_PUBLIC_PROOF_RELEASE_PASS. Public QA returned PHASE24_PUBLIC_PROOF_BROWSER_QA_PASS.

## Remaining exit gate (do not fabricate)

1. **Independent outside operator:** one genuinely separate developer must personally operate an existing agent through BlastLab, with source provenance and permission to cite. Founder-operated TermProof and project-operated PydanticAI do not meet that.
2. **Runner origin/side effects:** externally proposed/observed tool intentions remain reported by the owner runner; no signed third-party origin attestation or independent hidden-action evidence exists. Scope the claims accurately or add a verifiable signing and audit mechanism before claiming that level of provenance.
3. **Task success and product scope:** a literal answer marker does not certify arbitrary task correctness. Account-wide historical browsing/purge and additional proposed Chambers are not implemented. Do not claim their availability.
4. **Further Operator stages:** Red Team (25), Product Hygiene (26), Demo Production (27) and onward have not yet passed. No feature freeze or submission approval.

### How to complete the outside-runner check

Ask an unrelated developer to use the public independent testing guide at https://blastlab.45-77-138-147.sslip.io/connect/independent-tester.md. They must run their real agent, complete six adversarial cases, save the original unredacted report and manifest, and make their operator and agent source provenance checkable. If a real finding occurs, capture the same agent changed under exact attack-plan replay. Never ask for their model secrets or private credentials.

The next phase **RED_TEAM** must not be entered until this Phase 24 proof gate has a documented PASS. Technical evidence is now judge-readable, but independent-customer acceptance is **OPEN**.
