from datetime import datetime

def get_energy_data(home_id: str):

    return {
        "home_id": home_id,
        "timestamp": datetime.utcnow(),
        "temperature": 30,
        "humidity": 65,
        "ac_status": True,
        "fan_status": True,
        "light_status": False,
        "energy_consumption": 5.6
    }


def get_energy_summary(home_id: str):

    return {
        "home_id": home_id,
        "current_usage": 5.6,
        "daily_usage": 38.2,
        "weekly_usage": 250.1,
        "monthly_usage": 1032.5
    }


def get_hourly_usage(home_id: str):

    return [
        {"hour": "08:00", "usage": 4.2},
        {"hour": "09:00", "usage": 5.0},
        {"hour": "10:00", "usage": 5.4},
        {"hour": "11:00", "usage": 5.8}
    ]