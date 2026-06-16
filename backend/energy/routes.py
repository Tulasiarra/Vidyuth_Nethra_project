from fastapi import APIRouter, Depends

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


@router.get("/data")
def energy_data(home_id: str):
    return get_energy_data(home_id)


@router.get("/summary")
def energy_summary(home_id: str):
    return get_energy_summary(home_id)


@router.get("/hourly")
def hourly_usage(home_id: str):
    return get_hourly_usage(home_id)


@router.get("/prediction")
def energy_prediction(home_id: str):
    return predict_usage(home_id)


@router.get("/recommendations")
def recommendations():
    return generate_recommendations()