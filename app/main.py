from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ai import router as ai_router
from app.api.auth import router as auth_router
from app.api.consultation import router as consultation_router
from app.api.dashboard import router as dashboard_router
from app.api.user import router as users_router
from app.core.config import settings

from app.core.exceptions import (
    MediNovaException,
    medinova_exception_handler,
)

app = FastAPI(
    title="MediNova AI",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "MediNova AI Backend is Running",
        "database": settings.DATABASE_URL,
    }


# Register routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(ai_router)
app.include_router(consultation_router)
app.include_router(dashboard_router)


# Exception handler
app.add_exception_handler(
    MediNovaException,
    medinova_exception_handler,
)