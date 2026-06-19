import os
import numpy as np
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db.connection import SessionLocal
from app.db.models import Home, Device, DeviceDailySummary, HomeBaseline, Prediction, PredictionResult
from ml.predict import predict_runtimes, DEVICE_CATEGORIES

def get_device_history_30_days(db: Session, home_id: str) -> np.ndarray:
    """
    Retrieves the last 30 days of daily runtime history for all device categories in a home.
    Returns a numpy array of shape (30, 24).
    """
    now = datetime.now(timezone.utc)
    # Fetch all device summaries for this home from the last 35 days (to ensure we get 30 distinct days)
    start_date = (now - timedelta(days=35)).strftime("%Y-%m-%d")
    
    devices = db.query(Device).filter(Device.home_id == home_id).all()
    device_id_map = {d.id: d.device_type.lower().replace(" ", "_") for d in devices}
    
    # Query summaries
    summaries = db.query(DeviceDailySummary).filter(
        DeviceDailySummary.home_id == home_id,
        DeviceDailySummary.date >= start_date
    ).order_by(DeviceDailySummary.date.desc()).all()
    
    # Organize by date and category
    # Get the last 30 unique dates
    unique_dates = sorted(list(set(s.date for s in summaries)))[-30:]
    
    # Initialize history matrix (30, 24)
    history = np.zeros((30, 24))
    
    # Map category to index
    cat_to_idx = {cat: i for i, cat in enumerate(DEVICE_CATEGORIES)}
    
    # Fill history matrix
    for date_idx, date_str in enumerate(unique_dates):
        date_summaries = [s for s in summaries if s.date == date_str]
        for s in date_summaries:
            cat = device_id_map.get(s.device_id)
            if cat in cat_to_idx:
                idx = cat_to_idx[cat]
                history[date_idx, idx] = max(history[date_idx, idx], s.runtime_hours)
                
    return history

def predict_usage(home_id: str):
    db = SessionLocal()
    try:
        home = db.query(Home).filter(Home.id == home_id).first()
        if not home:
            return {"error": "Home not found"}

        # 1. Fetch history and run LSTM predictions
        history = get_device_history_30_days(db, home_id)
        raw_predictions = predict_runtimes(history, home_id) # dict with tomorrow, next_7_days, next_30_days
        
        # 2. Map predictions to devices
        devices = db.query(Device).filter(Device.home_id == home_id, Device.is_enabled == True).all()
        
        tomorrow_energy = 0.0
        tomorrow_cost = 0.0
        
        weekly_energy = 0.0
        weekly_cost = 0.0
        
        monthly_energy = 0.0
        monthly_cost = 0.0
        
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # Clear existing predictions for today to avoid duplicates
        db.query(Prediction).filter(
            Prediction.device_id.in_([d.id for d in devices]),
            Prediction.date == today_str
        ).delete(synchronize_session=False)
        db.commit()

        device_predictions = []
        for device in devices:
            cat = device.device_type.lower().replace(" ", "_")
            
            # Lookup predictions
            pred_t = raw_predictions["tomorrow"].get(cat, 0.0)
            pred_w = raw_predictions["next_7_days"].get(cat, 0.0)
            pred_m = raw_predictions["next_30_days"].get(cat, 0.0)
            
            # If no history exists, fallback to home baseline
            if pred_t < 0.01:
                baseline = db.query(HomeBaseline).filter(
                    HomeBaseline.home_id == home_id,
                    HomeBaseline.device_type == device.device_type
                ).first()
                if baseline:
                    pred_t = baseline.baseline_runtime_hours
                    pred_w = pred_t * 7.0
                    pred_m = pred_t * 30.0
                else:
                    # Generic fallback based on device type
                    fallback_runtimes = {
                        "AC": 5.0, "Fridge": 24.0, "Fan": 10.0, "BLDC Fan": 10.0,
                        "Light": 6.0, "LED Light": 6.0, "TV": 3.0, "Router": 24.0,
                        "Water Heater": 1.5, "Geyser": 1.5, "Washing Machine": 0.5
                    }
                    pred_t = fallback_runtimes.get(device.device_type, 2.0)
                    pred_w = pred_t * 7.0
                    pred_m = pred_t * 30.0
            
            # Energy calculation: rated_watts * runtime / 1000
            e_t = (pred_t * device.rated_watts) / 1000.0
            e_w = (pred_w * device.rated_watts) / 1000.0
            e_m = (pred_m * device.rated_watts) / 1000.0
            
            # Cost calculation: energy * rate
            c_t = e_t * home.electricity_rate
            c_w = e_w * home.electricity_rate
            c_m = e_m * home.electricity_rate
            
            # Aggregate totals
            tomorrow_energy += e_t
            tomorrow_cost += c_t
            
            weekly_energy += e_w
            weekly_cost += c_w
            
            monthly_energy += e_m
            monthly_cost += c_m
            
            # Update yesterday's predictions with actual runtimes and accuracy if available
            yesterday_str = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
            yesterday_summary = db.query(DeviceDailySummary).filter(
                DeviceDailySummary.device_id == device.id,
                DeviceDailySummary.date == yesterday_str
            ).first()
            if yesterday_summary:
                past_pred = db.query(Prediction).filter(
                    Prediction.device_id == device.id,
                    Prediction.date == yesterday_str
                ).first()
                if past_pred:
                    past_pred.actual_runtime_hours = yesterday_summary.runtime_hours
                    pred_val = past_pred.tomorrow_predicted_hours or past_pred.predicted_runtime_hours or 0.1
                    act_val = yesterday_summary.runtime_hours
                    error_ratio = abs(pred_val - act_val) / max(act_val, pred_val, 0.1)
                    past_pred.prediction_accuracy = round(max(0.0, (1.0 - error_ratio) * 100.0), 2)

            # Save device predictions
            db_pred = Prediction(
                device_id=device.id,
                date=today_str,
                tomorrow_predicted_hours=pred_t,
                seven_day_predicted_hours=pred_w,
                thirty_day_predicted_hours=pred_m,
                predicted_runtime_hours=pred_t,
                actual_runtime_hours=0.0,
                prediction_accuracy=100.0, # Updated next day
                predicted_energy_kwh=e_t,
                predicted_cost=c_t
            )
            db.add(db_pred)
            
            device_predictions.append({
                "device_id": device.id,
                "device_name": device.name,
                "device_type": device.device_type,
                "tomorrow": {
                    "runtime_hours": round(pred_t, 2),
                    "energy_kwh": round(e_t, 3),
                    "cost": round(c_t, 2)
                },
                "weekly": {
                    "runtime_hours": round(pred_w, 2),
                    "energy_kwh": round(e_w, 3),
                    "cost": round(c_w, 2)
                },
                "monthly": {
                    "runtime_hours": round(pred_m, 2),
                    "energy_kwh": round(e_m, 3),
                    "cost": round(c_m, 2)
                }
            })
            
        db.commit()
        
        return {
            "home_id": home_id,
            "tomorrow": {
                "energy_kwh": round(tomorrow_energy, 2),
                "cost": round(tomorrow_cost, 2)
            },
            "weekly": {
                "energy_kwh": round(weekly_energy, 2),
                "cost": round(weekly_cost, 2)
            },
            "monthly": {
                "energy_kwh": round(monthly_energy, 2),
                "cost": round(monthly_cost, 2)
            },
            "device_predictions": device_predictions
        }
    except Exception as e:
        db.rollback()
        print(f"Error executing forecasting: {e}")
        return {"error": str(e)}
    finally:
        db.close()