from fastapi import APIRouter, Depends
from energy.auth_middleware import get_current_user
from energy.service import (
    get_energy_data,
    get_energy_summary,
    get_hourly_usage
)
from energy.prediction import predict_usage
from energy.recommendation import generate_recommendations
from sessions.validators import validate_home_access
from sessions.lifecycle import get_active_session

router = APIRouter(
    prefix="/energy",
    tags=["Energy"]
)

@router.get("/data")
def energy_data(home_id: str, current_user: dict = Depends(get_current_user)):
    home_uuid = validate_home_access(current_user["email"], home_id)
    return get_energy_data(home_uuid)

@router.get("/summary")
def energy_summary(home_id: str, current_user: dict = Depends(get_current_user)):
    home_uuid = validate_home_access(current_user["email"], home_id)
    return get_energy_summary(home_uuid)

@router.get("/hourly")
def hourly_usage(home_id: str, current_user: dict = Depends(get_current_user)):
    home_uuid = validate_home_access(current_user["email"], home_id)
    return get_hourly_usage(home_uuid)

@router.get("/prediction")
def energy_prediction(home_id: str, current_user: dict = Depends(get_current_user)):
    home_uuid = validate_home_access(current_user["email"], home_id)
    return predict_usage(home_uuid)

@router.get("/recommendations")
def recommendations(current_user: dict = Depends(get_current_user)):
    # Get user's active home session to generate recommendations for
    session = get_active_session(current_user["email"])
    home_uuid = session["home_id"] if session else None
    return generate_recommendations(home_uuid)