from database import supabase
from energy.service import seed_household_data_if_empty

def predict_usage(home_id: str):
    seed_household_data_if_empty(home_id)
    
    try:
        # Query monthly bills
        bills_res = supabase.table("user_bills").select("*").eq("household_id", home_id).order("bill_month", desc=True).execute()
        
        if bills_res.data:
            latest_bill = bills_res.data[0]
            latest_usage = latest_bill["total_units_consumed"]
            
            # Predict usage with a slight variation (+5%)
            predicted_usage = round(latest_usage * 1.05, 2)
            next_day_estimate = round(latest_usage / latest_bill.get("billing_days", 30) * 0.98, 2)
        else:
            predicted_usage = 42.5
            next_day_estimate = 38.0
            
        return {
            "home_id": home_id,
            "predicted_usage": predicted_usage,
            "next_day_estimate": next_day_estimate
        }
    except Exception as e:
        return {
            "home_id": home_id,
            "predicted_usage": 42.5,
            "next_day_estimate": 38.0,
            "error": f"Database query failed: {str(e)}"
        }