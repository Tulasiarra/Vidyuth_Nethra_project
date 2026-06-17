from app.password_utils import hash_password, verify_password
from app.jwt_handler import create_access_token
from database import supabase

def register_user(data):
    hashed_password = hash_password(data.password)

    try:
        # Check if email already exists
        existing_user = (
            supabase
            .table("users")
            .select("*")
            .eq("email", data.email)
            .execute()
        )

        if existing_user.data:
            return {
                "success": False,
                "message": "User already registered"
            }

        # Insert user into Supabase
        response = supabase.table("users").insert({
            "full_name": data.name,
            "email": data.email,
            "password_hash": hashed_password
        }).execute()

        if response.data:
            return {
                "success": True,
                "message": "User registered"
            }
        else:
            return {
                "success": False,
                "message": "Failed to store user in database"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Database error: {str(e)}"
        }


def login_user(data):
    try:
        # Fetch user by email
        response = (
            supabase
            .table("users")
            .select("*")
            .eq("email", data.email)
            .execute()
        )

        if not response.data:
            return {
                "success": False,
                "message": "User not found"
            }

        user = response.data[0]

        # Verify password
        if not verify_password(data.password, user["password_hash"]):
            return {
                "success": False,
                "message": "Invalid password"
            }

        # Create JWT token
        token = create_access_token({"email": user["email"]})
        return {
            "success": True,
            "token": token
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Database error: {str(e)}"
        }