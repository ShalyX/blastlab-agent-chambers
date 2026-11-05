# BLASTLAB | Product Lock v2 — Chamber-first crash-testing facility
Updated: 2026-11-05. Lock owner: Hackathon Operator / Product Critic.
Revision: corrective MODIFY within the previously chosen BlastLab thesis. Supersedes fixed-replay product framing (preserved in Git history). See PRODUCT_DRIFT_AUDIT.md.

## User and job
Agent engineers and application security reviewers need to answer: "What happens when my browser-using AI agent reads a hostile page, and can it still finish the authorized task?" They need a repeatable, scoped test setup, a real run, and an explainable result with concrete evidence and caveats.

## Promise and differentiator
**Crash-test your agent’s authority boundary. See what survives.**
BlastLab is a Chamber-based test facility, not a screenshot gallery and not a blanket jailbreak guarantee. A Web Chamber drives real Vultr LLM decisions and disposable Docker/Chromium, records attempted tool actions, enforces capability boundaries, forces an independently scheduled interruption, verifies recovery and produces a scope-limited assessment and readable verification material.

## Locked primary workflow
**Chamber Library → Choose Web Chamber → Configure supported mission, attack and execution engine → Launch controlled run → Live/recorded Control Room → Outcome + Blast Radius + Remediation → Re-run/compare/export evidence**.
Other Chamber cards carry explicit NONFUNCTIONAL/NOT YET BUILT labels. No fake demo buttons or hidden emulation.

## Chamber definitions and commitments
- 01 The Web: prompt injection, malicious page claims, attempted tool-authority escape. **P0 fully executable** end-to-end for 2 scoped missions and at least 3 distinct test payloads, plus clean control.
- 02 Toolchain: malicious tool outputs/third-party docs. **PLANNED, NOT EXECUTABLE**.
- 03 Vault: decoy-credential exfil / unauthorized disclosures. **PLANNED, NOT EXECUTABLE**.
- 04 Machine: destructive host/file operations. **PLANNED, NOT EXECUTABLE**.
- 05 Chaos: uncontrolled resource use, failures, timeouts. **PLANNED, NOT EXECUTABLE**. Scheduled supervisor reset in the Web Chamber is *not* proof this Chamber exists.

## P0 acceptance ledger
| ID | Acceptance condition | Proof |
|---|---|---|
| WC01 | Chamber Library is first-class, visually distinctive and honest about available Chambers | UI browser tests desktop/mobile; Web enter works; unavailable cards cannot run |
| WC02 | Web setup offers >=2 distinct legitimate missions, >=3 concrete attack scenario families and a clean baseline | Validated server-side registry, rendered cards and explicit categories |
| WC03 | An approved Web configuration reaches real Docker Chromium with Vultr model or explicitly labeled scripted attack fixture; options genuinely change observed payload/result | New end-to-end VM test, trace metadata; negative validation tests |
| WC04 | Public reviewer can initiate a *limited deterministic* Docker Web test without privileged credentials; real inference owner-controlled, bounded costs | HTTP auth/cost limits, attack API tests, deployed public smoke |
| WC05 | Control Room is preserved, linked from selected run and shows real specimen, source-labeled model/fixture decisions and reset | Browser tests; no fabricated detection/denials |
| WC06 | Results include authorized mission, policy-denial count, source type, containment/reset checks, blast-radius outcome, coverage limitations and **evidence-grounded** remediation | Versioned deterministic report tests + real VM output |
| WC07 | Runs have persistent IDs, index/list, two-case comparison and correct source/attack attribution | API persistence tests and frontend interaction |
| WC08 | Public sanitized proof is independently verifiable without access to the production server, with digest and verifier; raw original digest identified as *not* self-contained in public export | Independent local verifier checks + tamper test |
| WC09 | Restored journey has usable accessible layout, loading, error, recovery, mobile, auth and replay states | Visual QA, interaction QA, installed Product Hygiene skill re-run |
| WC10 | Release package has public GitHub, license/compliance, slides, actual video, source docs, public app and confirmed LabLab entry | External link/attachment verification and receipt |

## Safety and truth invariants
- Model can propose only restricted `browse` and `finish` calls; untrusted page data never defines supervisor authority.
- A public user never supplies a URL, shell command, prompt or credentials to the sandbox. They can choose from versioned server-controlled templates/attack families and run rate-limited **scripted** tests.
- New real Vultr model calls require an operator credential. Public scripted tests consume VM compute and are tightly rate limited.
- "Attack detected" is only used if a detection rule actually observes the attack. Page exposure is not a policy violation. A scripted denied call is not an LLM behavior claim.
- The sandbox kill/reset in this test is a planned supervisor-owned fault-injection exercise, not an automatic response to compromise.
- Blast radius means observed prevented/allowed actions in *this configured run*, not a universal security score. Unattempted attack paths remain UNTESTED.
- Original trace hash remains original-only provenance unless full original is exported. A separately generated public-sanitized chain has its own independently verifiable digest, clearly distinct.
- Web Chamber supports only templates/controlled localhost supplier route until more surfaces are safely implemented. No third-party agent connection or arbitrary public web URLs is claimed.
- Prefer preservation and reuse of proven code and current product UI. Full five-chamber implementation is not a first-release dependency.

## Experience language
A clean industrial incident-testing facility with distinct entrances: Library for choice and state, Web Chamber setup for explicit scenarios, Control Room for execution, Results for blast radius and fix-it guidance, Evidence for forensic verification. Current visual language and components retained; no cosmetic restyle can substitute for a real workflow.

## Non-goals for the November 8 judged release
Five fake runnable Chambers, arbitrary external URLs, self-serve arbitrary agent adapters, paid accounts, broad multi-tenant production, universal red-team benchmark, automated exploit creation, SSH/network stress against real hosts, presenting scripted fixture as genuine model compromise.

## Release criteria
All WC01–WC09 verified with real integrated evidence, WC10 checked separately as submission gate. Remaining material gaps explicitly documented. Feature freeze must leave buffer for real video and LabLab entry.
