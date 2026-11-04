# Evidence registry

Updated: 2026-11-04. All claims refer to the Windows development host, not a Vultr VM unless explicitly stated.

| Claim | Classification | Proof source / reproduction | Caveat |
|---|---|---|---|
| Unit/integration regression suite | OBSERVED | `python -W error -m unittest -q`: 63 tests, 3 skipped, 0 failures | Skips include optional Docker tests |
| Chromium browser consumed malicious supplier content | OBSERVED | `python agent_spike.py run --provider deterministic --sandbox local`, `artifacts/agent-run-*/trace.jsonl` | Planner is deterministic, not an LLM |
| Hostile action attempts blocked | OBSERVED in scripted scenario | Latest run: 4 denied; policy boundary and worker capability tests | Does not establish resilience against general model-generated attacks |
| Worker torn down and recreated; mission continues | OBSERVED locally | Latest run: 2 browser reads, reset verified, supervisor sentinel intact; 65 trace events | Local process sandbox, not OS isolation |
| Accurate mission output | OBSERVED locally | `total_value_cents=7200`, `acceptance_passed=true` | Controlled supplier inventory |
| Vultr API request shape | TESTED BY MOCK | `test_browser_agent.py`, `browser_inference.py` | No live Vultr request verified |
| Model-driven prompt injection response | UNPROVEN | Pending live enabled Vultr model + API key | Deterministic planner must not be reported as real model |
| Docker OS containment, caps, destruction | UNPROVEN | Dockerfile and static contract tests exist | Docker not installed on Windows; run on Vultr VM |
| Vultr VM hosting | BLOCKED | `agent_spike.py doctor` config flags false | No authenticated VM/instance verification |
| Public URL and submission video | NOT STARTED | Future deployment/recording proof | Required judge-facing deliverables |

Generated raw traces are local artifacts, not included in public Git by default. Do not turn synthetic proof into a live claim.

| Active Serverless Inference subscription | OBSERVED on 2026-11-04 | Authenticated Vultr Console Inference list: "Hack", active, charges $0.00 | Key/model not yet configured; no live request proof |

| Live Vultr model authentication and tool call | OBSERVED (2026-11-04) | `artifacts/vultr-inference-smoke.json`: HTTP 200, `glm-5.3` requested/returned, `ping` function called, 197 tokens | Minimal API call only; not a full browser mission; evidence is local and ignored by Git |
| Full Vultr model-driven browser-agent mission | BLOCKED / FAILED LOCAL ATTEMPT | `artifacts/agent-run-89vxler_/result.json`: local browser worker timed out before inference; 0 browser reads, 0 model responses | This does not invalidate live API authentication; browser sandbox needs debug; Docker/VM not configured |
