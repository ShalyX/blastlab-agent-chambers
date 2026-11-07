# Phase 25 — Red Team opening audit and first repaired finding

Date: 2026-11-07
Phase: RED_TEAM (25 of 35)
Gate: OPEN — red-team review started, not complete
Product: BlastLab user-owned agent adversarial testing

## Owner-authorized transition from Phase 24

User instruction: "Move to next phase, we'd find exter dev later".

PHASE24_OWNER_DEFERRAL.md records consent to proceed without a completed independent outside-developer run. Phase 24 is marked CONDITIONAL_DEFERRED, NOT PASS. The missing genuinely independent operator is still mandatory before Submission Audit; its gate is enforced by deploy/phase_gate.py. External runner action reports are not signed third-party runtime attestations.

## Adversarial review matrix

| Surface | Tested abuse | Observation | Status |
|---|---|---|---|
| Public campaign policy | JSON object/list inside allowed_tools or forbidden_tools | Unhandled TypeError terminated a local HTTP request thread instead of HTTP 400 | FIXED in production |
| Public campaign policy | Unsupported callback endpoint, arbitrary code or owner flag | Input contract rejected unknown fields | PASS local |
| Origin | Cross-site policy creation | HTTP 403 | PASS local |
| Recovery token | Use recovery credential to read next case or post agent response | HTTP 401; incomplete recovery HTTP 409 | PASS local |
| Cross-campaign auth | Token from one campaign accesses another | HTTP 401 | PASS local |
| Oversized request body | Very large campaign JSON | HTTP 413 | PASS local |
| Nested tool arguments | Extremely deep tool-call arguments | Validation raises ValueError | PASS local |
| Verifiable reports | Alter saved verdict without adjusting event chain | Existing report verifier rejects corruption | PASS local |
| Agent side effects | Malicious external runner lying about executed tools | Remote actions are runner-reported, not independently attested | OPEN |
| Abuse at scale | Distributed compute quotas/concurrency, malicious adapters and forged runner action metadata | Existing limits present; adversarial validation incomplete | OPEN |
| UI attack content | Hostile/untrusted case rendering, Unicode and long content | Basic desktop/mobile checks exist; deep hostile-data QA pending | OPEN |

## Finding R25-01: malformed policy lists crash a request thread

BEFORE: agent_lab.validate_request computed set(forbidden_tools) and set(allowed) before checking individual members were legal strings. Valid JSON lists containing a dictionary or nested list caused TypeError; the isolated local HTTP client observed RemoteDisconnected, not HTTP 400.

FIX: Check each tool entry against the string/type pattern before set uniqueness; preserve existing campaign contract, inference flow and policy semantics.

TESTS: test_phase25_redteam.py covers forbidden/allowed type fuzz, real local HTTP 400, origin 403, session and recovery isolation, oversized body 413, nested tool bounds and changed report verdict rejection. Together with original Operator and deferral tests, 29 targeted tests PASS.

WIDER REGRESSION: Initial isolated 21-file sweep had 19 executable test modules and two zero-test support fixtures. 256 cases completed successfully and 3 skipped; one Phase25 local HTTP test hit the intermittent Windows WinError 10053 loopback transport error. The 10-case Phase25 module passed on a separate rerun. This is NOT described as one-pass 266-test green regression.

## Production correction / Nov 7

Original live agent_lab.py SHA-256: 363a688bd963e7c6330abc1e6ebad670d1b760cb465d48725a6a3d2f59e680d3. This differed from GitHub HEAD, so the original production module was preserved and patched surgically by deploy/phase25_policy_install.sh and deploy/phase25_policy_publish.py.

A backup was created at /opt/blastlab/backups/20261107-phase25-policy-validation/agent_lab.py. Preflight matched exact original hash. Patch matched both exact original conditions. Module compiled; BlastLab service restarted; API health passed. Two malformed policy POSTs returned HTTP 400 from the live controller. Installer reported PHASE25_MALFORMED_POLICY_PRODUCTION_HARDENING_VERIFIED; publisher reported PHASE25_POLICY_PRODUCTION_PASS. The two conditions were changed; other production source differences remain unreviewed.

## Remaining RED_TEAM exit scope

1. Test falsified or reordered external runner events and replay/manifest forgery under isolated campaign fixtures.
2. Verify active/concurrent quotas without exhausting paid Vultr compute or interrupting user runs.
3. Test the rendered report under attacker-supplied metadata, extreme Unicode and hostile textual content.
4. Review authentication origin and CSRF assumptions, ensure no secret disclosure, verify production/regressions.
5. Record the actual findings and successful fixes. Do not advance to Product Hygiene without Phase25 RED_TEAM exit PASS.

Status: RED_TEAM OPEN. Founder-authorized Phase24 deferral is not independent customer proof.
