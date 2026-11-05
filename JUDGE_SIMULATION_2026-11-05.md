# BlastLab — Judge Simulation 01 (November 5, 2026)

**Operator phase:** JUDGE_SIMULATION — **FAILED / SUBMISSION ON HOLD**. This is the first actual four-lens simulation. The old 21/24 was a visual self-score and must not count as judging.

**Evidence examined:** Published hackathon rules, live app (landing, Chamber Library, Web setup, scripted and live reports), public API records and offline verifier, actual 80-second demo contact sheet, 7-slide deck text/source, GitHub repo, historical proof and source-of-truth docs. Fresh probes below were run without executing costly inference or changing production.

## Official rubric

The organizer publishes Application of Technology, Presentation, Business Value, and Originality. **Official weights and scoring scale: UNKNOWN.** Scores here use an internal 0–10 scale and do not predict actual judges or prizes. Source: https://lablab.build/ai-hackathons/vultr-hackathon .

| Criterion | Internal /10 | Confidence | Verified merits | Deduction |
|---|---:|---|---|---|
| Application of Technology | 7 | High | Genuine GLM-5.3 on Vultr Serverless Inference, Vultr VM orchestrator, Docker/Chromium, tool policy, reset, recorded results | Public test only allows scripted fixture; genuine model proposed no forbidden actions; proof chain excludes critical report metadata |
| Presentation | 7 | Medium | Visually clear Chamber-first app, scripted real Docker run, 80s 1080p demo, slide deck | Genuine model and sponsor inference are underemphasized until late in video; homepage overclaims detection; slides were generated but not independently rendered for QA |
| Business Value | 4 | High | Clear engineer/security-reviewer audience, ability to rerun bounded attacks, result/remediation reports | No test-your-own-agent connection, arbitrary safe test target, CI integration, paying customer proof, or clear repeated buyer workflow; two variations of one fixed supplier task |
| Originality | 6 | Medium | Chamber lab identity, causal destroy/recover visualization, source-separated decisions, compare/replay evidence | Comparable submitted entries already describe generic sandboxing plus broader user tasks and more real probes; four of five Chambers are unimplemented |

**Internal simple-average orientation only: 6.0/10. This is NOT an official overall score; no equal official criterion weighting is assumed.**

## Judge lens 1 — Product

Who is it for? Agent engineers and security reviewers. Pain: untrusted page content may try to seize tool authority, and the developer needs reproducible evidence of containment and recovery. The UI clearly sells that idea and genuinely runs a bounded test.

**Main disbelief:** What practical thing can I do for my own agent? Normal reviewers cannot attach their own app/agent and cannot run live model inference without an operator token. The public route launches a deterministic fixture against a fixed supplier page; the value can look like a polished internal test harness rather than a repeatable third-party product. Neither business model nor customer validation is shown.

**Magic moment:** the worker's actual kill/reset is compelling, but the forbiddens were intentionally emitted by the fixture, not the model. The distinction is labeled correctly in the report.

## Judge lens 2 — Technical

Confirmed: read-only public GET /api/health, /api/catalog, /api/history, the scripted case and a live case returned HTTP 200. Real archived scripted case scripted-99bb851e7f39b5ba82 reports $24.00, one denied call, 47 events. A separate live GLM-5.3 case reports $24.00 and zero denied calls. Browser visits to /, /app, /app/chambers/web and both direct report URLs returned HTTP 200, no browser errors or horizontal overflow.

**P0 proof failure, reproduced:** Running deploy/judge_probe.py on actual public case JSON, verify_public_evidence correctly REJECTED a modified event, but ACCEPTED independent changes to summary.value_cents, report.verdict, mission_id and proof.trace_sha256. The sanitized event chain does not bind the user-visible report or original-source commitment. Furthermore a self-consistent unsigned chain does not authenticate server origin: it demonstrates internal consistency, not immutability against anyone able to recompute hashes. Restricting claims to event integrity or binding a full manifest and authenticating provenance is required.

**P0 language overclaim, directly observed:** Landing page says “INSTRUCTION OVERRIDE DETECTED IN PAGE.” This is a configured malicious fixture, not proven automatic detection. The scheduled worker reset is deliberate fault injection, not a detected-attack response.

**Coverage gap:** genuine LLM proposed no unauthorized action in examined runs. Security-denial evidence is legitimate but scripted. No broad prompt robustness certification, independent penetration test or multi-user hardening exists.

## Judge lens 3 — Sponsor

Vultr use is essential and credible: VM hosts the control plane, serverless GLM-5.3 makes the agent's real decisions, Docker/Chromium executes isolated browser steps on that VM. This is stronger than a host-name/logo integration.

Deduction: reviewers can only start the scripted fixture; the unique paid model integration is inspectable mainly through archived cases. The 80-second film reserves sponsor architecture for around 68 seconds. Move live model proof earlier with source-honest labels. The organizer's browser-use plan/verification/approval pattern is an example rather than a mandatory fixed implementation for all projects.

## Judge lens 4 — 30-second cold viewer

- **what_i_think_the_product_is:** A stylish security test facility for AI browser agents reading hostile pages.
- **what_i_think_is_special:** Real container kill/reset and a visible causal event track.
- **what_i_do_not_believe_yet:** That a live model tried a forbidden action and was blocked; that I can test my own agent; that the verified badge covers the entire report.
- **what_confused_me:** “detected” wording with no detector, “your agent” promise against owner-only live inference, five Chambers visible with one operational.
- **what_i_would_remember_tomorrow:** The industrial containment console and the line “the mission survived.”

**Result:** Category and visual story clear; actual AI agency, repeat buyer value and complete proof are not yet clear after 30 seconds.

## Product integrity

Approved thesis: Chamber-based agent crash-testing facility (not a case-file-only viewer). Current outcome: a verified bounded Web Chamber user journey and four explicitly future Chambers; this is a working vertical slice, not the full planned platform.

Locked acceptance check: WC01–WC05 verified in bounded scope; WC06 reporting partially verified but authenticity/scope deficient; WC07 history/compare verified; WC08 complete public proof FAIL (events only); WC09 basic UI tested but formal accessibility and presentation slide render QA not finished; WC10 official submission not done. The original Web execution mechanism is real; this simulation does not negate it.

**Product integrity verdict:** BLOCKED for JUDGE_READY. No new unauthorized design drift detected in Web Chamber v2, but original broader utility remains unproven.

## Competitive comparison (claims published by entrants, not independently tested)

- https://lablab.build/ai-hackathons/vultr-hackathon/blast-radius-zero-solo/blast-radius-zero-sandboxed-agent-runtime — entrant describes user-defined tasks, a second model auditing evidence, and seven real kernel containment probes.
- https://lablab.build/ai-hackathons/vultr-hackathon/signup-sandbox/signup-sandbox — entrant describes a specific useful browser workflow, website signup and email verification.
- https://lablab.build/ai-hackathons/vultr-hackathon/builders-nepal/detonation-chamber — entrant describes detonation of real submitted artifacts and decoy credential tracing.

Implication: Docker + threat fixture + polished UI is insufficient differentiation on its own. Our defensible advantage must be a clearly demonstrated attack → policy → containment → recovery → engineering remediation workflow that is useful beyond the contest.

## Ranked corrections — before any submission

1. **P0, Proof/Engineering:** Bind all outcome-critical report fields to a canonical export manifest and expand verifier tamper tests for event, mission, actor, scenario, value, verdict and source commitment. If provenance has no trusted signature, explicitly say so; do not imply authenticity from unsigned hashes. **Exit:** modified valuation or verdict fails verification.
2. **P0, Product/Proof:** Replace or prove “instruction override detected” and similar UI/pitch claims. Keep scheduled reset distinct from attack detection. **Exit:** every high-stakes homepage/video claim maps to actual log evidence.
3. **P0, Demo Director/Sponsor:** Lead the first 30 seconds with genuine GLM-5.3 decision + Vultr control flow. Then show a clearly labeled scripted denial. **Exit:** blind viewer can correctly tell real model from fixture, and describe Vultr's role.
4. **P0/P1, Product Critic/Engineering:** Restore a *meaningful reusable buyer workflow* within the already chosen agent crash-testing thesis, not another simulator. A safely scoped third-party agent/test adapter or developer regression case would be far stronger; do not silently lock new scope without reconciling original P0. **Exit:** judge can use/test something that applies to their own development practice.
5. **P1, Pitch/Business:** Define buyer, repeated pain, human/manual alternative and credible pricing/distribution hypothesis without fictional adoption or TAM. **Exit:** business-value slide says why anyone would pay or keep using BlastLab.
6. **P1, Presentation/Brand:** Resolve working-name collision decision; visually render and check every PPTX slide, validate final actual media playback. **Exit:** complete independent presentation QA and name decision.
7. **HARD GATE, Submission:** LabLab enrollment, team permission, submission receipt. **Exit:** verified public LabLab project URL and actual confirmation. **NOT NOW.**

## Operator handoff

**JUDGE_SIMULATION = FAIL. Submit gate remains HOLD.** Route to Proof Engine + Product Critic first. Do not claim ready to submit just because the app, GitHub, movie and slides are publicly accessible.

Reproduce read-only technical judge probe:
- python deploy/judge_probe.py
- cd web; node judge-browser.cjs

This report contains observations, not simulated customers, invented weights, new Vultr results or made-up market metrics.
