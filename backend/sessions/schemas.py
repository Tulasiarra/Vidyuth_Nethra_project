from pydantic import BaseModel
from datetime import datetime
from typing import Any, Dict

class HomeSelectionSchema(BaseModel):
    home_id: str

class SwitchHomeSchema(BaseModel):
    new_home_id: str

class SessionDetailSchema(BaseModel):
    home_id: str
    login_time: datetime
    last_activity: datetime

class SessionStatusResponse(BaseModel):
    success: bool
    session: SessionDetailSchema

class SessionEndResponse(BaseModel):
    success: bool
    message: str
    summary: Dict[str, Any]