from database import supabase
from energy.service import seed_household_data_if_empty

def generate_recommendations(home_id: str = None):
    if not home_id:
        return [
            {
                "recommendation": "Please select an active home session to generate personalized recommendations.",
                "reason": "No active home session found.",
                "expected_benefit": "N/A"
            }
        ]
        
    seed_household_data_if_empty(home_id)
    
    try:
        # Query recommendation history
        rec_res = supabase.table("recommendation_history").select("*").eq("household_id", home_id).execute()
        
        if rec_res.data:
            return [
                {
                    "recommendation": rec["recommendation_text"],
                    "reason": "Personalized energy savings plan for your home.",
                    "expected_benefit": f"Save ${rec['estimated_monthly_savings']} monthly"
                }
                for rec in rec_res.data
            ]
        else:
            return [
                {
                    "recommendation": "Reduce AC usage for one hour",
                    "reason": "AC is consuming most of today's electricity",
                    "expected_benefit": "May save 10-15% energy"
                },
                {
                    "recommendation": "Turn off unused lights at night",
                    "reason": "Night-time electricity usage is higher than usual",
                    "expected_benefit": "Reduce overnight consumption"
                }
            ]
    except Exception as e:
        return [
            {
                "recommendation": "Reduce AC usage for one hour",
                "reason": "AC is consuming most of today's electricity",
                "expected_benefit": "May save 10-15% energy"
            },
            {
                "recommendation": "Turn off unused lights at night",
                "reason": "Night-time electricity usage is higher than usual",
                "expected_benefit": "Reduce overnight consumption"
            }
        ]