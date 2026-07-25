from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.user import router as users_router
from app.core.config import settings

app = FastAPI(
    title="MediNova AI",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "MediNova AI Backend is Running",
        "database": settings.DATABASE_URL,
    }


app.include_router(auth_router)
app.include_router(users_router)