from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.connection import get_db
from app.db.models import Home
from app.auth_middleware import get_current_user
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/homes", tags=["Homes"])

class HomeCreateSchema(BaseModel):
    id: Optional[str] = None
    name: str
    location: Optional[str] = "Bangalore, Karnataka"
    electricity_rate: float
    target_monthly_bill: float
    home_type: str

class HomeResponseSchema(BaseModel):
    id: str
    name: str
    location: Optional[str]
    electricity_rate: float
    target_monthly_bill: float
    home_type: str
    user_email: str

    class Config:
        from_attributes = True

@router.get("", response_model=List[HomeResponseSchema])
def get_homes(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_email = current_user["email"]
    homes = db.query(Home).filter(Home.user_email == user_email).all()
    # Transfer seeded homes if user has fewer than 5 homes, so they can see all sample data
    if len(homes) < 5 and user_email not in ["arjun@example.com", "testuser_123@example.com"]:
        demo_homes_count = db.query(Home).filter(Home.user_email.in_(["arjun@example.com", "testuser_123@example.com"])).count()
        if demo_homes_count > 0:
            db.query(Home).filter(Home.user_email.in_(["arjun@example.com", "testuser_123@example.com"])).update({"user_email": user_email}, synchronize_session=False)
            db.commit()
            homes = db.query(Home).filter(Home.user_email == user_email).all()
    return homes

@router.post("", response_model=HomeResponseSchema, status_code=201)
def create_home(data: HomeCreateSchema, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_email = current_user["email"]
    # Generate unique home ID if not provided
    h_id = data.id or f"home_{int(datetime.utcnow().timestamp())}"
    
    # Check if home ID already exists
    existing = db.query(Home).filter(Home.id == h_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Home ID already exists")

    new_home = Home(
        id=h_id,
        name=data.name,
        location=data.location,
        electricity_rate=data.electricity_rate,
        target_monthly_bill=data.target_monthly_bill,
        home_type=data.home_type,
        user_email=user_email
    )
    db.add(new_home)
    db.commit()
    db.refresh(new_home)
    return new_home

@router.get("/{home_id}", response_model=HomeResponseSchema)
def get_home_details(home_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_email = current_user["email"]
    home = db.query(Home).filter(Home.id == home_id, Home.user_email == user_email).first()
    if not home:
        raise HTTPException(status_code=404, detail="Home not found")
    return home

@router.put("/{home_id}", response_model=HomeResponseSchema)
def update_home(home_id: str, data: HomeCreateSchema, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_email = current_user["email"]
    home = db.query(Home).filter(Home.id == home_id, Home.user_email == user_email).first()
    if not home:
        raise HTTPException(status_code=404, detail="Home not found")
    
    home.name = data.name
    home.location = data.location
    home.electricity_rate = data.electricity_rate
    home.target_monthly_bill = data.target_monthly_bill
    home.home_type = data.home_type
    
    db.commit()
    db.refresh(home)
    return home

@router.delete("/{home_id}")
def delete_home(home_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_email = current_user["email"]
    home = db.query(Home).filter(Home.id == home_id, Home.user_email == user_email).first()
    if not home:
        raise HTTPException(status_code=404, detail="Home not found")
    
    db.delete(home)
    db.commit()
    return {"success": True, "message": f"Home '{home_id}' deleted successfully"}
