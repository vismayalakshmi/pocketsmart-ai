import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash",
    )
    session_secret: str = os.getenv(
        "SESSION_SECRET",
        "dev-only-change-me",
    )
    database_path: str = os.getenv(
        "DATABASE_PATH",
        "pocketsmart.db",
    )
    demo_mode: bool = os.getenv(
        "DEMO_MODE",
        "true",
    ).lower() in {"1", "true", "yes", "on"}


settings = Settings()