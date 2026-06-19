import random
from datetime import datetime, timezone, timedelta
from sqlalchemy import func
from app.db.connection import SessionLocal
from app.db.models import Home, Device, DeviceDailySummary, HomeDailySummary, DeviceSession

def get_energy_data(home_id: str):
    db = SessionLocal()
    try:
        home = db.query(Home).filter(Home.id == home_id).first()
        if not home:
            return {"error": "Home not found"}
            
        devices = db.query(Device).filter(Device.home_id == home_id).all()
        
        # Calculate current power load
        active_devices = [d for d in devices if d.status == "ON" and d.is_enabled]
        current_load_kw = sum(d.rated_watts for d in active_devices) / 1000.0
        
        return {
            "home_id": home_id,
            "timestamp": datetime.now(timezone.utc),
            "temperature": 27.5, # Simulated environmental values
            "humidity": 60.0,
            "total_devices": len(devices),
            "active_devices_count": len(active_devices),
            "current_load_kw": round(current_load_kw, 3)
        }
    finally:
        db.close()

def get_energy_summary(home_id: str):
    db = SessionLocal()
    try:
        home = db.query(Home).filter(Home.id == home_id).first()
        if not home:
            return {"error": "Home not found"}
            
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        seven_days_ago_str = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
        thirty_days_ago_str = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Get all devices in this home
        devices = db.query(Device).filter(Device.home_id == home_id).all()
        device_ids = [d.id for d in devices]
        
        # Calculate dynamic today's energy up to now
        now = datetime.now(timezone.utc)
        today_start = datetime.combine(now.date(), datetime.min.time(), tzinfo=timezone.utc)
        today_str = now.strftime("%Y-%m-%d")
        yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # 1. Fetch completed sessions today for all devices in a single query
        completed_sessions_query = db.query(
            DeviceSession.device_id,
            func.sum(DeviceSession.energy_consumed_kwh).label("energy"),
            func.sum(DeviceSession.cost_incurred).label("cost")
        ).filter(
            DeviceSession.device_id.in_(device_ids),
            DeviceSession.start_time >= today_start,
            DeviceSession.end_time.isnot(None)
        ).group_by(DeviceSession.device_id).all()
        
        completed_map = {c.device_id: (float(c.energy or 0.0), float(c.cost or 0.0)) for c in completed_sessions_query}
        
        # 2. Fetch active sessions today for all devices in a single query
        active_sessions_query = db.query(
            DeviceSession
        ).filter(
            DeviceSession.device_id.in_(device_ids),
            DeviceSession.end_time.is_(None)
        ).all()
        
        active_map = {a.device_id: a for a in active_sessions_query}
        
        # 3. Fetch average runtimes over past 30 days for all devices in a single query
        avg_runtimes_query = db.query(
            DeviceDailySummary.device_id,
            func.avg(DeviceDailySummary.runtime_hours).label("avg_runtime")
        ).filter(
            DeviceDailySummary.device_id.in_(device_ids),
            DeviceDailySummary.date >= thirty_days_ago_str,
            DeviceDailySummary.date != today_str
        ).group_by(DeviceDailySummary.device_id).all()
        
        avg_runtime_map = {a.device_id: float(a.avg_runtime or 0.0) for a in avg_runtimes_query}
        
        # 4. Fetch yesterday's history for all devices in a single query
        yesterday_hist_query = db.query(
            DeviceDailySummary
        ).filter(
            DeviceDailySummary.device_id.in_(device_ids),
            DeviceDailySummary.date == yesterday_str
        ).all()
        
        yesterday_map = {y.device_id: y for y in yesterday_hist_query}
        
        today_device_breakdown = []
        yesterday_device_breakdown = []
        
        fallback_runtimes = {
            "AC": 5.0, "Fridge": 24.0, "Fan": 10.0, "BLDC Fan": 10.0,
            "Light": 6.0, "LED Light": 6.0, "TV": 3.0, "Router": 24.0,
            "Water Heater": 1.5, "Geyser": 1.5, "Washing Machine": 0.5
        }
        
        # Calculate breakdowns in-memory
        for d in devices:
            # Completed sessions today
            e_completed, c_completed = completed_map.get(d.id, (0.0, 0.0))
            
            # Active session today
            e_active = 0.0
            c_active = 0.0
            if d.status == "ON":
                active_session = active_map.get(d.id)
                if active_session:
                    start_time = active_session.start_time.replace(tzinfo=timezone.utc) if active_session.start_time.tzinfo is None else active_session.start_time
                    duration_hours = (now - start_time).total_seconds() / 3600.0
                    e_active = duration_hours * (d.rated_watts / 1000.0)
                    c_active = e_active * home.electricity_rate
            
            today_device_energy = e_completed + e_active
            today_device_cost = c_completed + c_active
            
            # Fallback if no sessions exist: scale the average daily runtime from the past 30 days
            if today_device_energy < 0.001:
                avg_runtime_val = avg_runtime_map.get(d.id, 0.0)
                if avg_runtime_val == 0.0:
                    avg_runtime_val = fallback_runtimes.get(d.device_type, 2.0)
                
                current_hour = now.hour + (now.minute / 60.0)
                today_device_energy = (current_hour / 24.0) * ((avg_runtime_val * d.rated_watts) / 1000.0)
                today_device_cost = today_device_energy * home.electricity_rate
                
            today_device_breakdown.append({
                "device_id": d.id,
                "device_name": d.name,
                "device_type": d.device_type,
                "energy_kwh": round(today_device_energy, 3),
                "cost": round(today_device_cost, 2)
            })
            
            # Yesterday's breakdown (from history)
            yesterday_hist = yesterday_map.get(d.id)
            if yesterday_hist:
                yesterday_device_breakdown.append({
                    "device_id": d.id,
                    "device_name": d.name,
                    "device_type": d.device_type,
                    "energy_kwh": round(yesterday_hist.energy_consumed_kwh, 3),
                    "cost": round(yesterday_hist.cost_incurred, 2)
                })
            else:
                # Mock if missing
                yesterday_device_breakdown.append({
                    "device_id": d.id,
                    "device_name": d.name,
                    "device_type": d.device_type,
                    "energy_kwh": round(((8.0 * d.rated_watts) / 1000.0) if d.device_type != "Fridge" else (24.0 * d.rated_watts / 1000.0), 3),
                    "cost": round(((8.0 * d.rated_watts / 1000.0) if d.device_type != "Fridge" else (24.0 * d.rated_watts / 1000.0)) * home.electricity_rate, 2)
                })
        
        # Today's totals
        today_energy = sum(x["energy_kwh"] for x in today_device_breakdown)
        today_cost = sum(x["cost"] for x in today_device_breakdown)
        
        # Yesterday's totals
        yesterday_energy = sum(x["energy_kwh"] for x in yesterday_device_breakdown)
        yesterday_cost = sum(x["cost"] for x in yesterday_device_breakdown)
        
        # Weekly (last 7 days including today's dynamic totals)
        weekly_hist = db.query(func.sum(HomeDailySummary.total_energy_kwh), func.sum(HomeDailySummary.total_cost)).filter(
            HomeDailySummary.home_id == home_id,
            HomeDailySummary.date >= seven_days_ago_str,
            HomeDailySummary.date != today_str
        ).first()
        weekly_energy = float(weekly_hist[0] or 0.0) + today_energy
        weekly_cost = float(weekly_hist[1] or 0.0) + today_cost
        
        # Monthly (last 30 days including today's dynamic totals)
        monthly_hist = db.query(func.sum(HomeDailySummary.total_energy_kwh), func.sum(HomeDailySummary.total_cost)).filter(
            HomeDailySummary.home_id == home_id,
            HomeDailySummary.date >= thirty_days_ago_str,
            HomeDailySummary.date != today_str
        ).first()
        monthly_energy = float(monthly_hist[0] or 0.0) + today_energy
        monthly_cost = float(monthly_hist[1] or 0.0) + today_cost
        
        # Top consuming device this month
        top_device = db.query(
            DeviceDailySummary.device_id,
            func.sum(DeviceDailySummary.energy_consumed_kwh)
        ).filter(
            DeviceDailySummary.home_id == home_id,
            DeviceDailySummary.date >= thirty_days_ago_str
        ).group_by(
            DeviceDailySummary.device_id
        ).order_by(
            func.sum(DeviceDailySummary.energy_consumed_kwh).desc()
        ).first()
        
        top_device_name = "None"
        top_device_usage = 0.0
        if top_device:
            # Look up device name from memory list
            device = next((device_obj for device_obj in devices if device_obj.id == top_device[0]), None)
            top_device_name = device.name if device else "Unknown"
            top_device_usage = float(top_device[1] or 0.0)
            
        return {
            "home_id": home_id,
            "target_bill": home.target_monthly_bill,
            "today": {
                "energy_kwh": round(today_energy, 1),
                "cost": round(today_cost, 0)
            },
            "yesterday": {
                "energy_kwh": round(yesterday_energy, 1),
                "cost": round(yesterday_cost, 0)
            },
            "weekly": {
                "energy_kwh": round(weekly_energy, 1),
                "cost": round(weekly_cost, 0)
            },
            "monthly": {
                "energy_kwh": round(monthly_energy, 1),
                "cost": round(monthly_cost, 0)
            },
            "top_consuming_device": {
                "name": top_device_name,
                "usage_kwh": round(top_device_usage, 1)
            },
            "today_device_breakdown": today_device_breakdown,
            "yesterday_device_breakdown": yesterday_device_breakdown
        }
    finally:
        db.close()

def get_hourly_usage(home_id: str):
    # Retrieve mock or relative hourly readings for visual charts
    # We will generate a structured curve peaking in afternoon/evening
    curve = [2.1, 1.8, 1.5, 3.2, 5.6, 7.2, 8.4, 9.1, 9.8, 8.7, 7.3, 4.2, 2.8]
    hours = ["12 AM", "2 AM", "4 AM", "6 AM", "8 AM", "10 AM", "12 PM", "2 PM", "4 PM", "6 PM", "8 PM", "10 PM", "12 AM"]
    
    # Scale based on the home's size / average
    db = SessionLocal()
    try:
        home = db.query(Home).filter(Home.id == home_id).first()
        scale = 1.0
        if home:
            # Scale based on target bill (higher budget -> larger home -> higher load)
            scale = home.target_monthly_bill / 3000.0
            
        results = []
        for h, val in zip(hours, curve):
            results.append({
                "time": h,
                "today": round(val * scale * random.uniform(0.92, 1.08), 1),
                "yesterday": round(val * scale * random.uniform(0.90, 1.10), 1)
            })
        return results
    finally:
        db.close()