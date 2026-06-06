"""storage.py – read/write session data to ~/.studylog/sessions.json"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

DATA_DIR = Path.home() / ".studylog"
SESSIONS_FILE = DATA_DIR / "sessions.json"
ACTIVE_FILE = DATA_DIR / "active.json"  # written when a session is in progress


def _ensure_dir() -> None:
    DATA_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

def load_sessions() -> list[dict[str, Any]]:
    _ensure_dir()
    if not SESSIONS_FILE.exists():
        return []
    with SESSIONS_FILE.open() as f:
        return json.load(f)


def save_session(session: dict[str, Any]) -> None:
    _ensure_dir()
    sessions = load_sessions()
    sessions.append(session)
    with SESSIONS_FILE.open("w") as f:
        json.dump(sessions, f, indent=2)


def new_session(subject: str) -> dict[str, Any]:
    return {
        "id": str(uuid.uuid4()),
        "subject": subject,
        "start": datetime.now().isoformat(),
        "end": None,
        "duration_seconds": 0,
        "app_usage": {},
    }


# ---------------------------------------------------------------------------
# Active session (persisted so tracker can be interrupted and resumed)
# ---------------------------------------------------------------------------

def write_active(session: dict[str, Any]) -> None:
    _ensure_dir()
    with ACTIVE_FILE.open("w") as f:
        json.dump(session, f, indent=2)


def read_active() -> dict[str, Any] | None:
    _ensure_dir()
    if not ACTIVE_FILE.exists():
        return None
    with ACTIVE_FILE.open() as f:
        return json.load(f)


def clear_active() -> None:
    if ACTIVE_FILE.exists():
        ACTIVE_FILE.unlink()
