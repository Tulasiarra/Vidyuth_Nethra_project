from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.jwt_handler import verify_token

# ✅ tokenUrl matches the new /token route
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = verify_token(token)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid or expired token: {str(e)}"
        )