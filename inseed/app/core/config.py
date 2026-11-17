from pydantic_settings import BaseSettings
from pydantic import ValidationError
import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """
    Application settings and environment variable management.
    Handles database connection strings, security secrets, and token expiration.
    """
    PROJECT_NAME: str = "Inseed"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(48))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days in minutes

    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "inseed_db")
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "SQLALCHEMY_DATABASE_URI", f"sqlite:///./{POSTGRES_DB}.db"
    )

    class Config:
        case_sensitive = True

try:
    settings = Settings()
except ValidationError as e:
    import sys
    sys.exit(f"Error loading settings: {e}")