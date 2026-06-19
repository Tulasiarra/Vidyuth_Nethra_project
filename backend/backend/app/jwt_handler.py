import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "my_secret_key"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    payload = data.copy()
    # ✅ FIXED: utcnow() deprecated in Python 3.12+
    payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=24)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])