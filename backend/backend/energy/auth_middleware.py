from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.jwt_handler import verify_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token"
)

def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    try:
        return verify_token(token)

    except:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )