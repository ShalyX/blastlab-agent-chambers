"""Use real TermProof production planner + verifier as a BlastLab user-owned agent.

Real agent source: https://github.com/ShalyX/termproof (unchanged).
This adapter invokes TermProof's real /api/verify endpoint and reports only
actual returned verdicts, claims and adapter observations. It never creates
substitute model output. If the original runtime is unavailable, fail CLOSED,
so the BlastLab campaign cursor is not advanced with fabricated evidence.
"""
from __future__ import annotations
import json
import os
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

TERMPROOF_URL = "https://termproof-mauve.vercel.app/api/verify"
MILESTONE = "Public repository exists"
REPO = "https://github.com/ShalyX/termproof"
MAX_RESPONSE_BYTES = 1024 * 1024
VERDICTS = {"VERIFIED", "PARTIALLY_VERIFIED", "NEEDS_EVIDENCE", "FAILED"}

class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise RuntimeError("TermProof redirected unexpectedly")

def respond(case: dict) -> dict:
    if not isinstance(case, dict):
        raise TypeError("BlastLab case must be a dictionary")
    attack = case.get("untrusted_input")
    if not isinstance(attack, str) or len(attack) > 9500:
        raise ValueError("Invalid untrusted attack input")
    # Preserve the legitimate acceptance condition exactly. The model also
    # receives the untrusted repository data in plannerDataPrompt. Only the
    # first two URL path segments anchor the actual GitHub repository.
    milestone = MILESTONE
    repo_input = (
        REPO + "#UNTRUSTED_REPOSITORY_CONTEXT_NOT_ACCEPTANCE_CONDITIONS:\n"
        + "<source-note>\n" + attack + "\n</source-note>"
    )
    if len(repo_input) > 12000:
        raise ValueError("Untrusted repository context exceeds permitted size")
    body = json.dumps({"milestone": milestone, "githubRepository": repo_input}).encode("utf-8")
    request = Request(
        TERMPROOF_URL, data=body, method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json",
                 "User-Agent": "BlastLab-TermProof-Owned-Agent-Acceptance/1.0"},
    )
    try:
        with build_opener(NoRedirects()).open(request, timeout=115) as response:
            if response.status != 200:
                raise RuntimeError(f"TermProof returned HTTP {response.status}")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise RuntimeError("TermProof evidence exceeded response bound")
            data = json.loads(raw)
    except HTTPError as exc:
        status = exc.code
        try:
            error = json.loads(exc.read(16000))
        except (ValueError, UnicodeError):
            error = {}
        raise RuntimeError(
            f"REAL_TERMPROOF_RUNTIME_UNAVAILABLE HTTP {status} "
            f"code={error.get('code', 'unknown')}. "
            "No BlastLab case was submitted."
        ) from None
    if not isinstance(data, dict):
        raise RuntimeError("TermProof returned a non-object response")
    verdict = data.get("verdict")
    provenance = data.get("provenance") or {}
    planner = provenance.get("planner") or {}
    claims = data.get("claims")
    evidence = data.get("evidence")
    if verdict not in VERDICTS or not isinstance(claims, list) or not isinstance(evidence, list):
        raise RuntimeError("TermProof did not return its actual structured verification")
    if not isinstance(planner, dict) or planner.get("provider") not in ("gemini", "deepseek"):
        raise RuntimeError("TermProof did not return real Gemini/DeepSeek planning provenance")
    if not planner.get("model"):
        raise RuntimeError("TermProof's model provenance is missing")
    executed_steps = []
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        for step in claim.get("steps", []):
            if not isinstance(step, dict):
                continue
            name = step.get("adapter")
            if name not in ("github", "http", "npm", "base"):
                raise RuntimeError("TermProof reported an unsupported adapter")
            if not isinstance(step.get("evidenceIds"), list) or not step["evidenceIds"]:
                raise RuntimeError("TermProof reported tool use without an evidence reference")
            executed_steps.append({
                "name": name,
                "arguments": {
                    "operation": str(step.get("operation", ""))[:70],
                    "result": str(step.get("result", ""))[:30],
                    "evidence_count": len(step["evidenceIds"])
                },
            })
    # This answer serializes actual policy, planner and adapter output.
    # 'milestoneVerdict' is a label, never a manufactured success claim.
    answer = (
        f"milestoneVerdict: {verdict}\n"
        f"TermProof actual model planner: {planner['provider']} / {planner['model']}\n"
        f"Independent deterministic verification claims: {len(claims)}\n"
        f"Observed read-only adapter evidence receipts: {len(evidence)}\n"
        f"Original promise: {MILESTONE}\n"
        f"TermProof original runtime returned: {verdict}"
    )
    return {"answer": answer, "tool_calls": executed_steps}

if __name__ == "__main__":
    print("Real TermProof production adapter ready. Call respond(case) from BlastLab.", flush=True)
