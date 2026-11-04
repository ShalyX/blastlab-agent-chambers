# BlastLab | Hackathon Operator checkpoint

Updated: 2026-11-04
Event: Vultr Agent Rush (November 3â€“8, 2026). Verify exact submission cutoff in the event dashboard.
Current phase: **BUILD_VERTICAL_SLICE / judge-facing productization**, following PASSED technical de-risking.
Chosen technical thesis: crash-test browser agents reading hostile content; enforce a capability policy; destroy an isolated worker; restore checkpoint; complete the legitimate mission. The working candidate is called BlastLab; product naming and brand are **not** finalized.

## Verified live infrastructure (not a proposal)

- Vultr Cloud Compute instance `2db5a222-bd1f-42ea-acba-cc09a247a40c`, active in Amsterdam (`ams`), `vc2-2c-4gb` (2 vCPU, 4 GB), Ubuntu 24.04, public IP `45.77.138.147`.
- Docker 29.1.3 installed; immutable local image `blastlab-browser:spike` built from root `Dockerfile.sandbox`.
- VM project at `/opt/blastlab`; private inference settings at root-owned mode-0600 `/etc/blastlab/inference.env`. Cloud-management key stays off VM. No UI endpoint is published.
- Linux VM reached with dedicated key from Windows `~/.ssh/blastlab_vultr_2026`.
- Browser worker cleanup fixed and tested: verify absence from Docker daemon's container list; no brittle stderr parsing.

## Verified proof on 2026-11-04

1. **Real model end-to-end:** Vultr `glm-5.3` performed 3 actual inference rounds against hostile supplier content in Docker, 2 browser reads, distinct worker destroy/recreate, correct `$72` valuation, 41 chained trace events, 11.7 seconds, success true. The LLM did not attempt a forbidden action (0 denials).
2. **Scripted hostile-action control:** deterministic attack planner exercised 4 blocked actions inside the same Vultr Docker boundary and still completed the `$72` mission after reset; 65 chained events. This is not falsely presented as LLM-chosen attack behavior.
3. **Independent verification:** `artifacts/vultr-vm-20261104/proof-audit.json` reports both trace chains intact, no inference key leaked, full Docker cleanup, source/container restrictions, and an active matching Vultr control-plane instance. See `EVIDENCE.md`.
4. **VM targeted tests:** 10 policy/inference tests pass; 1 opted-in Docker browser test passes. Full VM unit suite is not green because host-only Node/browser fixture dependencies were not provisioned. Post-patch Windows regression suite also passed: 63 total tests, 3 skips, 0 failures.

## Remaining highest-value work

1. **P0 Product surface:** build a real judge-facing UX showing mission, injected page excerpt, proposed tool calls, policy decisions, kill/reset, evidence and resume. Distinguish real GLM model decisions from fixture attack calls, visibly.
2. **P0 Public deploy:** expose the controller through a hardened API/service and deploy the UI to a public URL; keep private inference key and privileged Docker daemon strictly server-side; no browser-to-Docker access.
3. **P0 Demo/video:** record real product walkthrough with visible Vultr model/VM and verified Docker kill-and-resume. No fake action feed or claims of 4 denials from the live LLM.
4. **P1 Reliability:** resolve optional local-host test dependencies on VM or clearly separate cloud-only CI; harden SSH/networking, make resource lifecycle deterministic, publish sanitized proof; enforce billing budget and stop VM after hackathon.
5. **P1 Operator gates:** product/name/brand lock, visual QA, Product Hygiene, judge simulation, submission requirements and cutoff verification.

## Status notes

The initial account block was solved by redeeming the `$200` hackathon credit via Vultr **Gift Codes** (not Coupon Codes). Initial local Chromium startup timeout, Docker image pull/build and Docker teardown-verification errors are now fixed. Technical de-risk proof is real; final product and submission are still **NOT READY**.

## 2026-11-04: full product control room deployed

- PUBLIC HTTPS: https://blastlab.45-77-138-147.sslip.io/ (Caddy on real Vultr VM, DNS/TLS externally verified).
- Genuine React/TypeScript product: landing, Control Room with real causal event timeline and injected web specimen, independent model/fixture source switch, policy/worker inspectors, Evidence vault/export and Architecture views, responsive mobile and reduction of motion.
- The public interface is read-only until a credentialed operator initiates a fixed test. Live and scripted owner-initiated tests both completed via /api/runs on actual Vultr backend, with fresh hash-chained proof published; NO client secrets or arbitrary commands.
- Gateway security tests 8/8 passed; full Python regression 71 tests, 0 failed, 3 intentional skips. Playwright interaction suite passed desktop/mobile workflows, no app JS page errors. Mobile 390px layouts have zero document overflow.
- Official build and product QA details: PRODUCT.md, BRAND.md, DESIGN.md, HYGIENE.md, SCORECARD.md, web/VISUAL_QA.md.
- OPEN FOR SUBMISSION: public GitHub remote/repository missing; final judge demo video and receipt still missing. Current SSLip domain works but is not permanent branded domain. Vultr VM billable while running.
- NEXT ACTION: polish demo script, record real browser/UI + model/fixture distinction, publish public source repository after secret audit, submit before verified November 8 cutoff.

## 2026-11-05 - Product drift detected (audit only)
Operator Product Critic verdict MODIFY; the original agent crash-testing facility architecture, including proposed Chambers, was narrowed to one fixed supplier replay in PRODUCT.md. Five Chambers were suggested, not individually locked release requirements. See PRODUCT_DRIFT_AUDIT.md for 20 findings, exact source files and an evidence-preserving repair sequence. Technical Vultr/GLM/Docker proof remains valid for its narrow scenario; the full product/hygiene/demo gates are reopened. No runtime, frontend or deployed infrastructure was changed during this audit. Next action: reconcile/lock the real Web Chamber user journey before further design/demo work.
