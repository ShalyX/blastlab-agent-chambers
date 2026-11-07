# PHASE 23 — Recovery Milestone (partial BUILD_LOOP)
**Date:** 2026-11-07
**Status:** RECOVERY SLICE VERIFIED in production. **Phase 23 BUILD_LOOP remains OPEN.**

## What shipped
- Every **new** BYOA campaign now receives a separate cryptographically random 32-byte-equivalent read-only recovery capability (`recovery_key`) and expiry 30 days from creation.
- The recovery capability is shown for the initial creation session with COPY/SAVE RECOVERY RECEIPT controls. Only its SHA-256 digest and deadline are written to the existing atomic, permission-restricted session file. The plaintext recovery key is not stored in the server session or browser sessionStorage.
- `GET /api/agent-lab/sessions/{id}/recovery-report` requires `Authorization: Bearer <recovery_key>`, returns a completed session report only, and uses no-store responses. The key cannot be used to poll for cases, submit responses, or run agents. Expired or unknown keys fail closed. Old campaigns lacking a recovery key fail closed.
- Connect screen has an authenticated "Recover a completed report" section. Success supports Download Report and Use for Exact Retest. Recovery credential input is cleared after the request.
- Existing short-lived connector token and its permissions remain unchanged. No new account system or global customer history was introduced.
- Source touched: `agent_lab_service.py`, `control_api.py`, `web/src/App.tsx`, `web/src/AgentLabExperience.tsx`, `web/src/agent-lab.css`.

## Verified test evidence
- `python -m unittest -q test_phase23_recovery`: 23 tests, no failures. Tests include key not persisted in plaintext; expired connector access rejected; read-only cross-campaign failure; expired/missing capability rejection; completed-only access; full server-restart equivalent via separate interpreter reading the existing file; HTTP 401 vs 200 and no write authority.
- `python -m unittest -q`: 215 tests run, 3 skipped, 0 failures.
- `cd web && npm run build`: TypeScript and Vite production compilation passed.
- `node web/qa-phase23-recovery.cjs`: local browser + project-owned Python adapter, six real outbound case submissions; expire original connector token on disk; fresh mobile browser retrieves the original report with recovery key, downloads and verifies report manifest, begins same-plan exact retest and completes a second six-case connector run. Observed baseline 2 rule violations → retest 0. Identical plan hash, zero browser errors, no mobile overflow.
- Scoped production release via `deploy/phase23_recovery_publish.py` and `deploy/phase23_recovery_install.sh` passed. Only two backend modules and compiled HTML/CSS/JS published. VM installer saved original files in `/opt/blastlab/backups/20261107-phase23-recovery`, restarted API, and checked public HTML + API health. No stored run reports, keys, or connector sources replaced.
- `node web/qa-phase23-public.cjs`: **PUBLIC HTTPS PASS**. Created one real GLM/Vultr-planned six-case project-owned adapter campaign via production UI/API (201), received all six actual responses (one observed violation), fetched saved completed report with recovery key (200), confirmed recovery token rejected for status (401), confirmed execution token rejected for recovery (401), recovered and downloaded matching report in a fresh 390px Chrome browser, and loaded the exact retest form. No JavaScript errors or horizontal mobile overflow. Public test did NOT simulate actual connector expiry on production, since that would mutate user-facing data; separate local and unit tests covered expiry.

## Explicit limitations and next gates
1. This is **per-campaign bearer-key recovery**, not email-based login, account identity, shared org workspace or a cross-session history index. The key must be saved at creation; if lost it cannot be reissued. Existing older campaigns never received a recovery key and are not automatically recoverable through this endpoint.
2. After 30 days the recovery key expires, but no automatic data retention/purge policy was added. This requires a separate privacy/retention implementation before long-term production use.
3. Recovery key authenticates possession only; it does not attest to the runner's identity or any side effect. Reports remain explicitly runner-reported, and report integrity hashes are unsigned.
4. P0-07 improves materially but remains **PARTIAL** until user-facing authenticated multi-session history and lifecycle acceptance are complete. Do not close P0-01, P0-09, P0-10 or all of BUILD_LOOP on this slice.
5. Next implementation target: independent, externally authored customer-style BYOA agent integration through the public flow. Next critical architecture target: integrate the Vultr-contained project-owned judge sample path without suggesting owner-run arbitrary code is VM-contained.

**Milestone verdict: PASS — production recovery slice only. BUILD_LOOP gate stays OPEN; PROOF_ENGINE is still blocked.**
