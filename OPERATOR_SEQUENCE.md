# Hackathon Operator — enforced sequential gate register
**Date:** November 5, 2026. The user explicitly instructed us NEVER to skip a specialist/phase. A passing unit test or finished demo cannot stand in for a missing product gate.

## Why we're here
The former v2 release passed its internal demo tests, then skipped Product Integrity / Judge Simulation and rushed to submission. Its actual external-agent P0 was missing. Lock revision v3 restores the original thesis. The previous presentation and judge scores are now STALE for the corrected product.

## Sequence — every stage must have a recorded exit artifact
| # | Stage | Current classification | Required proof |
|---|---|---|---|
| 01 | INTAKE | Historical, completed for Vultr hackathon | Original challenge/eligibility |
| 02 | RUBRIC_DECODE | Historical, reviewed; weights unknown | Official rules in HACKATHON.md |
| 03 | RESEARCH | Historical, review as needed | Competition/technical landscape |
| 04 | IDEATION | Historical, BlastLab chosen | Original decision |
| 05 | HUMAN_IDEA_GATE | User explicitly chose BlastLab | User decision |
| 06 | VALIDATION | REOPENED for BYOA business/technical promises | Product Critic PASS/MODIFY |
| 07 | PRODUCT_LOCK | **CURRENT GATE / corrected v3** | USER-APPROVED BYOA P0 ledger mapped to original thesis |
| 08 | NAME_LOCK | OPEN / Blast Lab name collision candidate | Naming review or explicit knowingly accepted working name |
| 09 | DEMO_ARCHITECTURE | STALE | First actual own-agent attack + mitigation storyboard |
| 10 | EVIDENCE_PLAN | STALE | Claim-by-claim proof standards for user-agent trials |
| 11 | DEPENDENCY_ATTACK | INDEPENDENT PROBE (no formal phase advancement) | Genuine external connector over HTTPS, safe data handling |
| 12 | TECHNICAL_DERISK | PROBE BEING TESTED, NOT EXITED | Independent real agent responds to multiple attacks; controlled tool observation |
| 13 | BUILD_VERTICAL_SLICE | NOT PASSED | Public Connect → real agent → attack → observed failure → fix |
| 14 | PRODUCT_REVIEW | FAILED previously; requires re-run | Critic against v3 P0 |
| 15 | BRAND_KIT | STALE | Brand for actual BYOA product |
| 16 | ART_DIRECTION | STALE | First-party actual agent connect/attack/report design |
| 17 | REFERENCE_BOARD | STALE | Product-specific visual references |
| 18 | VISUAL_ASSET_STRATEGY | STALE | Meaningful connection, threat and results visualization |
| 19 | MOTION_STORYBOARD | STALE | Real attack/failure evidence motion |
| 20 | DESIGN_LOCK | STALE | Accepted composition and components |
| 21 | DESIGN_ENGINEERING | PARTIAL local WIP | Actual BYOA UI |
| 22 | VISUAL_QA | LOCAL WIP / old v2 QA invalid | Desktop/mobile/screens/interactions |
| 23 | BUILD_LOOP | OPEN | Every v3 P0 verified with independent integrated evidence |
| 24 | PROOF_ENGINE | OPEN | Fix manifest integrity, actual agent behavior, sponsor proof |
| 25 | RED_TEAM | OPEN | Abuse/forgery/auth, malicious agent adapters |
| 26 | PRODUCT_HYGIENE | REOPEN | Run user's installed skill end-to-end and capture QA |
| 27 | DEMO_PRODUCTION | STALE old demo | New actual BYOA product recording |
| 28 | DEMO_QA | OPEN | Actual footage/audio/labels verified |
| 29 | PITCH | STALE old pitch | Real value proposition/test-your-own-agent |
| 30 | JUDGE_SIMULATION | FAILED on v2; must repeat against v3 | All four judges incl product fidelity |
| 31 | PRIORITIZED_FIXES | OPEN | Remedy simulation findings |
| 32 | FEATURE_FREEZE | OPEN | No missing P0; explicit user-authorized cuts only |
| 33 | SUBMISSION_AUDIT | BLOCKED | Verify all mandatory artifacts & challenge rules |
| 34 | READY_TO_SUBMIT | BLOCKED | All upstream phase gates PASS |
| 35 | SUBMITTED | BLOCKED | Authenticated submission and observed receipt |

**Progress notes:** Engineering integration experiments can be performed in parallel to resolve existential dependencies; that DOES NOT mark the formal sequence as complete. Store evidence, then return to the earliest open prerequisite. No silent phase promotion.

## Automatic check on transitions
The script `ops/phase_gate.py` refuses skipping stages and refuses JUDGE_READY if current P0s remain unverified. The user-facing product cannot be declared complete until all P0s are proven. Tests `test_phase_gate.py` exercise those guards. The Operator must explicitly run the checker before reporting any transition, and stop on non-zero exit.
