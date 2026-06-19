from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.db.connection import SessionLocal
from app.db.models import Home, Device, DeviceDailySummary, HomeBaseline, Recommendation
from energy.prediction import predict_usage

def generate_recommendations(home_id: str):
    db = SessionLocal()
    try:
        home = db.query(Home).filter(Home.id == home_id).first()
        if not home:
            return {"error": "Home not found"}

        # 1. Clear old recommendations
        db.query(Recommendation).filter(
            Recommendation.home_id == home_id,
            Recommendation.status == "active"
        ).delete(synchronize_session=False)
        db.commit()

        recommendations = []

        # 2. Check predicted bill vs target budget
        pred_res = predict_usage(home_id)
        if "error" not in pred_res:
            monthly_cost = pred_res["monthly"]["cost"]
            target_bill = home.target_monthly_bill
            
            if monthly_cost > target_bill:
                diff = monthly_cost - target_bill
                
                # Find high consuming devices (e.g. AC or Geyser) to suggest savings
                devices = db.query(Device).filter(Device.home_id == home_id).all()
                ac_devices = [d for d in devices if d.device_type.upper() in ["AC", "GEYSER", "WATER HEATER"]]
                
                saving_msg = ""
                potential_saving = 0.0
                if ac_devices:
                    target_device = ac_devices[0]
                    # Calculate potential savings if reduced by 2 hours/day
                    # 2 hours * rated_watts / 1000 * 30 days * rate
                    kwh_saved = (2.0 * target_device.rated_watts / 1000.0) * 30.0
                    potential_saving = kwh_saved * home.electricity_rate
                    saving_msg = f" Reducing {target_device.name} runtime by 2 hours per day could save approximately {round(kwh_saved, 1)} kWh (₹{round(potential_saving, 0)}) per month."
                
                reco = Recommendation(
                    home_id=home_id,
                    type="Budget Alert",
                    message=f"Your electricity bill is expected to exceed your monthly target of ₹{round(target_bill, 0)} by ₹{round(diff, 0)}.{saving_msg}",
                    potential_saving=potential_saving,
                    priority="high",
                    status="active"
                )
                db.add(reco)
                recommendations.append(reco)

        # 3. Analyze runtime vs baseline per device category
        baselines = db.query(HomeBaseline).filter(HomeBaseline.home_id == home_id).all()
        baseline_map = {b.device_type.upper(): b.baseline_runtime_hours for b in baselines}
        
        # Calculate last 7 days average runtime per device category
        seven_days_ago_str = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Fetch summaries grouped by device type
        avg_runtimes = db.query(
            Device.device_type,
            func.avg(DeviceDailySummary.runtime_hours)
        ).join(
            DeviceDailySummary, Device.id == DeviceDailySummary.device_id
        ).filter(
            Device.home_id == home_id,
            DeviceDailySummary.date >= seven_days_ago_str
        ).group_by(
            Device.device_type
        ).all()
        
        for dev_type, avg_runtime in avg_runtimes:
            dev_type_up = dev_type.upper()
            avg_runtime = float(avg_runtime or 0.0)
            
            if dev_type_up in baseline_map:
                base_val = baseline_map[dev_type_up]
                
                if base_val > 0.5: # Only analyze significant devices
                    ratio = avg_runtime / base_val
                    
                    if ratio > 1.25:
                        pct_increase = int((ratio - 1.0) * 100.0)
                        
                        # Find a device of this type
                        device = db.query(Device).filter(Device.home_id == home_id, Device.device_type == dev_type).first()
                        potential_saving = ((avg_runtime - base_val) * (device.rated_watts if device else 100.0) / 1000.0) * 30.0 * home.electricity_rate
                        
                        reco = Recommendation(
                            home_id=home_id,
                            device_id=device.id if device else None,
                            type="Usage Spike",
                            message=f"Your {dev_type} usage is {pct_increase}% higher than your normal pattern this week.",
                            potential_saving=potential_saving,
                            priority="medium" if ratio < 1.5 else "high",
                            status="active"
                        )
                        db.add(reco)
                        recommendations.append(reco)
                        
                    elif ratio < 0.95:
                        reco = Recommendation(
                            home_id=home_id,
                            type="Usage Normal",
                            message=f"{dev_type} usage remains within or below your normal range.",
                            potential_saving=0.0,
                            priority="low",
                            status="active"
                        )
                        db.add(reco)
                        recommendations.append(reco)
                        
        db.commit()

        # Format output
        result = []
        for r in recommendations:
            result.append({
                "id": r.id,
                "home_id": r.home_id,
                "device_id": r.device_id,
                "type": r.type,
                "message": r.message,
                "potential_saving": round(r.potential_saving, 2),
                "priority": r.priority,
                "created_at": r.created_at
            })
            
        return result
    except Exception as e:
        db.rollback()
        print(f"Error generating recommendations: {e}")
        return {"error": str(e)}
    finally:
        db.close()