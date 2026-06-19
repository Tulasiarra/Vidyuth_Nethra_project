from security import hash_password, verify_password
from jwt_handler import create_token

users = {}
def register(name, email, password):

    if email in users:
        return {"error": "User already exists"}

    users[email] = {
        "name": name,
        "email": email,
        "password": hash_password(password)
    }

    return {"message": "User registered successfully"}
def register(name, email, password):

    if email in users:
        return {"error": "User already exists"}

    users[email] = {
        "name": name,
        "email": email,
        "password": hash_password(password)
    }

    return {"message": "User registered successfully"}
def login(email, password):

    user = users.get(email)

    if not user:
        return {"error": "User not found"}

    if not verify_password(password, user["password"]):
        return {"error": "Wrong password"}

    token = create_token({"email": email})

    return {"token": token}