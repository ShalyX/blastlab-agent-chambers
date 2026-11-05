# BLASTLAB — ORIGINAL PRODUCT THESIS RESTORED / LOCK v3
Date: 2026-11-05 | Deciding authority: user's explicit correction in conversation
Status: PRODUCT LOCK REOPENED, P0 IMPLEMENTATION UNVERIFIED
Supersedes v2 as product scope. v2 is a successful technical demo and remains preserved in Git history.

## Non-negotiable user-approved definition

**BlastLab is a lab where people BRING THEIR OWN AI AGENTS to be attacked, stress-tested and evaluated.** The lab actively tries to make an agent violate its instructions, tool permissions or task constraints using multiple types of controlled prompt attacks, indirect injection and adversarial material. If an agent fails, the developer sees exact behavior, impact, reproducible evidence and mitigation steps they can take, then reruns to verify a fix.

Target user: individual/team building an AI agent who needs evidence it can withstand hostile inputs before shipping.

Core promise: Connect your agent -> define what it may and may not do -> launch an adversarial campaign -> observe real agent actions and detected failures -> inspect replay & blast radius -> receive specific fixes -> rerun and compare.

Magic moment: A connected USER'S OWN real agent is induced to attempt a forbidden action (or resists it); the lab records the exact adversarial payload and observed action, relates it to a clear rule, and shows a tested mitigation. Not a scripted internal fixture disguised as a third-party agent.

## P0 coverage ledger — DO NOT SILENTLY CUT

| ID | Locked capability | User value | Product stage | Status 2026-11-05 | Acceptance proof |
|---|---|---|---|---|---|
| P0-01 | Bring/connect OWN agent | Can test what I actually built | Agent onboarding | **NOT STARTED** | Judge connects independent agent implementation using documented connector; real response obtained |
| P0-02 | Define agent task and rules | Knows authorized vs forbidden | Configuration | **NOT STARTED** | Task, allowed actions, forbidden actions, success condition persisted and validated |
| P0-03 | Real adversarial attack campaign | Lab tries multiple prompts/injection techniques | Test chamber | **NOT STARTED** | At least 3 distinct attacks against connected agent, with real observed outputs (not scripts) |
| P0-04 | Safe execution and boundaries | Tests without uncontrolled harm | Execution | **PARTIAL** | Hosted tests isolated, bounded, no real secrets/real exfil; authenticated session & abuse controls |
| P0-05 | Actual verdict against user's agent | See what broke and how | Evaluation | **NOT STARTED** | Logs exact tested outputs/tool intents, pass/fail/unknown by contract, not fixture-only policy denials |
| P0-06 | Evidence-based fix recommendations | Can improve agent | Results | **NOT STARTED** | Each failure references exact evidence and targeted mitigation; rerun tested |
| P0-07 | Replay, history, before/after | Can demonstrate improvement | Evidence/regression | **PARTIAL** | Persist user-agent campaign and compare a before/after run |
| P0-08 | First-class BYOA workflow UI | Accessible working product | Agent setup / Lab / Report | **NOT STARTED** | Real browser journey, mobile/error/loading/empty/auth |
| P0-09 | Real Vultr attack/evaluation integration | Sponsor tech integral | Engine | **PARTIAL** | Actual Vultr Serverless Inference attacker/evaluator, Vulkan VM orchestrator, controlled worker |
| P0-10 | Valid verifiable results | Can trust claims | Proof | **PARTIAL / FAIL** | Export binds run metadata/results to evidence; no false claim of unsigned origin authenticity |
| P0-11 | Retain Chambers and attack surface breadth | Broad adversarial laboratory | Chamber library | **PARTIAL** | Web works; other intended surfaces explicitly tracked and not silently dropped; test breadth not fake |
| P0-12 | Demo separate from product | Judge not fooled by a fixture | Demo / Samples | **NOT STARTED** | Supplier inventory appears only as DEMO with visibly synthetic fixture source |

## Locked user journey
1. Arrive -> **Connect your agent** (not "choose our canned mission").
2. Establish compatible connector, real handshake and scope/permission setup. User secrets remain with user's agent; never paste private keys into a public form.
3. Select threat surfaces / multiple attack techniques, choose intensity/cost limits and mission.
4. BlastLab attacks the connected agent, with real input/response cycles and reproducible transcripts. It should attempt to break the agent, not merely display attack cards.
5. Evaluate only observable evidence: exact prompts, actual agent messages and attempted tools; mark unverified unknowns.
6. Deliver severity, attack success/failure and blast-radius analysis with actions to repair.
7. Export report, rerun agent after mitigation and compare.

## First safe integration contract (engineering decision; not a reduction in product scope)
Initial path: a standard **pull-based Python agent connector** that runs in the owner's own environment and calls their agent code. The connector initiates HTTPS requests to BlastLab on Vultr to retrieve attack tasks and submits actual agent outputs/tool intents. This avoids BlastLab making arbitrary outbound calls to user-supplied endpoints (SSRF) and avoids collecting user LLM keys. More adapters (REST agent endpoint, JavaScript) remain P1 integrations, not substitutes for real BYOA.

The adapter must accept an actual independently authored agent callable. Example user requirement: implement `respond(task, untrusted_text)-> {answer, tool_calls}`; connector invokes it for each injected case. Responses are **user-runner-reported**, not Vultr-executed attestations; label honestly. BlastLab's own adversarial campaign and result processing run on Vultr.

## Existing proof — valuable but not product completion
- Real Vultr VM, GLM-5.3 Serverless Inference, Docker Chromium and supervisor scheduled reset.
- Working Chamber UI, 2 supplier arithmetic tasks, 4 attack fixtures, policy stress and trace viewer.
- This is **DEMO / SAMPLE RUN ONLY** until independent agent is connected.
- The deterministic fixture's 1/4 denials are not a user agent failure; the real embedded GLM model proposed 0 forbidden actions.
- The sanitized event-chain verifier currently does not bind critical summary/report metadata. Gate blocked.

## Explicitly forbidden product drift
- No renaming the supplier scenario as "test your agent".
- No marking BYOA complete because user can select scripted fixtures or our hardcoded GLM model.
- No stopping after an HTTP handshake if attacks were never run against the connected agent.
- No shipping a report with scripted results attributed to a real external agent.
- No treating screenshots/demo/slides as a substitute for a connect -> attack -> fix workflow.
- No skipped Operator phases or declaring JUDGE_READY before real P0 acceptance and a fresh Judge Simulator PASS.

## Operator sequence
Resume at **PRODUCT_LOCK** (because former v2 product lock did not match user-approved thesis). Once contract is preserved: NAME_LOCK (check unresolved existing brand collision), DEMO_ARCHITECTURE (new true magic moment), EVIDENCE_PLAN (proof standards for external agent), DEPENDENCY_ATTACK (is agent connector feasible, threat boundary), TECHNICAL_DERISK (real independent agent response against attack), BUILD_VERTICAL_SLICE, PRODUCT_REVIEW, BRAND_KIT, ART_DIRECTION, REFERENCE_BOARD, VISUAL_ASSET_STRATEGY, MOTION_STORYBOARD, DESIGN_LOCK, DESIGN_ENGINEERING, VISUAL_QA, BUILD_LOOP, PROOF_ENGINE, RED_TEAM, PRODUCT_HYGIENE, DEMO_PRODUCTION, DEMO_QA, PITCH, JUDGE_SIMULATION, PRIORITIZED_FIXES, FEATURE_FREEZE, SUBMISSION_AUDIT, READY_TO_SUBMIT, SUBMITTED. A stage needs its actual exit evidence. Existing assets may be reused where proof remains valid, but downstream gates are invalidated by the product revision.

## Initial admission criteria for engineering
Real independent agent (not deterministically scripting tool actions as our own fixtures) connected via published protocol, 3+ attacks delivered, real replies recorded, at least one observed policy violation and one resilient case, targeted remediation, isolated/limited data handling, real user journey from connect through report. Do not declare a finished product on the first passing integration.
