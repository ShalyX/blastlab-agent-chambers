# BlastLab | Operator checkpoint

Updated: 2026-11-04
Phase: TECHNICAL_DERISK
Goal: PROVE real-model browser-agent execution plus isolated disposable container on a genuine Vultr VM.
Candidate thesis: crash-test autonomous agents against hostile web content, enforce tool boundaries, recover, and still complete the user's legitimate mission.
Scope: supplier stock-valuation mission, hostile supplier note, denied actions, browser worker teardown, new worker, fresh read, verified $72 result.
Decision: BlastLab leading candidate; Repro preserved as alternative. No final product or brand lock.

## Verified local facts
- 2026-11-04: `python -W error -m unittest -q` reports 63 tests, 3 skipped, zero failures (60 passed).
- 2026-11-04: `python agent_spike.py run --provider deterministic --sandbox local` exits with `acceptance_passed=true`: mission $72, reset verified, 4 denied action attempts, 2 browser reads, 65 trace events, supervisor sentinel unchanged.
- Local Chromium activity and process/workspace reset observed. Planner deterministic/simulated. Local process NOT a security container.

## Blocked external gates
1. Obtain Vultr Serverless Inference subscription key and exact enabled tool-capable model ID. Store in secure VM env or ignored `.env.vultr`; never in code or chat.
2. Supply/provision authorized Vultr Linux VM and access details, verify its instance ID and region.
3. Install Docker on VM. Build sandbox image and run deterministic container test there.
4. Run genuine Vultr inference + Docker mission, retain model/tool transcript, Docker lifecycle logs and source hashes. Only then mark live gate PROVEN.
5. Develop public product URL, judge UX, production architecture, recorded proof, hygiene and submission.

## Current blocker
`agent_spike.py doctor` on Windows: inference key/model false, VM host/user/SSH key false, Docker unavailable. Do NOT claim live Vultr or real-model success.
Next action: user provisions/authorizes Vultr inference subscription and VM, then rerun `python agent_spike.py doctor --env-file .env.vultr` where supported; follow BROWSER_SPIKE.md for VM deployment. Verify CLI options before running.

## Update 2026-11-04: Vultr activation unblocked
- User confirmed $200 hackathon credit redemption worked through Vultr **Gift Codes** (not coupon codes).
- Authenticated Vultr browser page shows active Serverless Inference subscription labelled "Hack" with $0.00 charges. This is OBSERVED SUBSCRIPTION STATUS only, not evidence of API inference.
- Local inference key and model have not yet been configured; VM and Docker cloud runtime remain unverified.
- Next action: retrieve subscription API key securely from Vultr manage page; select exact enabled tool-capable model; configure ignored .env.vultr and run doctor, then provision VM/Docker and live model test.

## 2026-11-04 inference configuration update
Private, gitignored `.env.vultr` is now configured with Hack subscription key and `glm-5.3`; doctor reported inference_ready=true. A real API request to Vultr returned HTTP 200 with exact model `glm-5.3` and a `ping` function tool call (197 tokens); key not logged. Full local model-driven browser mission attempted but failed due to a local browser sandbox timeout before reaching inference. Next: repair worker startup, then run complete real-model mission; VM/Docker proof still pending.
