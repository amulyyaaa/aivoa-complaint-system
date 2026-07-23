"""
Application configuration.
All values are read from environment variables (see .env.example).
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # --- Database ---
    # Works with either Postgres or MySQL. Example values:
    # Postgres: postgresql+psycopg2://user:password@localhost:5432/aivoa_complaints
    # MySQL:    mysql+pymysql://user:password@localhost:3306/aivoa_complaints
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite:///./aivoa_complaints.db"  # local fallback for quick demo
    )

    # --- Groq / LLM ---
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GROQ_FALLBACK_MODEL: str = os.getenv(
    "GROQ_FALLBACK_MODEL",
    "llama-3.1-8b-instant"
)

    # --- CORS ---
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "")

    # --- Uploads ---
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")


settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
