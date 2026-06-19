import re
from fastapi import APIRouter, Depends, HTTPException

from energy.auth_middleware import get_current_user

from energy.service import (
    get_energy_data,
    get_energy_summary,
    get_hourly_usage
)

from energy.prediction import predict_usage
from energy.recommendation import generate_recommendations

router = APIRouter(
    prefix="/energy",
    tags=["Energy"]
)

# Only allow letters, digits, underscores, and hyphens in home IDs
_HOME_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]+$')

def _validate_home_id(home_id: str) -> None:
    """Raise HTTP 400 if home_id contains special characters."""
    if not _HOME_ID_PATTERN.match(home_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid Home ID: special characters are not allowed. "
                   "Only letters, digits, underscores, and hyphens are permitted."
        )


@router.get("/data")
def energy_data(home_id: str):
    _validate_home_id(home_id)
    return get_energy_data(home_id)


@router.get("/summary")
def energy_summary(home_id: str):
    _validate_home_id(home_id)
    return get_energy_summary(home_id)


@router.get("/hourly")
def hourly_usage(home_id: str):
    _validate_home_id(home_id)
    return get_hourly_usage(home_id)


@router.get("/prediction")
def energy_prediction(home_id: str):
    _validate_home_id(home_id)
    return predict_usage(home_id)


@router.get("/recommendations")
def recommendations():
    return generate_recommendations()