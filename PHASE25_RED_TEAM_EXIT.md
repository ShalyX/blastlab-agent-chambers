# BlastLab / Phase 25 RED_TEAM exit audit

Date: 7 November 2026
Product: Real bring-your-own-agent adversarial testing
Scope: API, auth, storage, reported runner events, exact replay, quotas, hostile case rendering, and public Vultr service.

## Red Team findings fixed

R25-01 / HTTP handler crash on malformed tool policy

The request validator computed set(forbidden_tools) and set(allowed_tools) before checking member types. A JSON object or nested array caused an unhandled TypeError; local HTTP clients observed a dropped connection. The fix checks the string/type pattern first, then set uniqueness.

Production release changed exactly those two conditions. An exact pre-deployment SHA check, preserved source backup, Python compilation, restart and API health checks passed. Two live malformed POST requests now returned HTTP 400.

Sources: agent_lab.py; test_phase25_redteam.py; deploy/phase25_policy_install.sh; deploy/phase25_policy_publish.py.
Live backup: /opt/blastlab/backups/20261107-phase25-policy-validation/agent_lab.py.

R25-02 / Long hostile runner text overflowed the findings panel

The React report correctly escaped HTML/script input, but intentionally unbroken hostile strings in an agent response, observations and mitigation copy overflowed the viewport. Reproduced using a real six-case report with synthetic hostile replacement text, not a genuine provider incident.

Display-only CSS wrapping fixed the issue. The production bundle was built and deployed with rollback. Local AND production-hosted desktop/mobile browser QA passed at 1440px and 390px: six findings rendered, zero injected DOM scripts, zero external attacker requests, zero page errors and zero horizontal overflow.

Sources: web/src/agent-lab.css, web/qa-phase25-redteam.cjs, web/qa-phase25-public.cjs, deploy/phase25_hostile_ui_publish.py, deploy/phase25_hostile_ui_install.sh.
Production rollback: /opt/blastlab/backups/20261107-phase25-hostile-ui.

## Attack matrix / actual observations

| Risk | Observation |
|---|---|
| Malformed campaign policies | Invalid arrays, objects, nulls and unsupported code/endpoint fields rejected with validation errors, rather than a dropped connection |
| Quota concurrency | 20 parallel local fixture campaigns permitted exactly the configured five active sessions; rejected the other fifteen with HTTP 429; unique session tokens, durable counter |
| Daily quota | Exhausted limit returned HTTP 429 and did not call the planner |
| Provider failure | Mocked upstream inference failure produced HTTP 503, no session allocation, no quota consumption or exposed token |
| Cross-campaign authorization | Wrong join token, recovery key and attempt to read/write another campaign rejected with HTTP 401 |
| Recovery separation | Expired connector token cannot report, but the separate read-only recovery key retrieves only a completed report and cannot post or fetch attacks |
| Case integrity | Duplicate, wrong-order and post-completion responses rejected; expected cursor unchanged on invalid submissions |
| Forged adapter metadata | Extra source/VM attestation claims, extra executed fields, invalid names, malformed arguments and excess tool calls rejected |
| Malformed HTTP body | Deep JSON rejected with HTTP 400; oversized request rejected with HTTP 413; invalid cross-origin creation rejected with HTTP 403 |
| Exact replay and reports | Tampered plan hashes, verdicts, event order, agent/task name and other evidence fields failed validation or replay |
| Reported execution | An authorized runner could submit an untrue tool proposal and have it preserved as reported. This remains EXTERNAL_AGENT_RUNNER_REPORTED, not independent VM attestation |
| Hostile frontend | XSS-shaped HTML/SVG/script payloads appeared only as text; no outbound attacker traffic, scripting, crash or desktop/mobile overflow |

No local test attempted unauthorized real-world access, executed malicious tools, or spent public Vultr model credits. The quota tests used the deterministic fake planner and isolated temporary campaign storage.

## Verification and release record

- Earlier targeted security and operator transition test batch: 29 PASS.
- Expanded adversarial backend/HTTP fixture run: 29 PASS.
- Full original regression plus added Phase25 tests: **295 executable tests passed, 3 skipped, zero failures** across 20 runnable modules, each in an isolated Python process. Original test assertions unchanged.
- TypeScript/Vite build: PASS.
- Production API after targeted validation patch: PASS health + malformed JSON POSTs HTTP 400.
- Production static bundle after hostile text CSS patch: PASS public proof index and API health checks.
- Production browser hostile-report QA: PASS desktop and mobile.

## Remaining boundaries / acceptance policy

The external agent runner is not signed or VM-attested. Unsigned SHA-256 manifests prove that a given report is internally consistent, not the historical identity of its producer. A malicious runner can invent a reported action; the product must never claim to have independently observed actual customer-side side effects. The first-party Vultr contained sample is a separate host-observed proof and does not host customer-submitted code.

The independent outside-developer acceptance test is explicitly deferred by the founder but still OPEN under PHASE24_OWNER_DEFERRAL.md. Submission Audit must refuse advancement until real outside-operated evidence is present; the deferral is not a PASS.

Do not claim universal protection, signed third-party provenance, full account-wide history/purge, guaranteed distributed quota resilience, or completed formal accessibility checks.

Exit decision: **PHASE25 RED_TEAM PASS**, with two verified production repairs and scoped external-runner limitations. Advance only to the adjacent Phase26 PRODUCT_HYGIENE; subsequent phase gates remain independent.


## Final signed-off engineering acceptance — 2026-11-07

- Full isolated Python regression: 295 executed test cases, 3 documented skips, zero failed modules; the 2 zero-test support fixtures are excluded. Source summary: PHASE25_REGRESSION_SUMMARY.json.
- Separate hostile browser QA: 1440 and 390 passed against **locally built** UI and **live production-served** UI, with zero execution, external traffic or horizontal overflow. Screenshots were retained locally for operator inspection; malicious samples are synthetic.
- Prior original Phase24 production proof page retained intact with unchanged evidence SHA-256 after the CSS release.
- Two confirmed Red Team defects were fixed, and the production service/UI checks passed. No open reproducible high-severity vulnerability was observed within this **bounded** attack matrix.
- Limitations remain: external owner-run actions are runner reported; no source-signed attestation; independent outside developer not verified; no promise of universal attack coverage or large-scale multi-process DDoS protection.
- RED_TEAM PASS means reviewed scoped security surfaces are fit to enter Product Hygiene. It is not production penetration-test certification or submission approval.
