"""Durable agent-onboarding + campaign endpoints behind the BlastLab controller.

No arbitrary callback URLs, no downloaded executable code, no user keys.
Developer-owned runner calls outbound and reports agent decisions (not VM attested).
"""
from __future__ import annotations
import json
import os
import secrets
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agent_lab import (
    ATTACKS, add_response, create_session, expired, next_case, report,
    valid_id, validate_request, verify_token,
)

DIR = Path(os.environ.get("BLASTLAB_AGENT_LAB_DIR", "/var/lib/blastlab/agent-lab"))
LOCK = threading.RLock()
MAX_CAMPAIGNS_PER_DAY = 12
MAX_ACTIVE_CAMPAIGNS = 5


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
            return json.load(f)
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


def new_campaign(payload: dict) -> tuple[int, dict]:
    try:
        config = validate_request(payload)
    except ValueError as exc:
        return 400, {"error": str(exc)}
    with LOCK:
        if _usage() >= MAX_CAMPAIGNS_PER_DAY:
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
        state, token = create_session(config)
        atomic_json(session_file(state["id"]), state)
        atomic_json(_daily_counter(), {"created": _usage() + 1})
    return 201, {
        "session_id": state["id"],
        "join_token": token,  # returned once, never stored in plaintext
        "expires_at": state["expires_at"],
        "cases_total": len(ATTACKS),
        "source_type": state["source_type"],
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
                "total": len(ATTACKS),
                "expires_at": state["expires_at"],
                "source_type": state["source_type"],
            }
        if operation == "next":
            case = next_case(state)
            if case is None:
                return 200, {"complete": True}
            return 200, {"complete": False, "case": case}
        if operation == "report":
            return 200, report(state)
        return 404, {"error": "Unknown campaign operation"}


def post_campaign(ident: str, bearer: str | None, data: Any) -> tuple[int, dict]:
    with LOCK:
        status, state = _get_authorized(ident, bearer)
        if status == 404:
            return 404, {"error": "Unknown campaign"}
        if status == 401:
            return 401, {"error": "Campaign token invalid or expired"}
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
            "total": len(ATTACKS),
            "next_available": state["status"] != "complete",
            "source_type": state["source_type"],
        }
