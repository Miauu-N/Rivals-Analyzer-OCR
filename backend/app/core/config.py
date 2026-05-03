from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Rivals Replay Analyzer"
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    UPLOAD_DIR: str = "uploads"
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
