import os
import httpx
from dotenv import load_dotenv
from app.db.connection import SessionLocal
from app.db.models import User

# Load root .env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL", "https://ngfkgavqefymfgfvgsps.supabase.co")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")

def register_user(data):
    try:
        # 1. Sign up on Supabase Auth
        url = f"{SUPABASE_URL}/auth/v1/signup"
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json"
        }
        body = {
            "email": data.email,
            "password": data.password,
            "options": {
                "data": {
                    "full_name": data.name
                }
            }
        }
        
        response = httpx.post(url, headers=headers, json=body)
        
        if response.status_code != 200:
            err_msg = response.json().get("msg", "Registration failed")
            return {"success": False, "message": err_msg}
            
        res_data = response.json()
        
        # 2. Sync to local database
        db = SessionLocal()
        try:
            # Check if user already in local DB
            existing = db.query(User).filter(User.email == data.email).first()
            if not existing:
                new_user = User(
                    name=data.name,
                    email=data.email,
                    phone_number=getattr(data, "phone", None),
                    password_hash="", # Password is managed by Supabase, local hash empty for safety
                    notification_preferences="all"
                )
                db.add(new_user)
                db.commit()
        except Exception as local_err:
            print(f"Failed to sync user to local DB: {local_err}")
        finally:
            db.close()
            
        return {"success": True, "message": "Registration successful"}
    except Exception as e:
        return {"success": False, "message": f"Server error: {str(e)}"}

def login_user(data):
    try:
        # Sign in on Supabase Auth
        url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json"
        }
        body = {
            "email": data.email,
            "password": data.password
        }
        
        response = httpx.post(url, headers=headers, json=body)
        
        if response.status_code != 200:
            err_msg = response.json().get("error_description", "Invalid login credentials")
            return {"success": False, "message": err_msg}
            
        res_data = response.json()
        token = res_data.get("access_token")
        
        # Store user info locally if not exists
        db = SessionLocal()
        try:
            existing = db.query(User).filter(User.email == data.email).first()
            if not existing:
                # Retrieve user name from user object
                user_info = res_data.get("user", {})
                user_metadata = user_info.get("user_metadata", {})
                name = user_metadata.get("full_name", data.email.split("@")[0].capitalize())
                
                new_user = User(
                    name=name,
                    email=data.email,
                    phone_number=None,
                    password_hash="",
                    notification_preferences="all"
                )
                db.add(new_user)
                db.commit()
        except Exception as local_err:
            print(f"Failed to sync user on login: {local_err}")
        finally:
            db.close()
            
        return {"success": True, "token": token}
    except Exception as e:
        return {"success": False, "message": f"Server error: {str(e)}"}