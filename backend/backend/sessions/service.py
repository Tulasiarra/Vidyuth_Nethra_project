from .lifecycle import (
    start_session,
    get_active_session,
    update_session_home,
    end_session
)
from fastapi import HTTPException

def select_home(user_id: str, home_id: str):
    session = start_session(user_id, home_id)
    return {
        "success": True,
        "message": f"Home '{home_id}' selected successfully.",
        "session": session
    }

def switch_home(user_id: str, new_home_id: str):
    session = update_session_home(user_id, new_home_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="No active session found. Please select a home first."
        )
    return {
        "success": True,
        "message": f"Switched to home '{new_home_id}' successfully.",
        "session": session
    }

def get_session_status(user_id: str):
    session = get_active_session(user_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="No active session found. Please select a home first."
        )
    return {
        "success": True,
        "session": session
    }

def terminate_session(user_id: str):
    result = end_session(user_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="No active session to terminate."
        )
    return {
        "success": True,
        "message": "Session ended successfully.",
        "summary": result
    }
