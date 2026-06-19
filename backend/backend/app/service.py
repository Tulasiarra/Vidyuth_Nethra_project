# ✅ FIXED: removed 'app.' prefix
from app.password_utils import hash_password, verify_password
from app.jwt_handler import create_access_token

users = {}

def register_user(data):
    if data.email in users:
        return {"success": False, "message": "User already exists"}

    users[data.email] = {
        "name": data.name,
        "email": data.email,
        "password": hash_password(data.password)
    }
    return {"success": True, "message": "User registered"}


def login_user(data):
    user = users.get(data.email)

    if not user:
        return {"success": False, "message": "User not found"}

    if not verify_password(data.password, user["password"]):
        return {"success": False, "message": "Invalid password"}

    token = create_access_token({"email": user["email"]})
    return {"success": True, "token": token}