"""
MediTraceX Core Production Configuration Settings
Supports environment variable overrides for Cloud & Local deployment.
"""

import os
from pathlib import Path
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

# Load root .env file
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

class Settings(BaseModel):
    PROJECT_NAME: str = "MediTraceX – Intelligent Medicine Availability & Pharmacy Discovery Platform"
    TAGLINE: str = "Find. Verify. Reach."
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", os.getenv("ENV", "development")).lower() # 'development' or 'production'
    
    # Server Binding
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Database Configuration
    DB_TYPE: str = os.getenv("DB_TYPE", "mysql" if os.getenv("ENVIRONMENT", "").lower() == "production" else "sqlite")
    
    # Direct DATABASE_URL or individual MySQL credentials
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "meditracex_db")

    # JWT Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", os.getenv("JWT_SECRET_KEY", "meditracex-development-jwt-secret-key-32chars-minimum"))
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 hours

    # CORS Allowed Origins (Comma-separated string or * for mobile clients)
    CORS_ORIGINS: List[str] = [
        origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",") if origin.strip()
    ]

    # Geospatial Defaults
    DEFAULT_SEARCH_RADIUS_KM: float = 15.0
    MAX_SEARCH_RADIUS_KM: float = 50.0

    # SMTP Mail Server Configuration (Gmail or custom SMTP)
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "MediTraceX Healthcare")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")

settings = Settings()
