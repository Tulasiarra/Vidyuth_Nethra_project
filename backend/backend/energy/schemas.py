from pydantic import BaseModel


class EnergyDataResponse(BaseModel):
    home_id: str
    temperature: float
    humidity: float
    energy_consumption: float


class PredictionResponse(BaseModel):
    home_id: str
    predicted_usage: float
    next_day_estimate: float