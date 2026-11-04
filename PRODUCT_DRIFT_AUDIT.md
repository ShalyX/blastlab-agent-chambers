# BLASTLAB | PRODUCT-DRIFT & COMPLETENESS AUDIT
**Date:** November 5, 2026 (Africa/Lagos)
**Owner:** Hackathon Operator HQ -> Product Critic
**Verdict:** MODIFY: original north-star intact, product definition/UI drifted to a fixed-test replay viewer.
**Scope:** READ/INSPECT ONLY. No application, API, billing, infrastructure or deployment changes authorized by this audit.

## 1. Evidence sources & certainty
1. November 1 original ideation history recoverable in prior conversation context: BlastLab described as "crash testing for autonomous agents"; give an agent legitimate work inside hostile environments, observe failures/survival and produce violations, replay, blast-radius evidence and remediation. Five Chamber categories **proposed**: Web, Toolchain, Vault, Machine, Chaos. User loved BlastLab and chose it as leading direction; no proof all five were individually locked for the initial release. Repro remained a fallback early in ideation.
2. Root Git history at baseline `0833f77`: the narrow $72 supplier workflow was explicitly `TECHNICAL_DERISK`, with proof goals (real agent, hostile page, policy, destructive reset, resumed verified mission), and separately listed later public-product work. It was not a final product lock.
3. Repository current commit `c1d1c29`: `PRODUCT.md`, `DESIGN.md`, `README.md`, `control_api.py`, `agent_spike.py`, `browser_sandbox.py`, `evidence_export.py`, `web/src/App.tsx`, `HYGIENE.md`, `SCORECARD.md`, `.hackathon/state.json`, and independent VM proof.
4. Official event pages rechecked November 5: https://lablab.build/ai-hackathons/vultr-hackathon and https://community.vultr.com/e/vultr-agent-rush-hackathon. The challenge expects a user-facing agent that performs real work on Vultr, dispatches to an isolated sandbox, returns verifiable output; required Vultr VM and Serverless Inference (Challenge 1), public GitHub, public demo, recorded containment video. Lablab submission checklist includes project description, tags, cover image, video, slide presentation, application URL and GitHub link. Verify exact participant-dashboard cutoff; online phase Nov 3-8.
5. Naming collision search on Nov 5: a pre-existing Blast Lab technology/hardware/software firm at blastlab.co, and entities with similar names. This is a **confusability research hit, not a legal trademark opinion**. Name remains a working title, not cleared/locked.

## 2. Product north star vs current lock
**Original north star (high confidence):** "Agent crash-testing facility": take a legitimate agent mission, select a hostile environment/attack, run it under enforceable constraints, observe attempts and fallout, destroy/reset, verify task result, then report risk, evidence and remediation.

**Current real product (verified scope):** public landing; authenticated-owner fixed-supplier run; recorded GLM-5.3 or deterministic fixture source toggle; execution scrubber; supplier injected page, policy inspector, VM/worker evidence; architecture view and sanitized JSON download. One canned agent, one mission, one injected supplier document, one scripted attacker fixture. No Chamber catalogue, mission/test authoring, coverage assessment, user-agent onboarding or remediation result.

**Structural drift found:** Rejection of proposed 3D cutaway **visual direction C** in DESIGN.md was treated as justification for dropping the Chamber **product architecture**. These are unrelated decisions. `PRODUCT.md` actively codified one case-file replay as the product and designated broader missions/URLs as non-goals, although baseline described that case as the technical de-risking scope. `.hackathon/state.json` progressed to PRODUCT_HYGIENE without a proven original product-lock reconciliation.

**Operator gate:** PRODUCT_REVIEW must reopen. Product Critic verdict MODIFY; do not jump to Demo Director yet. Preserve proven technical slice and current product design components.

## 3. Chamber inventory / original concept status
| Chamber (originally proposed) | Intended stress surface | Present reality | Classification |
|---|---|---|---|
| **The Web** | Malicious web pages / prompt injection and browser-boundary enforcement | A real hostile supplier page, GLM-5.3 tool loop, Chromium+Docker reset, separate scripted policy denials | **PARTIAL**: executable scenario, no selectable Chamber or test catalogue |
| **Toolchain** | Poisoned tool results/documentation/APIs, misuse of tool permissions | One generic capability allowlist for browse/finish; no tool-output poisoning Chamber | **UNIMPLEMENTED** |
| **Vault** | Secret exfiltration / sensitive data exposure | Worker deliberately inherits no real secrets (good isolation), but no safe decoy-secret challenge/proof surface | **UNIMPLEMENTED** |
| **Machine** | Destructive files, host/shell actions | `execute_shell` denied at the policy layer by a scripted proposal; no destructive operation actually executed inside a disposable Machine stress chamber | **UNIMPLEMENTED** |
| **Chaos** | Resource exhaustion, loops, crashes, recoverability | Docker resource limits and *scheduled* trusted interruption/reset; no parameterized chaos scenarios or stress results | **UNIMPLEMENTED** |

**Crucial honesty:** The five named Chambers were a proposed architecture, not all independently user-locked launch criteria. No five-working-Chamber claim is permitted. A static gallery with four "Working" badges would be deceptive.

## 4. Missing product journeys and critical risks
| ID | Finding | Evidence | Risk | Priority |
|---|---|---|---|---|
| D01 | No Chamber navigation, selection or life cycle | UI has Landing / Control / Evidence / Architecture; `control_api.py` has `mode in (live, scripted)` only | Original product identity invisible | P0 |
| D02 | No legitimate mission configuration | Hardcoded `SYSTEM`, `/supplier`, $72 stock, exact tool grammar in `agent_spike.py` | Business value appears one-off/hardcoded | P0 |
| D03 | No threat/scenario catalogue or parameter selection | One `hostile` page flag, deterministic fixture, no scenario parameter in API | User cannot perform an actual controlled test sweep | P0 |
| D04 | No agent-under-test interface beyond built-in GLM-5.3 | Hardcoded internal model/provider and tool schema; no external agent harness | Claim "test your agent" would be unsupported | P1 initial release; central longer-term product requirement |
| D05 | No blast-radius result or test grade | Reports mission success, denied actions, resets, traces; no explicit what was reached/damaged/contained or severity and attack coverage | Product name/promise unsupported as a general test report | P0 |
| D06 | No remediation guidance/actionable weakness report | No report sections mapping violation -> capability -> recommendation -> evidence | An engineer learns that the run finished, but not what to fix/what remains untested | P0 |
| D07 | No persistent browseable run history, comparison, multi-case report | Public GET exposes two latest files; fresh runs overwrite `live.json`/`scripted.json`; job metadata in process memory | Cannot compare baseline vs fix, regressions or attack variants | P1, valuable to product |
| D08 | Public judges cannot start a real run; owner token onboarding absent | Owner token generated on VM, typed into modal; no user-facing access bootstrap | Call-to-action "New Test Run" is blocked for normal users | P0 for interactive judge experience (with abuse/cost limits) |
| D09 | No independently reconstructible public cryptographic proof | `evidence_export.py` first verifies original chained JSONL then emits stripped event summary hashes, omitting canonical source body and previous hash. UI says "Nothing here requires trust." | Sanitized download cannot validate original raw SHA chain by itself; server's validation boolean must be trusted | P0 claim/evidence correctness |
| D10 | Real LLM did not propose any denied calls | Real model read hostile page, made three genuine calls, zero denials; scripted attacker made four denied calls | Cannot pitch "live-model attempted dangerous command and sandbox absorbed it" | P0 demo truth / P1 broader attack coverage |
| D11 | Supervisor reset is scheduled, not breach-triggered | `trusted_interruption` after first observed page in `agent_spike.py` | Must call it an intentional fault-injection exercise, not attack detection/self-healing response | P0 narration accuracy |
| D12 | No customer workflow before/after reporting, coverage matrix or repeat-test loop | App shows one case file and latest result | Low differentiation/business value even with visually polished UI | P0 workflow / P1 history |
| D13 | Brand not truly locked; collision candidate found | `BRAND.md` says working name only; existing Blast Lab tech firm | Confusion/trademark/marketing risk | P1, naming gate open |
| D14 | No verified actual demo movie, slide deck, public repo, final submission record | No Git remote, no LICENSE, no video/presentation artifacts; HACKATHON.md scope/checklists incomplete | Eligibility / presentation risk | HARD DEADLINE P0 |
| D15 | Official event may require original, MIT-compliant submission | Event says original/MIT-compliant; no LICENSE | License/attribution compliance needs review; not automatically a disqualification conclusion | HARD DEADLINE P0 |
| D16 | Source-of-truth files contradict current reality | `HACKATHON.md`, `DEMO.md`, old `PROJECT.md` sections say public UX absent even though site launched | Judge and Operator may mistake stale assertions for current facts | P1 hygiene |
| D17 | Self-rated 21/24 visual score is insufficient product score | `SCORECARD.md` rates design screenshots, not the missing user journey or actual rubric weights | Premature "ready" claim possible | P0 revise scorecard |
| D18 | Product Hygiene skill full canonical execution not substantiated | `HYGIENE.md` lists "inspected and applied"; Operator requires *invoke skill end-to-end*, rerun and log output | Hygiene gate must be marked OPEN until verified | P1 |
| D19 | Controller and sandbox production hardening unfinished | Root backend controls Docker, single owner bearer, cost exposure, no multi-tenant auth, only local fixed scenarios | No broad production-grade security claim permitted | P1 beyond controlled demo |
| D20 | Hosting address temporary and pricing resources accrue charges | `sslip.io`, active Vultr VM | Launch polish and operational risk | P1 |

## 5. Strong parts to preserve, not rebuild
- Real Vultr VM, GLM-5.3 Serverless Inference, Docker Chromium, strict policy, no secrets in worker, resource limits, 2 verified generations and a real $72 accepted result.
- Separate demonstrably live-model decisions and deterministic adversarial fixture; no fabricated mixed evidence.
- Hash-chained original raw traces, independent server-side audit, sanitized public replay.
- Functional polished landing, UX components, interactive timeline, inspector, event ledger, Evidence Vault, architecture view, responsive UI and HTTPS deployment.
- 71 local regression tests (68 pass, 3 optional skips) and targeted VM/API tests. Preserve the existing security harness.

## 6. Highest-value corrective scope (recommendation, not approval or implementation)
**Do not attempt five superficial running Chambers before November 8.** Product Critic recommends one complete **Web Chamber** with a genuine start-to-report flow. Other four Chambers remain clearly **NOT IMPLEMENTED / future test surfaces** unless their specific backend execution is proven.

Minimum viable product restoration, in priority order:
1. Reconcile PRODUCT_LOCK to restore "crash-test facility" vs "case-file replay" and implement Chamber entry point; Web Chamber must lead, Control Room becomes the execution/inspection view.
2. Introduce securely constrained mission/test configuration: selected authorized mission template and hostile scenario variants (no arbitrary public browsing or host commands until isolated safe threat model is proven).
3. Execute an **actual selected Web test** through the Vultr inference/Docker path, report outcome, policy violations, scope/coverage, containment, recovery and what remains untested. Keep live-model and scripted-fixture paths unmistakably distinct.
4. Add clear pass/fail/coverage and evidence-grounded remediation suggestions, no invented danger scores. Expose a public/exportable verifier path appropriate for sanitized evidence, with clear limits.
5. Save a stable per-run identifier and history or, at minimum, two comparable proof cases and controlled repeat-run affordance.
6. Make reviewer interaction meaningful without exposing a costly unrestricted API; strongly rate-limit curated public tests or provide a clearly disclosed nonbillable interactive replay and owner-authenticated genuine run.
7. Re-run Product Critic -> DESIGN/Visual QA -> PROOF -> RED_TEAM -> Product Hygiene (full skill) after the product change; then Demo Director, Judge Simulator, pitch, repository, slides, video, submission audit.
8. Reassess the name after a collision/genericity search; do not call BlastLab fully cleared until a human/brand lock or time-budget decision.
9. Secure official submission requirements and exact cutoff via lablab participant form; prepare slide and cover deliverables, license/attribution audit and public repo as hard deadline gates.

## 7. What this audit does NOT conclude
- It does **not** establish that five working Chambers or arbitrary third-party agent imports were confirmed release requirements.
- It does **not** mean the working Web mechanism, Docker reset or live LLM execution was fake.
- It does **not** conclude the existing code is unsafe to run; product completeness and evidence accuracy are separate from a security penetration test.
- It does **not** endorse shipping "coming soon" Chamber cards as functional.
- It does **not** replace product scope decisions with a silent design rewrite.

## 8. Operator transition
**Detected drift:** original source (2026-11-01 ideation) vs current `PRODUCT.md` and fixed API.
**Severity:** MAJOR.
**Specialist:** Product Critic.
**Verdict:** MODIFY within original chosen thesis, not abandon or reopen ideation.
**Current blocked gate:** PRODUCT_REVIEW + PRODUCT_LOCK_RECONCILIATION; downstream previous PRODUCT_HYGIENE status and self-rated completeness are stale for the corrected product.
**Next action:** Lock the minimum Web Chamber experience and its honest claims, then implement the smallest complete end-to-end user workflow before demo production. Preserve prior technical evidence as valid for original bounded scenario; it does not automatically prove new Chamber behavior.

## 9. Competitive distinction check (public claims, not independently tested)
A competing event entry, "Blast Radius Zero: sandboxed agent runtime" (https://lablab.build/ai-hackathons/vultr-hackathon/blast-radius-zero-solo/blast-radius-zero-sandboxed-agent-runtime), publicly advertises seven containment probes, a user task input, program and output inspection, a SQLite ledger, Docker/gVisor, and a second-model evidence audit. These are **self-reported** claims; this audit has not run its product. The existence of that positioning is enough to show that "we built Docker containment" alone is not a distinctive winning pitch. Our unique wedge should be a coherent Chamber-based *agent attack laboratory* with realistic mission/attack/containment/remediation receipts, not a generic sandbox demo.
