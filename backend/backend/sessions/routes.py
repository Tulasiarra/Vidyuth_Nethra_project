from fastapi import APIRouter, Depends
from app.auth_middleware import get_current_user
from .schemas import HomeSelectionSchema, SwitchHomeSchema, SessionStatusResponse, SessionEndResponse
from .service import select_home, switch_home, get_session_status, terminate_session
from .validators import validate_home_access

router = APIRouter()

@router.post("/select", status_code=201)
def api_select_home(
    data: HomeSelectionSchema,
    current_user: dict = Depends(get_current_user)
):
    user_email = current_user["email"]
    validate_home_access(user_email, data.home_id)
    return select_home(user_email, data.home_id)

@router.post("/switch")
def api_switch_home(
    data: SwitchHomeSchema,
    current_user: dict = Depends(get_current_user)
):
    user_email = current_user["email"]
    validate_home_access(user_email, data.new_home_id)
    return switch_home(user_email, data.new_home_id)

@router.get("/status", response_model=SessionStatusResponse)
def api_get_status(
    current_user: dict = Depends(get_current_user)
):
    user_email = current_user["email"]
    return get_session_status(user_email)

@router.post("/end", response_model=SessionEndResponse)
def api_end_session(
    current_user: dict = Depends(get_current_user)
):
    user_email = current_user["email"]
    return terminate_session(user_email)
