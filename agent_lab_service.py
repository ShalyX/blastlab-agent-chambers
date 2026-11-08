"""Durable agent-onboarding + campaign endpoints behind the BlastLab controller.

No arbitrary callback URLs, no downloaded executable code, no user keys.
Developer-owned runner calls outbound and reports agent decisions (not VM attested).
"""
from __future__ import annotations
import json
import hashlib
import hmac
import re
import os
import secrets
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from agent_lab import (
    ATTACKS, add_response, create_session, expired, next_case, report,
    valid_id, validate_request, verify_token, ensure_attack_plan, digest,
    replay_session,
)
from agent_lab_attacks import generate_vultr_attack_plan

DIR = Path(os.environ.get("BLASTLAB_AGENT_LAB_DIR", "/var/lib/blastlab/agent-lab"))
LOCK = threading.RLock()
MAX_CAMPAIGNS_PER_DAY = 12
MAX_OWNER_CAMPAIGNS_PER_DAY = 8
MAX_ACTIVE_CAMPAIGNS = 5
RECOVERY_DAYS = 30
RECOVERY_KEY_PATTERN = re.compile(r"^[A-Za-z0-9_-]{32,80}$")


def atomic_json(path: Path, item: Any):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    content = json.dumps(item, ensure_ascii=False, separators=(",", ":"))
    tmp = path.with_name("." + secrets.token_hex(12) + ".tmp")
    try:
        with tmp.open("x", encoding="utf-8") as f:
            f.write(content + "\n")
        os.chmod(tmp, 0o600)
        tmp.replace(path)
    finally:
        if tmp.exists():
            tmp.unlink()


def session_file(ident: str) -> Path:
    if not valid_id(ident):
        raise ValueError("Invalid session identifier")
    return DIR / (ident + ".json")


def _read_session(ident: str) -> dict:
    try:
        with session_file(ident).open(encoding="utf-8") as f:
            state = json.load(f)
        ensure_attack_plan(state)
        return state
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        raise KeyError("Unknown session") from None


def _daily_counter() -> Path:
    return DIR / ("created-" + datetime.now(timezone.utc).strftime("%Y%m%d") + ".json")


def _usage() -> int:
    try:
        with _daily_counter().open(encoding="utf-8") as f:
            return max(0, int(json.load(f)["created"]))
    except (FileNotFoundError, OSError, ValueError, TypeError, KeyError):
        return 0


def _owner_daily_counter() -> Path:
    return DIR / ("created-owner-" + datetime.now(timezone.utc).strftime("%Y%m%d") + ".json")


def _owner_usage() -> int:
    try:
        with _owner_daily_counter().open(encoding="utf-8") as f:
            return max(0, int(json.load(f)["created"]))
    except (FileNotFoundError, OSError, ValueError, TypeError, KeyError):
        return 0


def new_campaign(payload: dict, *, owner: bool = False) -> tuple[int, dict]:
    try:
        if not isinstance(payload, dict):
            raise ValueError('Invalid campaign request')
        config = validate_request({k: v for k, v in payload.items() if k != 'baseline_report'})
        replay = replay_session(config, payload['baseline_report']) if 'baseline_report' in payload else None
    except ValueError as exc:
        return 400, {"error": str(exc)}
    with LOCK:
        # The trusted controller authenticates the operator token before
        # passing owner=True. Public calls retain the original strict quota.
        if owner:
            if _owner_usage() >= MAX_OWNER_CAMPAIGNS_PER_DAY:
                return 429, {"error": "Daily owner agent test allocation exhausted"}
        elif _usage() >= MAX_CAMPAIGNS_PER_DAY:
            return 429, {"error": "Daily public agent test allocation exhausted"}
        active = 0
        for item in DIR.glob("[0-9a-f]" * 32 + ".json") if DIR.exists() else []:
            try:
                with item.open(encoding="utf-8") as f:
                    state = json.load(f)
                if state.get("status") != "complete" and not expired(state):
                    active += 1
            except Exception:
                continue
        if active >= MAX_ACTIVE_CAMPAIGNS:
            return 429, {"error": "Active campaign capacity reached"}
        state, token = replay if replay is not None else create_session(config)
        try:
            # Public campaigns must use the real Vultr planner. No silent switch
            # to the deterministic unit-test fixture when inference is unavailable.
            plan = state['attack_plan'] if replay is not None else generate_vultr_attack_plan(config, state["canary"])
            if (not isinstance(plan, dict)
                    or plan.get("source") != "VULTR_LLM_GENERATED"
                    or plan.get("sha256") != digest({k:v for k,v in plan.items() if k != "sha256"})):
                raise RuntimeError("Invalid Vultr attack plan")
            state["attack_plan"] = plan
        except Exception as exc:
            # Log only the exception class: provider bodies, prompts and credentials stay private.
            print(json.dumps({"event": "adaptive_attack_plan_failed",
                              "error_type": type(exc).__name__}), flush=True)
            return 503, {
                "error": "Vultr adaptive attack planning is unavailable. No scripted fallback was used; try again later."
            }
        # Separate capability: report retrieval only, never agent execution.
        # Generate after planner success. Store a digest, not the bearer key.
        recovery_key = secrets.token_urlsafe(32)
        recovery_expires_at = (datetime.now(timezone.utc) + timedelta(days=RECOVERY_DAYS)).isoformat()
        state["recovery_key_sha256"] = hashlib.sha256(recovery_key.encode("ascii")).hexdigest()
        state["recovery_expires_at"] = recovery_expires_at
        atomic_json(session_file(state["id"]), state)
        if owner:
            atomic_json(_owner_daily_counter(), {"created": _owner_usage() + 1})
        else:
            atomic_json(_daily_counter(), {"created": _usage() + 1})
    return 201, {
        "session_id": state["id"],
        "join_token": token,  # returned once, never stored in plaintext
        "recovery_key": recovery_key,  # returned once, never stored in plaintext
        "recovery_expires_at": recovery_expires_at,
        "expires_at": state["expires_at"],
        "cases_total": len(state["attack_plan"]["attacks"]),
        "attack_source": state["attack_plan"]["source"],
        "attack_provider": state["attack_plan"]["provider"],
        "attack_model": state["attack_plan"]["model"],
        "attack_plan_sha256": state["attack_plan"]["sha256"],
        "source_type": state["source_type"],
        "execution_mode": state['config'].get('execution_mode', 'external'),
        **({key: state['config'][key] for key in ('chamber', 'web_mission')} if state['config'].get('chamber') == 'web' else {}),
        "connector": "/connect/blastlab_connector.py",
    }


def _get_authorized(ident: str, bearer: str | None) -> tuple[int, dict | None]:
    try:
        state = _read_session(ident)
    except (KeyError, ValueError):
        return 404, None
    if not bearer or not bearer.startswith("Bearer ") or not verify_token(state, bearer[7:].strip()):
        return 401, None
    return 200, state


def get_campaign(ident: str, bearer: str | None, operation: str) -> tuple[int, dict]:
    with LOCK:
        status, state = _get_authorized(ident, bearer)
        if status == 404:
            return 404, {"error": "Unknown campaign"}
        if status == 401:
            return 401, {"error": "Campaign token invalid or expired"}
        if operation == "status":
            return 200, {
                "session_id": ident,
                "agent_name": state["config"]["agent_name"],
                "status": state["status"],
                "completed": state["case_cursor"],
                "total": len(state["attack_plan"]["attacks"]),
                "expires_at": state["expires_at"],
                "source_type": state["source_type"],
                "execution_mode": state['config'].get('execution_mode', 'external'),
                "execution_state": state.get('execution_state', 'awaiting_source'),
                "execution_error": state.get('execution_error'),
            }
        if operation == "next":
            if state['config'].get('execution_mode') == 'vultr_sandbox':
                return 409, {'error': 'Hosted campaigns accept source bundles, not external runners'}
            case = next_case(state)
            if case is None:
                return 200, {"complete": True}
            return 200, {"complete": False, "case": case}
        if operation == "report":
            if state['config'].get('execution_mode') == 'vultr_sandbox' and state.get('execution_state') != 'verified':
                return 409, {'error': 'Awaiting host verification and worker teardown'}
            return 200, report(state)
        return 404, {"error": "Unknown campaign operation"}


def get_recovery_report(ident: str, bearer: str | None) -> tuple[int, dict]:
    """Read-only campaign-scoped capability, distinct from short-lived connector auth."""
    with LOCK:
        try:
            state = _read_session(ident)
        except (KeyError, ValueError):
            return 404, {"error": "Campaign not found"}
        key = bearer[7:].strip() if isinstance(bearer, str) and bearer.startswith("Bearer ") else ""
        stored = state.get("recovery_key_sha256")
        deadline = state.get("recovery_expires_at")
        if (not RECOVERY_KEY_PATTERN.fullmatch(key) or
            not isinstance(stored, str) or len(stored) != 64 or
            not isinstance(deadline, str)):
            return 401, {"error": "Recovery key invalid or expired"}
        try:
            valid_until = datetime.fromisoformat(deadline)
            active = valid_until.tzinfo is not None and datetime.now(timezone.utc) < valid_until
        except ValueError:
            active = False
        matched = hmac.compare_digest(
            hashlib.sha256(key.encode("ascii")).hexdigest(), stored
        )
        if not matched or not active:
            return 401, {"error": "Recovery key invalid or expired"}
        if state.get("status") != "complete":
            return 409, {"error": "Campaign must be completed before report recovery"}
        artifact = report(state)
        return 200, artifact


def post_campaign(ident: str, bearer: str | None, data: Any) -> tuple[int, dict]:
    with LOCK:
        status, state = _get_authorized(ident, bearer)
        if status == 404:
            return 404, {"error": "Unknown campaign"}
        if status == 401:
            return 401, {"error": "Campaign token invalid or expired"}
        if state['config'].get('execution_mode') == 'vultr_sandbox':
            return 409, {'error': 'Only the trusted Vultr supervisor can submit hosted campaign results'}
        try:
            result = add_response(state, data)
        except ValueError as exc:
            return 400, {"error": str(exc)}
        atomic_json(session_file(ident), state)
        return 200, {
            "accepted": True,
            "case_id": result["case_id"],
            "observed_verdict": result["verdict"],
            "completed": state["case_cursor"],
            "total": len(state["attack_plan"]["attacks"]),
            "next_available": state["status"] != "complete",
            "source_type": state["source_type"],
        }
