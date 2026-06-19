from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.db.connection import get_db
from app.db.models import Device, Home, DeviceSession, DeviceDailySummary, HomeDailySummary
from app.auth_middleware import get_current_user
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/devices", tags=["Devices"])

class DeviceCreateSchema(BaseModel):
    id: Optional[str] = None
    home_id: str
    name: str
    device_type: str
    brand: Optional[str] = None
    model: Optional[str] = None
    room_name: Optional[str] = "Living Room"
    rated_watts: float

class DeviceResponseSchema(BaseModel):
    id: str
    home_id: str
    name: str
    device_type: str
    brand: Optional[str]
    model: Optional[str]
    room_name: str
    rated_watts: float
    status: str
    is_enabled: bool

    class Config:
        from_attributes = True

class ToggleResponseSchema(BaseModel):
    success: bool
    status: str
    session_summary: Optional[dict] = None

@router.get("", response_model=List[DeviceResponseSchema])
def get_devices(home_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Verify home belongs to user
    user_email = current_user["email"]
    home = db.query(Home).filter(Home.id == home_id, Home.user_email == user_email).first()
    if not home:
        raise HTTPException(status_code=403, detail="Access denied or home not found")
        
    devices = db.query(Device).filter(Device.home_id == home_id).all()
    return devices

@router.post("", response_model=DeviceResponseSchema, status_code=201)
def add_device(data: DeviceCreateSchema, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_email = current_user["email"]
    home = db.query(Home).filter(Home.id == data.home_id, Home.user_email == user_email).first()
    if not home:
        raise HTTPException(status_code=403, detail="Access denied or home not found")
        
    d_id = data.id or f"device_{int(datetime.now(timezone.utc).timestamp())}"
    
    # Check if ID exists
    existing = db.query(Device).filter(Device.id == d_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Device ID already exists")
        
    new_device = Device(
        id=d_id,
        home_id=data.home_id,
        name=data.name,
        device_type=data.device_type,
        brand=data.brand,
        model=data.model,
        room_name=data.room_name,
        rated_watts=data.rated_watts,
        status="OFF",
        is_enabled=True
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device

@router.get("/{device_id}", response_model=DeviceResponseSchema)
def get_device_details(device_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    # Verify access
    user_email = current_user["email"]
    home = db.query(Home).filter(Home.id == device.home_id, Home.user_email == user_email).first()
    if not home:
        raise HTTPException(status_code=403, detail="Access denied")
        
    return device

@router.put("/{device_id}", response_model=DeviceResponseSchema)
def update_device(device_id: str, data: DeviceCreateSchema, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    # Verify access
    user_email = current_user["email"]
    home = db.query(Home).filter(Home.id == device.home_id, Home.user_email == user_email).first()
    if not home:
        raise HTTPException(status_code=403, detail="Access denied")
        
    device.name = data.name
    device.brand = data.brand
    device.model = data.model
    device.room_name = data.room_name
    device.rated_watts = data.rated_watts
    
    db.commit()
    db.refresh(device)
    return device

@router.delete("/{device_id}")
def delete_device(device_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    # Verify access
    user_email = current_user["email"]
    home = db.query(Home).filter(Home.id == device.home_id, Home.user_email == user_email).first()
    if not home:
        raise HTTPException(status_code=403, detail="Access denied")
        
    db.delete(device)
    db.commit()
    return {"success": True, "message": f"Device '{device_id}' deleted successfully"}

@router.post("/{device_id}/toggle", response_model=ToggleResponseSchema)
def toggle_device(device_id: str, status: Optional[str] = None, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    # Verify access
    user_email = current_user["email"]
    home = db.query(Home).filter(Home.id == device.home_id, Home.user_email == user_email).first()
    if not home:
        raise HTTPException(status_code=403, detail="Access denied")
        
    # Determine next status
    current_status = device.status
    next_status = status.upper() if status else ("OFF" if current_status == "ON" else "ON")
    
    if next_status not in ["ON", "OFF"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be ON or OFF.")
        
    session_summary = None
    
    if current_status != next_status:
        now = datetime.now(timezone.utc)
        device.status = next_status
        
        if next_status == "ON":
            # Start new session
            new_session = DeviceSession(
                device_id=device_id,
                start_time=now
            )
            db.add(new_session)
        else:
            # End existing session
            session = db.query(DeviceSession).filter(
                DeviceSession.device_id == device_id,
                DeviceSession.end_time.is_(None)
            ).order_by(DeviceSession.start_time.desc()).first()
            
            if session:
                session.end_time = now
                delta = now - session.start_time.replace(tzinfo=timezone.utc)
                runtime_minutes = max(0.1, delta.total_seconds() / 60.0) # at least 0.1 min for logs
                
                energy = (runtime_minutes / 60.0) * device.rated_watts / 1000.0
                cost = energy * home.electricity_rate
                
                session.runtime_minutes = runtime_minutes
                session.energy_consumed_kwh = energy
                session.cost_incurred = cost
                
                session_summary = {
                    "duration_minutes": round(runtime_minutes, 2),
                    "energy_kwh": round(energy, 4),
                    "cost_incurred": round(cost, 2)
                }
                
                # Update Daily Summaries
                today_str = now.strftime("%Y-%m-%d")
                
                # Device Daily Summary
                summary = db.query(DeviceDailySummary).filter(
                    DeviceDailySummary.device_id == device_id,
                    DeviceDailySummary.date == today_str
                ).first()
                
                runtime_hours = runtime_minutes / 60.0
                if summary:
                    summary.runtime_hours += runtime_hours
                    summary.energy_consumed_kwh += energy
                    summary.cost_incurred += cost
                else:
                    summary = DeviceDailySummary(
                        home_id=device.home_id,
                        device_id=device_id,
                        date=today_str,
                        runtime_hours=runtime_hours,
                        energy_consumed_kwh=energy,
                        cost_incurred=cost
                    )
                    db.add(summary)
                    
                # Home Daily Summary
                home_summary = db.query(HomeDailySummary).filter(
                    HomeDailySummary.home_id == device.home_id,
                    HomeDailySummary.date == today_str
                ).first()
                
                if home_summary:
                    home_summary.total_energy_kwh += energy
                    home_summary.total_cost += cost
                else:
                    home_summary = HomeDailySummary(
                        home_id=device.home_id,
                        date=today_str,
                        total_energy_kwh=energy,
                        total_cost=cost
                    )
                    db.add(home_summary)
        
        db.commit()
        
    return ToggleResponseSchema(
        success=True,
        status=device.status,
        session_summary=session_summary
    )
