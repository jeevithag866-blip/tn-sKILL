from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from the project root.
load_dotenv(BASE_DIR / ".env")


class Settings:
    app_name: str = os.getenv("APP_NAME", "LegalEase")

    gemini_api_key: str = os.getenv(
        "GEMINI_API_KEY",
        ""
    ).strip()

    gemini_model: str = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.8-flash"
    ).strip()

    gemini_fallback_model: str = os.getenv(
        "GEMINI_FALLBACK_MODEL",
        ""
    ).strip()

    backend_url: str = os.getenv(
        "BACKEND_URL",
        "http://127.0.0.1:8000"
    ).rstrip("/")

    max_terms: int = int(
        os.getenv("MAX_TERMS", "40")
    )

    cors_origins: list[str] = [
        item.strip()
        for item in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:8501,http://127.0.0.1:8501",
        ).split(",")
        if item.strip()
    ]

    @property
    def gemini_configured(self) -> bool:
        return bool(self.gemini_api_key)


settings = Settings()