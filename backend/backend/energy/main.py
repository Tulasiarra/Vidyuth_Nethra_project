from fastapi import FastAPI

from energy.routes import router

app = FastAPI(
    title="Energy Module API"
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "Energy Module Running"
    }