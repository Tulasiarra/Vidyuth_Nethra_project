import jwt
from datetime import datetime, timedelta, timezone
from app.config import SECRET_KEY, ALGORITHM

# Fallback values if not specified in configuration
JWT_SECRET = SECRET_KEY or "my_secret_key"
JWT_ALGORITHM = ALGORITHM or "HS256"

def create_access_token(data: dict):
    payload = data.copy()
    # ✅ FIXED: utcnow() deprecated in Python 3.12+
    payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=24)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str):
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])