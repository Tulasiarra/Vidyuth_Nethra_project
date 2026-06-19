import os
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.connection import get_db
from app.db.models import Home, Device
from app.auth_middleware import get_current_user
from app.api.devices import toggle_device
from energy.service import get_energy_summary
from energy.prediction import predict_usage
from pydantic import BaseModel

router = APIRouter(prefix="/voice", tags=["Voice Assistant"])

class VoiceCommandSchema(BaseModel):
    home_id: str
    command: str

def classify_voice_intent(command: str) -> dict:
    """
    Calls Groq to classify the voice command intent and extract parameters.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is missing. Voice assistant LLM intent classification is disabled."
        )
        
    try:
        from groq import Groq
        client = Groq(api_key=groq_api_key)
        
        system_prompt = (
            "You are a smart home intent classifier. Classify the user's voice command into one of the following intents:\n"
            "- toggle_on: Turn a device ON (e.g., 'Turn on living room AC')\n"
            "- toggle_off: Turn a device OFF (e.g., 'Switch off kitchen fan')\n"
            "- query_usage: Ask about energy consumption or electricity usage (e.g., 'Show current usage')\n"
            "- query_bill: Ask about bills, costs, or budget (e.g., 'Show current bill')\n"
            "- query_top_device: Ask about the highest/top consuming device (e.g., 'Show top consuming device')\n"
            "- query_prediction: Ask about energy predictions or forecasts (e.g., 'Predict next week's usage')\n"
            "- fallback: Unknown command or unsupported action\n\n"
            "Also extract parameters:\n"
            "- device_type: The normalized category of the device mentioned (e.g., 'ac', 'fan', 'light', 'fridge', 'geyser', etc.)\n"
            "- room_name: The room mentioned (e.g., 'living room', 'bedroom', 'kitchen', 'bathroom', 'utility', etc.)\n\n"
            "Response MUST be a valid JSON object only, with keys: 'intent', 'device_type', 'room_name'. Do not write any explanation."
        )
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Command: '{command}'"}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        result_str = completion.choices[0].message.content
        return json.loads(result_str)
    except Exception as e:
        print(f"Voice LLM Intent classification failed: {e}")
        # Return fallback dict if call fails
        return {"intent": "fallback", "device_type": None, "room_name": None}

@router.post("/command")
def process_voice_command(data: VoiceCommandSchema, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_email = current_user["email"]
    home_id = data.home_id
    command_text = data.command
    
    # Verify access to home
    home = db.query(Home).filter(Home.id == home_id, Home.user_email == user_email).first()
    if not home:
        raise HTTPException(status_code=403, detail="Access denied")
        
    # Classify intent using Groq
    classification = classify_voice_intent(command_text)
    intent = classification.get("intent", "fallback")
    detected_type = classification.get("device_type")
    detected_room = classification.get("room_name")
    
    # Execute actions based on intent
    if intent in ["toggle_on", "toggle_off"]:
        target_status = "ON" if intent == "toggle_on" else "OFF"
        
        if not detected_type:
            return {
                "response": f"I understood you want to turn a device {target_status.lower()}, but I couldn't identify the device category. Try saying 'turn on the AC' or 'turn off bedroom light'.",
                "intent": "toggle_device_unknown",
                "refresh_required": False
            }
            
        # Query device
        query = db.query(Device).filter(Device.home_id == home_id)
        
        # Normalize category
        mapped_type = detected_type
        if detected_type == "refrigerator":
            mapped_type = "fridge"
        elif detected_type == "television":
            mapped_type = "tv"
            
        query = query.filter(func.lower(Device.device_type) == mapped_type.lower())
        
        if detected_room:
            query = query.filter(func.lower(Device.room_name) == detected_room.lower())
            
        devices_found = query.all()
        
        if not devices_found:
            room_clause = f" in the {detected_room}" if detected_room else ""
            return {
                "response": f"I couldn't find any {detected_type}{room_clause} registered in your home.",
                "intent": "toggle_device_not_found",
                "refresh_required": False
            }
            
        # Toggle the first matching device
        target_device = devices_found[0]
        res = toggle_device(device_id=target_device.id, status=target_status, db=db, current_user=current_user)
        
        status_action = "turned on" if target_status == "ON" else "turned off"
        room_desc = f"in the {target_device.room_name}" if target_device.room_name else ""
        return {
            "response": f"Ok, I've {status_action} the {target_device.name} {room_desc}.",
            "intent": intent,
            "device_id": target_device.id,
            "device_name": target_device.name,
            "status": target_status,
            "refresh_required": True
        }
        
    elif intent == "query_usage":
        summary = get_energy_summary(home_id)
        if "error" not in summary:
            return {
                "response": f"Your home consumption today is {summary['today']['energy_kwh']} kWh, and this month is {summary['monthly']['energy_kwh']} kWh.",
                "intent": intent,
                "refresh_required": False
            }
            
    elif intent == "query_bill":
        summary = get_energy_summary(home_id)
        pred = predict_usage(home_id)
        
        if "error" not in summary and "error" not in pred:
            target = summary["target_bill"]
            est = pred["monthly"]["cost"]
            return {
                "response": f"Your current monthly cost is ₹{summary['monthly']['cost']}. The estimated bill for this month is ₹{est} against your target of ₹{target}.",
                "intent": intent,
                "refresh_required": False
            }
            
    elif intent == "query_top_device":
        summary = get_energy_summary(home_id)
        if "error" not in summary:
            top_dev = summary["top_consuming_device"]
            return {
                "response": f"The highest consuming device in your home is the {top_dev['name']}, using {top_dev['usage_kwh']} kWh this month.",
                "intent": intent,
                "refresh_required": False
            }
            
    elif intent == "query_prediction":
        pred = predict_usage(home_id)
        if "error" not in pred:
            return {
                "response": f"AI forecasts your energy bill to be ₹{pred['weekly']['cost']} next week and ₹{pred['monthly']['cost']} next month.",
                "intent": intent,
                "refresh_required": False
            }
            
    # Default fallback response
    return {
        "response": "I didn't quite catch that. You can ask me to turn devices on/off, predict next month's bill, show usage, or list the highest consuming device.",
        "intent": "fallback",
        "refresh_required": False
    }
