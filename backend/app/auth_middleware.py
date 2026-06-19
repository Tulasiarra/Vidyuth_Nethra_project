import os
import httpx
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

# Load root .env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL", "https://ngfkgavqefymfgfvgsps.supabase.co")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
    # Fallback to query parameter "token" if Authorization header is not present
    if not token:
        token = request.query_params.get("token")
        
    if not token or token == "undefined" or token == "demo_token" or token.startswith("demo_"):
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )
    
    # Try decoding locally first
    try:
        from jwt_handler import verify_token
        payload = verify_token(token)
        if payload and "email" in payload:
            from app.db.connection import SessionLocal
            from app.db.models import User
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.email == payload["email"]).first()
                if user:
                    return {
                        "id": f"local_{user.id}",
                        "email": user.email,
                        "user_metadata": {"full_name": user.name},
                        "name": user.name
                    }
            finally:
                db.close()
    except Exception as local_err:
        pass

    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "apikey": SUPABASE_KEY
        }
        url = f"{SUPABASE_URL}/auth/v1/user"
        response = httpx.get(url, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired Supabase token"
            )
            
        user_data = response.json()
        # Ensure 'name' is in the root of returned user dict for the frontend's profile display
        user_metadata = user_data.get("user_metadata", {})
        full_name = user_metadata.get("full_name", user_data.get("email", "").split("@")[0].capitalize())
        user_data["name"] = full_name
        return user_data
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=401,
            detail=f"Token validation failed: {str(e)}"
        )