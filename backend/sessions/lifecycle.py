from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

# In-memory store for active sessions: {user_email: {home_id, login_time, last_activity}}
active_sessions: Dict[str, Dict[str, Any]] = {}

SESSION_TIMEOUT_MINUTES = 30

def start_session(user_id: str, home_id: str) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    active_sessions[user_id] = {
        "home_id": home_id,
        "login_time": now,
        "last_activity": now
    }
    return active_sessions[user_id]

def get_active_session(user_id: str) -> Optional[Dict[str, Any]]:
    cleanup_expired_sessions()
    session = active_sessions.get(user_id)
    if session:
        now = datetime.now(timezone.utc)
        if now - session["last_activity"] > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            end_session(user_id)
            return None
        # Update last activity to extend session
        session["last_activity"] = now
        return session
    return None

def update_session_home(user_id: str, new_home_id: str) -> Optional[Dict[str, Any]]:
    session = get_active_session(user_id)
    if session:
        session["home_id"] = new_home_id
        session["last_activity"] = datetime.now(timezone.utc)
        return session
    return None

def end_session(user_id: str) -> Optional[Dict[str, Any]]:
    session = active_sessions.get(user_id)
    if not session:
        return None

    now = datetime.now(timezone.utc)
    duration = now - session["login_time"]

    result = {
        "user_id": user_id,
        "home_id": session["home_id"],
        "login_time": session["login_time"],
        "logout_time": now,
        "duration_minutes": duration.total_seconds() / 60
    }

    del active_sessions[user_id]
    return result

def cleanup_expired_sessions():
    now = datetime.now(timezone.utc)
    expired_users = [
        user_id for user_id, session in active_sessions.items()
        if now - session["last_activity"] > timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    ]
    for user_id in expired_users:
        del active_sessions[user_id]
