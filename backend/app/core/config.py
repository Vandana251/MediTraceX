"""
MediTraceX Core Production Configuration Settings
Supports environment variable overrides for Cloud & Local deployment.
"""

import os
from typing import List
from pydantic import BaseModel

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

settings = Settings()
