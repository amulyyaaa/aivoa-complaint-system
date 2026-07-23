from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models  # noqa: F401  (ensures models are registered before create_all)
from app.config import settings
from app.api import chat, upload, complaints

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AIVOA Customer Complaint Management API",
    description="AI-powered pharmaceutical customer complaint intake, built with FastAPI + LangGraph + Groq.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(complaints.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "AIVOA Customer Complaint Management API"}


@app.get("/debug")
def debug():
    return {
        "frontend_origin": settings.FRONTEND_ORIGIN
    }


@app.get("/health")
def health():
    return {"status": "healthy"}