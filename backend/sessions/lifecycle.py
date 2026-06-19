from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from app.db.connection import SessionLocal
from app.db.models import UserSession

# In-memory store for active sessions: {user_email: {home_id, login_time, last_activity, db_session_id}}
active_sessions: Dict[str, Dict[str, Any]] = {}

SESSION_TIMEOUT_MINUTES = 30

def start_session(user_id: str, home_id: str) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    
    # Save session to Database
    db = SessionLocal()
    db_session_id = None
    try:
        db_sess = UserSession(
            user_email=user_id,
            login_time=now,
            last_activity=now
        )
        db.add(db_sess)
        db.commit()
        db.refresh(db_sess)
        db_session_id = db_sess.id
    except Exception as e:
        print(f"Failed to record session in DB: {e}")
    finally:
        db.close()
        
    active_sessions[user_id] = {
        "home_id": home_id,
        "login_time": now,
        "last_activity": now,
        "db_session_id": db_session_id
    }
    return {
        "home_id": home_id,
        "login_time": now,
        "last_activity": now
    }

def get_active_session(user_id: str) -> Optional[Dict[str, Any]]:
    cleanup_expired_sessions()
    session = active_sessions.get(user_id)
    if session:
        now = datetime.now(timezone.utc)
        if now - session["last_activity"] > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            end_session(user_id)
            return None
        # Update last activity in memory
        session["last_activity"] = now
        
        # Update last activity in DB
        if session.get("db_session_id"):
            db = SessionLocal()
            try:
                db_sess = db.query(UserSession).filter(UserSession.id == session["db_session_id"]).first()
                if db_sess:
                    db_sess.last_activity = now
                    db.commit()
            except Exception as e:
                print(f"Failed to update session activity in DB: {e}")
            finally:
                db.close()
                
        return {
            "home_id": session["home_id"],
            "login_time": session["login_time"],
            "last_activity": session["last_activity"]
        }
    return None

def update_session_home(user_id: str, new_home_id: str) -> Optional[Dict[str, Any]]:
    session = get_active_session(user_id)
    if session:
        session_cache = active_sessions.get(user_id)
        if session_cache:
            session_cache["home_id"] = new_home_id
            session_cache["last_activity"] = datetime.now(timezone.utc)
            return {
                "home_id": new_home_id,
                "login_time": session_cache["login_time"],
                "last_activity": session_cache["last_activity"]
            }
    return None

def end_session(user_id: str) -> Optional[Dict[str, Any]]:
    session = active_sessions.get(user_id)
    if not session:
        return None

    now = datetime.now(timezone.utc)
    duration = now - session["login_time"]
    duration_minutes = duration.total_seconds() / 60.0

    # Save logout to DB
    if session.get("db_session_id"):
        db = SessionLocal()
        try:
            db_sess = db.query(UserSession).filter(UserSession.id == session["db_session_id"]).first()
            if db_sess:
                db_sess.logout_time = now
                db_sess.duration_minutes = duration_minutes
                db.commit()
        except Exception as e:
            print(f"Failed to save session logout to DB: {e}")
        finally:
            db.close()

    result = {
        "user_id": user_id,
        "home_id": session["home_id"],
        "login_time": session["login_time"],
        "logout_time": now,
        "duration_minutes": duration_minutes
    }

    del active_sessions[user_id]
    return result

def cleanup_expired_sessions():
    now = datetime.now(timezone.utc)
    # Collect expired users first
    expired_users = []
    for user_id, session in list(active_sessions.items()):
        if now - session["last_activity"] > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            expired_users.append(user_id)
            
    for user_id in expired_users:
        end_session(user_id)
