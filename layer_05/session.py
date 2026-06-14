# layer_05/session.py
import os
import json
from datetime import datetime

SESSIONS_DIR = os.path.join(os.path.dirname(__file__), '..', 'sessions')

def _ensure_dir():
    os.makedirs(SESSIONS_DIR, exist_ok=True)

def session_path(session_id: str) -> str:
    return os.path.join(SESSIONS_DIR, f"{session_id}.json")

def save_session(session_id: str, messages: list[dict]) -> str:
    """Save messages to a JSON file. Returns the file path."""
    _ensure_dir()
    # Strip internal metadata keys before saving
    clean = [
        {k: v for k, v in m.items() if not k.startswith('_')}
        for m in messages
    ]
    data = {
        "session_id": session_id,
        "updated_at": datetime.utcnow().isoformat(),
        "messages": clean,
    }
    path = session_path(session_id)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    return path

def load_session(session_id: str) -> list[dict]:
    """Load messages from a session file."""
    path = session_path(session_id)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Session not found: {session_id}")
    with open(path) as f:
        data = json.load(f)
    return data["messages"]

def list_sessions() -> list[dict]:
    """Return all sessions sorted by most recent first."""
    _ensure_dir()
    sessions = []
    for fname in os.listdir(SESSIONS_DIR):
        if not fname.endswith('.json'):
            continue
        path = os.path.join(SESSIONS_DIR, fname)
        try:
            with open(path) as f:
                data = json.load(f)
            # Count only user messages for the summary
            user_msgs = [m for m in data["messages"] if m["role"] == "user"]
            first_msg = user_msgs[0]["content"][:60] if user_msgs else "(empty)"
            sessions.append({
                "session_id": data["session_id"],
                "updated_at": data["updated_at"],
                "message_count": len(user_msgs),
                "preview": first_msg,
            })
        except Exception:
            continue
    sessions.sort(key=lambda s: s["updated_at"], reverse=True)
    return sessions

def new_session_id() -> str:
    """Generate a timestamp-based session ID."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def delete_session(session_id: str) -> bool:
    path = session_path(session_id)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False