from fastapi import FastAPI, Depends

# ✅ FIXED: removed 'app.' prefix — we're already inside the app/ folder
from routes import router
from auth_middleware import get_current_user

app = FastAPI()

app.include_router(router)  # ✅ registers /login before OAuth2 scheme reads tokenUrl

@app.get("/profile")
def profile(user=Depends(get_current_user)):
    return {
        "message": "Access Granted",
        "user": user
    }