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
