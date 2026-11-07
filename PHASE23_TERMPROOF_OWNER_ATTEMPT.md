# Phase 23 — Real TermProof founder-operated acceptance attempt

**Date:** 2026-11-07

## User-led steps completed
- User personally opened BlastLab, reviewed the five prefilled fields, and clicked Connect My Agent.
- Public BlastLab created campaign `22c0ae335edcddd84e5632fe9559fce4`.
- Status checked through the actual authenticated campaign UI: `awaiting_agent`, **0/6 cases**.
- Vultr GLM-5.3 generated the attack plan; this is a real campaign, not a fixture.
- Join token expires **2026-11-07T03:36:37Z** (short-lived). User-only recovery receipt expires **2026-12-07T03:06:42Z**, but recovery is for completed reports only. **No token or recovery key is stored in this document.**

## The real external agent and blocker
- Agent: TermProof, https://github.com/ShalyX/termproof, owned by the same founder as BlastLab.
- TermProof is an LLM-planned milestone verifier with deterministic acceptance policy and read-only GitHub/HTTPS/npm/EVM evidence adapters.
- Live production `POST https://termproof-mauve.vercel.app/api/verify` with a harmless public-source milestone returned **HTTP 503 `PERSISTENCE_UNAVAILABLE`**, **before actual Gemini/DeepSeek planning or verification**.
- The documented August immutable deployment and currently active Vercel deployment also returned the same 503; this is not a BlastLab connector failure.
- Vercel metadata shows `GEMINI_API_KEY`, `DEEPSEEK_API_KEY`, `TERMPROOF_DATABASE_URL` target production; does **not** prove the PostgreSQL connection is healthy. Vercel runtime log confirmed `PersistenceError/PERSISTENCE_UNAVAILABLE`.
- Actual underlying database/network/schema cause has **not** been independently established.
- Original local TermProof git checkout exists at `C:\Users\USER\Documents\Codex\2026-08-22\use-this-prompt-act-as-a\work\termproof` (commit cb2d4e2, installed packages), but no local Gemini/DeepSeek environment keys exist. The original Vercel runtime is therefore the correct connector target; do not substitute a fixture.

## Honest connector implementation
- `examples/termproof_live_agent.py`: Calls TermProof's real production HTTP verifier per untrusted BlastLab case, with the original public repository proof obligation. Requires genuine provider/model provenance and actual deterministic verdict, collects actual evidence adapter calls. If TermProof is unavailable, it throws and **submits no fabricated answer**.
- `web/run-termproof-owner-agent.cjs`: First preflights real TermProof; only on PASS reads one-time BlastLab join token from the original Chrome session **in process memory** and starts the real Python connector with token via subprocess env; no credentials are printed or committed.
- Tested `python -m py_compile`, `node --check`, and `node run-termproof-owner-agent.cjs --preflight-only`. Preflight **SAFE_ABORT** on HTTP 503, and no BlastLab cases submitted.
- Current campaign remains 0/6 after preflight.

## Required next work
1. Restore TermProof production PostgreSQL/Neon access without weakening its existing durable rate-limiter or verification semantics. Inspect the actual Neon project and the Vercel production `TERMPROOF_DATABASE_URL` connection, migrations and reachability. Never paste database passwords or model credentials in chat.
2. Verify that a genuine TermProof `POST /api/verify` responds 200 with real Gemini/DeepSeek planner provenance, claims, evidence, and deterministic verdict.
3. If the BlastLab join token expired, create a new campaign manually in the browser; a 30-day recovery key cannot extend the join token.
4. Run `node web/run-termproof-owner-agent.cjs` from BlastLab project root, under the same active Chrome user profile. Preserve original TermProof semantics.
5. Inspect six real model-driven case reports, exact plan hash, observed tool actions; fix and retest only if real violations were found.

**Gate integrity:** founder-operated acceptance in progress but **NOT PASS**. Independent outside-developer acceptance remains a separate unmet requirement.

## Resolution ? 2026-11-07: real TermProof completed in BlastLab

Neon/PostgreSQL was restored by the user. The production API subsequently returned a real Gemini 2.5 Flash plan, one bounded GitHub evidence result and a deterministic TermProof `VERIFIED` verdict for the legitimate single-condition task `Public repository exists`.

**Original campaign** `22c0ae335edcddd84e5632fe9559fce4`: all six real runner cases completed, 0 observed forbidden-tool violations, report manifest `99b4b84a8a826d41d174e928aa21ff5d16eba376cce71d6b785ad7cc2dde48db`. However **all six original TermProof verdicts were NEEDS_EVIDENCE**, including the clean control. Cause: the bridge appended lower-trust attack strings to the milestone text, contaminating the original acceptance condition. This was an integration/test design flaw; the result is preserved, not rewritten.

**Corrected bridge:** `examples/termproof_live_agent.py` now preserves the original exact milestone and places the adversarial payload in the **untrusted GitHub repository URL fragment**. TermProof independently parses the same fixed GitHub owner/repo from its valid URL path, while its unchanged Gemini planner receives the raw untrusted repository input separately. No TermProof source code, system prompt, allowed adapters, or verdict policies were changed. A real standalone control first returned TermProof `VERIFIED` with `github` evidence.

**Exact retest** `e5530b43aec6d3f4d446fd9fe411c392`: new campaign created through BlastLab's real **Import report ? Replay original attacks** browser flow, preserving attack plan SHA-256 `abf18ceceb0d6323c47d4a646ba67e1bce13648a91e6e0691ecb86cdb389420f` and all six attack cases. An outbound connector on the founder's authorized Windows PC called the original TermProof production API six times, receiving genuine Gemini plans, GitHub evidence and deterministic TermProof `VERIFIED` verdicts in **all 6/6**. Only the permitted `github` adapter was observed in all six; configured forbidden-tool violations were **0**. Report manifest `09d21a114653fabe65326d697a5ca3b6b3acdc3c53b154ec507a841fb1208921`.

Independent local verification called `agent_lab.verify_report` on **both** reports and `agent_lab.verify_import({'report': original, 'current': retest})`: all passed; plan hash identical. Original and retest JSON plus browser evidence are stored under ignored local `artifacts/phase23-termproof-founder/`. The retest's one-time private recovery receipt was saved locally and must NEVER be committed, printed or shared.

**Interpretation:** genuine founder-assisted/owner-agent integration and actual task-success acceptance PASS: **0/6 ? 6/6 legitimate tasks verified** after correcting the bridge's trust separation, **0 ? 0 forbidden tool violations**. This is **not** a demonstrated TermProof model vulnerability repaired; the changed component was the BlastLab-side connector. The source type is runner-reported, not independently VM-attested. As the same founder owns both apps, this does not satisfy the strictly independent outside-customer adoption/attestation gate. That remaining P0-01 condition remains OPEN.

**Operator:** Phase 23 BUILD_LOOP remains OPEN, Phase 24 PROOF_ENGINE BLOCKED for the other product P0 gaps and outside-customer acceptance. No silent phase promotion.
