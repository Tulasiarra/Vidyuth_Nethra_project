import sys
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# Ensure the backend root and app directory are in Python's search path
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
app_path = os.path.join(backend_path, "app")
if app_path not in sys.path:
    sys.path.insert(0, app_path)

# Database startup
from app.db.connection import engine, Base

# Import Routers
from routes import router as auth_router
from app.api.homes import router as homes_router
from app.api.devices import router as devices_router
from app.api.reports import router as reports_router
from app.api.voice import router as voice_router
from app.api.chatbot import router as chatbot_router
from energy.routes import router as energy_router
from sessions.routes import router as sessions_router

from auth_middleware import get_current_user

# Initialize tables on startup
Base.metadata.create_all(bind=engine)

# Seed database on startup if tables are empty
from app.db.seed import seed_database
try:
    seed_database()
except Exception as e:
    print(f"Database seeding skipped or failed on startup: {e}")

app = FastAPI(
    title="Vidyuth Nethra API"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth_router)
app.include_router(homes_router)
app.include_router(devices_router)
app.include_router(reports_router)
app.include_router(voice_router)
app.include_router(chatbot_router)
app.include_router(energy_router)
app.include_router(sessions_router, prefix="/sessions", tags=["Sessions"])

@app.get("/profile")
def profile(user=Depends(get_current_user)):
    return {
        "message": "Access Granted",
        "user": user
    }