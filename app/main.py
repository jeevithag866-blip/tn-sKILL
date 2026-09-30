from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import router


app = FastAPI(
    title="LegalEase API",
    description="AI-powered legal document drafting API.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


@app.get("/", tags=["system"])
def root():

    return {
        "name": "LegalEase",
        "message": "LegalEase API is running.",
        "docs": "/docs",
    }


@app.get("/health", tags=["system"])
def health():

    return {
        "status": "ok",
        "ai_configured": settings.gemini_configured,
    }