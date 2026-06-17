import sys
import os
from fastapi import FastAPI, Depends

# Ensure the backend root is in Python's search path
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# App imports
from app.routes import router
from app.auth_middleware import get_current_user

# Sessions module
from sessions.routes import router as sessions_router

# Energy module
from energy.routes import router as energy_router

app = FastAPI(
    title="Vidyuth Nethra API"
)

# Register Routers
app.include_router(router)

app.include_router(
    energy_router
)

app.include_router(
    sessions_router,
    prefix="/sessions",
    tags=["Sessions"]
)

@app.get("/profile")
def profile(user=Depends(get_current_user)):
    return {
        "message": "Access Granted",
        "user": user
    }

from database import supabase

@app.get("/db-test")
def db_test():

    data = (
        supabase
        .table("users")
        .select("*")
        .limit(5)
        .execute()
    )

    return data.data