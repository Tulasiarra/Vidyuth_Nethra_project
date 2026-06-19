from fastapi import HTTPException
from app.db.connection import SessionLocal
from app.db.models import Home

def validate_home_access(user_email: str, home_id: str):
    """
    Validates that the user has access to the specified home by checking the database.
    """
    db = SessionLocal()
    try:
        home = db.query(Home).filter(Home.id == home_id, Home.user_email == user_email).first()
        if not home:
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied: User does not have access to home '{home_id}'"
            )
    finally:
        db.close()
