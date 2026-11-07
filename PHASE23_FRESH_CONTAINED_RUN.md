# Phase 23 — Fresh bounded Vultr sample: production acceptance

**Date:** 2026-11-07
**Operator stage:** BUILD_LOOP (Phase 23), still open for other unrelated P0s.
**Milestone:** Fresh fixed-sample worker launched from the public BlastLab UI **VERIFIED**.

## What shipped

- `POST /api/contained-sample/jobs` accepts only the literal `{"mode":"fixed-project-sample"}` with a matching trusted Origin. **No caller-provided code, URL, model, task, tools, environment variables or credentials.**
- Daily budget persists in `/var/lib/blastlab/sample-jobs`: **one public run per UTC day, two owner runs per UTC day**, and at most one active job globally. A restart cannot reset daily spending or automatically repeat interrupted execution.
- `GET /api/contained-sample/jobs/{id}` returns safe persisted state and, after completion, a sanitized proof summary. `GET /api/contained-sample/latest` exposes the last fixed-sample status with no token/credential.
- Trusted host invokes the approved `experiments/byoa-containment/host_supervisor.py` with a cryptographically random fixed job ID. The VM owns and provisions the disposable Docker worker, the mounted Unix socket to the trusted inference proxy, and the final teardown.
- Separate `experiments/byoa-containment/verify_run.py` validates the new worker's recorded report, exact event counts, inference provenance, Docker boundaries, observed tool execution, denied actions, and teardown. It does not insist on the archived sample's historical action totals or predetermine a clean result.
- `/contained-sample` now has a real on-demand button, queued/running/verified/blocked state, and the truthful latest result **alongside** the independently verified archived sample.
- `/app` links to the independent external-agent tester protocol at `/connect/independent-tester.md`. That protocol cannot count as a completed customer test without actual external operation.
- Existing customer session API, campaign reports, Vultr credentials, older contained-worker archive and third-party PydanticAI evidence remain separate.

## Real public-interface acceptance — PASS

**User action:** clicked **RUN FIXED VULTR SAMPLE** on the deployed HTTPS page in a real Chrome browser, which returned `202`.
**Job:** `ae83cba9fe31bdf4435e40b806466d8b`.
**Vultr evidence:** a fresh Docker container `blastlab-byoa-p12-ae83cba9fe31` and dedicated worker inference socket were observed while active; the VM's new artifact path was `/var/lib/blastlab/experiments/byoa-containment-20261107T011008Z-ae83cba9`.

| Check | Observed |
|---|---|
| Submitted from public UI | PASS, HTTP 202 |
| Six case campaign | **6/6 completed** |
| Vultr model inference | **12 actual calls** |
| Harmless synthetic actions | **12 executed inside worker** |
| Forbidden actions | **10 denied** |
| Configured policy violations | **0 of 6 observed** |
| Independent host/evidence checks | **22/22 PASS** |
| Container absent after run | **YES** |
| Inference socket removed | **YES** |
| Network egress blocked | **YES** |
| Production Chrome desktop/mobile | **PASS**, no errors or 390px overflow |

Proof captured in `web/qa-public-fresh-worker/completed-public-job.json`, `live-queued.png`, `live-verified-desktop.png`, and `live-verified-mobile.png`. Test logic: `web/qa-public-fresh-worker.cjs`. Fresh evidence is **not** the original November 6 archived run; it has a different job ID, case event trace, and observed 10 denied actions (rather than the archive's 7).

## Security and regression

- Targeted `test_contained_sample_service`, `test_contained_sample_http` and Operator phase-gate suite: **33 tests passed**.
- Production negative probes: latest status 200; malicious Origin 403; arbitrary custom code in request 400; invalid job path 404.
- UI-only mocked contract test at desktop/mobile passed and was labeled **mock-only**. Its results are not used as evidence of real VM execution.
- Real Chrome public worker acceptance above independently establishes production action and teardown.
- The broad `python -m unittest -q` run under concurrent browser/build load reported 220 tests, 3 skips, 1 failure, 4 errors. They occurred in pre-existing Windows sandbox/HTTP resource/time-out tests, not the targeted contained-sample suite. The isolated legacy `test_blastlab_agent test_control_api` suite then **passed 30 tests (1 skipped)**. A fresh serial full-suite rerun subsequently PASSED 238 tests, 3 skipped, 0 failures; the isolated legacy sandbox/API rerun also PASSED 30 tests, 1 skipped. The first concurrent run failed under resource contention and remains documented.
- Production release `deploy/phase23_fresh_sample_publish.py` + LF-normalized installer completed with `PHASE23_FRESH_SAMPLE_RELEASE_VERIFIED`; health/latest checks passed, rollback backup at `/opt/blastlab/backups/20261107-phase23-fresh-sample`.

## Product integrity / remaining gaps

**P0-09:** VERIFIED for the explicit acceptance of first-party Vultr inference and real bounded contained **project-owned judge sample** execution, through the deployed product, including independent host teardown verification. This does **not** imply the owner's arbitrary external agent was run on BlastLab's VM.

**P0-01:** still PARTIAL. Third-party *framework* interoperability passes (PydanticAI), but no demonstrably independently authored-and-operated outside customer's agent has yet been connected and evidenced. A third party must actually run their existing agent and provide the six-case report plus source/operation provenance. The new public tester protocol explains precisely how; a protocol is not a customer acceptance report.

Other locked P0 rows (account-based history/retention, source identity attestation, comprehensive accessibility, attack-surface inventory) remain separately gated. **Phase 23 BUILD_LOOP remains OPEN and Phase 24 PROOF_ENGINE remains BLOCKED** until the full locked product acceptance requirements are genuinely met.


## Final production UI hygiene check

- UI-only polish shipped with a new rollback backup: archived-November-6 record and fresh-November-7 run are explicitly distinguished.
- The PydanticAI 0-to-0 comparison arrow is rendered as an SVG icon; no unsupported claims of improvement.
- A freshly verified job exposes all six actual case verdicts plus its manifest and downloadable summary, without exposing its owner token or model credentials.
- \`node web/qa-public-fresh-readonly.cjs\`: public HTTPS PASS at 1440px and 390px, six fresh case rows, 22 independent checks, 10 denied actions, exact downloaded summary manifest, no JS errors or overflow.
- Final release \`deploy/phase23_fresh_ui_polish_publish.py\` returned \`FRESH_UI_POLISH_RELEASE_PASS\`. No backend service or customer data changed in this UI-only step.
