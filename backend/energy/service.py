from datetime import datetime, date, timezone, timedelta
import uuid
from database import supabase

def seed_household_data_if_empty(household_id: str):
    try:
        # Check if we already have appliance usage data for this household
        usage_check = supabase.table("appliance_usage").select("usage_id").eq("household_id", household_id).limit(1).execute()
        if usage_check.data:
            return  # Data already exists
            
        # Get user_id associated with this household
        house_res = supabase.table("households").select("user_id").eq("household_id", household_id).execute()
        user_id = house_res.data[0]["user_id"] if house_res.data else None

        # 1. Insert user_appliances
        user_appliance_data = [
            {"user_appliance_id": str(uuid.uuid4()), "household_id": household_id, "appliance_id": 1, "quantity": 3, "purchase_year": 2022, "energy_rating": "5 Star"},
            {"user_appliance_id": str(uuid.uuid4()), "household_id": household_id, "appliance_id": 2, "quantity": 1, "purchase_year": 2023, "energy_rating": "3 Star"},
            {"user_appliance_id": str(uuid.uuid4()), "household_id": household_id, "appliance_id": 3, "quantity": 1, "purchase_year": 2021, "energy_rating": "4 Star"}
        ]
        supabase.table("user_appliances").insert(user_appliance_data).execute()

        # 2. Insert appliance_usage
        current_date = date.today().replace(day=1)
        usage_data = [
            {"usage_id": str(uuid.uuid4()), "household_id": household_id, "appliance_id": 1, "usage_month": str(current_date), "average_daily_hours": 8.5, "estimated_units_consumed": 57.375},
            {"usage_id": str(uuid.uuid4()), "household_id": household_id, "appliance_id": 2, "usage_month": str(current_date), "average_daily_hours": 6.0, "estimated_units_consumed": 270.00},
            {"usage_id": str(uuid.uuid4()), "household_id": household_id, "appliance_id": 3, "usage_month": str(current_date), "average_daily_hours": 24.0, "estimated_units_consumed": 180.00}
        ]
        supabase.table("appliance_usage").insert(usage_data).execute()

        # 3. Insert user_bills
        bill_data = [
            {
                "bill_id": str(uuid.uuid4()),
                "household_id": household_id,
                "bill_month": str(current_date),
                "total_units_consumed": 507.375,
                "total_amount": 4566.38,
                "billing_days": 30
            },
            {
                "bill_id": str(uuid.uuid4()),
                "household_id": household_id,
                "bill_month": str(current_date - timedelta(days=30)),
                "total_units_consumed": 480.50,
                "total_amount": 4324.50,
                "billing_days": 31
            }
        ]
        bill_res = supabase.table("user_bills").insert(bill_data).execute()
        bill_id = bill_res.data[0]["bill_id"] if bill_res.data else str(uuid.uuid4())

        # 4. Insert recommendation_history
        rec_data = [
            {
                "recommendation_id": str(uuid.uuid4()),
                "household_id": household_id,
                "bill_id": bill_id,
                "appliance_id": 2,
                "recommendation_text": "Reduce AC usage for one hour",
                "estimated_monthly_savings": 45.00
            },
            {
                "recommendation_id": str(uuid.uuid4()),
                "household_id": household_id,
                "bill_id": bill_id,
                "appliance_id": 1,
                "recommendation_text": "Use ceiling fans instead of AC when possible",
                "estimated_monthly_savings": 25.00
            }
        ]
        supabase.table("recommendation_history").insert(rec_data).execute()

    except Exception as e:
        print(f"Warning: Failed to seed default household data: {str(e)}")


def get_energy_data(home_id: str):
    seed_household_data_if_empty(home_id)
    
    try:
        # Query total units consumed by appliances
        contrib_res = supabase.table("appliance_contribution").select("*").eq("household_id", home_id).execute()
        total_units = sum(item["total_units"] for item in contrib_res.data) if contrib_res.data else 0.0
        
        # Real-time dashboard expects hourly consumption rate
        # Let's divide total monthly units by 30 days and 24 hours to scale to a realistic current usage rate (kW)
        current_rate = round(total_units / (30 * 24), 2) if total_units > 0 else 5.6
        
        return {
            "home_id": home_id,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "temperature": 29.0,
            "humidity": 62,
            "ac_status": True,
            "fan_status": True,
            "light_status": False,
            "energy_consumption": current_rate
        }
    except Exception as e:
        return {
            "home_id": home_id,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "temperature": 30.0,
            "humidity": 65,
            "ac_status": True,
            "fan_status": True,
            "light_status": False,
            "energy_consumption": 5.6,
            "error": f"Database query failed: {str(e)}"
        }


def get_energy_summary(home_id: str):
    seed_household_data_if_empty(home_id)
    
    try:
        # Query monthly bills
        bills_res = supabase.table("user_bills").select("*").eq("household_id", home_id).order("bill_month", desc=True).execute()
        
        if bills_res.data:
            latest_bill = bills_res.data[0]
            monthly_usage = latest_bill["total_units_consumed"]
            
            # Estimate current usage details relative to monthly consumption
            daily_usage = round(monthly_usage / latest_bill.get("billing_days", 30), 2)
            current_usage = round(daily_usage / 24, 2)
            weekly_usage = round(daily_usage * 7, 2)
        else:
            current_usage = 5.6
            daily_usage = 38.2
            weekly_usage = 250.1
            monthly_usage = 1032.5

        return {
            "home_id": home_id,
            "current_usage": current_usage,
            "daily_usage": daily_usage,
            "weekly_usage": weekly_usage,
            "monthly_usage": monthly_usage
        }
    except Exception as e:
        return {
            "home_id": home_id,
            "current_usage": 5.6,
            "daily_usage": 38.2,
            "weekly_usage": 250.1,
            "monthly_usage": 1032.5,
            "error": f"Database query failed: {str(e)}"
        }


def get_hourly_usage(home_id: str):
    seed_household_data_if_empty(home_id)
    
    try:
        # Query user_appliances joined with appliances avg_wattage
        appliances_res = supabase.table("user_appliances").select("*, appliances(avg_wattage)").eq("household_id", home_id).execute()
        
        if not appliances_res.data:
            return [
                {"hour": "08:00", "usage": 4.2},
                {"hour": "09:00", "usage": 5.0},
                {"hour": "10:00", "usage": 5.4},
                {"hour": "11:00", "usage": 5.8}
            ]
            
        total_watts = 0
        for item in appliances_res.data:
            quantity = item["quantity"]
            app_info = item.get("appliances")
            avg_wattage = app_info.get("avg_wattage", 100) if app_info else 100
            total_watts += quantity * avg_wattage
            
        avg_kwh = total_watts / 1000.0
        
        return [
            {"hour": "08:00", "usage": round(avg_kwh * 0.7, 2)},
            {"hour": "09:00", "usage": round(avg_kwh * 0.9, 2)},
            {"hour": "10:00", "usage": round(avg_kwh * 1.0, 2)},
            {"hour": "11:00", "usage": round(avg_kwh * 1.1, 2)}
        ]
    except Exception as e:
        return [
            {"hour": "08:00", "usage": 4.2},
            {"hour": "09:00", "usage": 5.0},
            {"hour": "10:00", "usage": 5.4},
            {"hour": "11:00", "usage": 5.8}
        ]