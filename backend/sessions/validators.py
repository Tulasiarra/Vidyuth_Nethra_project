import uuid
from fastapi import HTTPException
from database import supabase

def get_uuid_from_home_id(home_id: str) -> str:
    """
    Resolves any home_id (like 'home_123' or a raw string) to a valid UUID string.
    If it's already a valid UUID, returns it. Otherwise, derives a deterministic UUID.
    """
    try:
        return str(uuid.UUID(home_id))
    except ValueError:
        clean_id = home_id
        if home_id.startswith("home_"):
            clean_id = home_id[5:]
        try:
            return str(uuid.UUID(clean_id))
        except ValueError:
            # Deterministic UUID mapping based on string name
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, home_id))

def validate_home_access(user_email: str, home_id: str) -> str:
    """
    Validates home access for the given user email and home_id.
    Returns the resolved household_id (UUID string).
    """
    home_uuid = get_uuid_from_home_id(home_id)

    try:
        # Get user_id from email
        user_res = supabase.table("users").select("user_id").eq("email", user_email).execute()
        if not user_res.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = user_res.data[0]["user_id"]

        # Check if the household exists in the database
        house_res = supabase.table("households").select("*").eq("household_id", home_uuid).execute()
        
        if not house_res.data:
            # Check if user has any households at all
            all_house_res = supabase.table("households").select("*").eq("user_id", user_id).execute()
            if not all_house_res.data:
                # If this user has no households, automatically create a default one for them
                clean_name = home_id.replace("_", " ").title() if "_" in home_id else f"{home_id.title()} Household"
                supabase.table("households").insert({
                    "household_id": home_uuid,
                    "user_id": user_id,
                    "household_name": clean_name,
                    "location": "Default Location"
                }).execute()
            else:
                # User owns other households, but not this one. Deny access.
                raise HTTPException(
                    status_code=403,
                    detail=f"Access Denied: User does not have access to household '{home_id}'"
                )
        else:
            # Household exists, verify user ownership
            household = house_res.data[0]
            if household["user_id"] != user_id:
                raise HTTPException(
                    status_code=403,
                    detail=f"Access Denied: Household '{home_id}' belongs to another user"
                )

        return home_uuid

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error during validation: {str(e)}"
        )
