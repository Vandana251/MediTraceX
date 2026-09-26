"""
=============================================================================
MediTraceX Database Connection & Session Manager
=============================================================================
Supports:
- Production: Enterprise MySQL with connection pooling, keepalive, and pre-ping
- Development / Testing: Lightweight SQLite fallback
=============================================================================
"""

import sys
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine

# Root paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meditracex.db")

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", os.getenv("ENV", "development")).lower()
DB_TYPE = os.getenv("DB_TYPE", "mysql" if ENVIRONMENT == "production" else "sqlite").lower()

# MySQL parameters
DATABASE_URL = os.getenv("DATABASE_URL", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "meditracex_db")

Base = declarative_base()

def build_mysql_url() -> str:
    """Builds a standardized SQLAlchemy MySQL connection URL."""
    if DATABASE_URL and ("mysql" in DATABASE_URL.lower()):
        url = DATABASE_URL
        # If bare mysql:// is supplied, map to mysql+pymysql://
        if url.startswith("mysql://"):
            url = url.replace("mysql://", "mysql+pymysql://", 1)
        return url

    # Fallback to discrete environment variables
    safe_password = quote_plus(MYSQL_PASSWORD) if MYSQL_PASSWORD else ""
    return f"mysql+pymysql://{MYSQL_USER}:{safe_password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

def get_engine() -> Engine:
    """
    Initializes the SQLAlchemy Database Engine based on environment and DB_TYPE.
    - Production: MySQL with connection pooling (pool_size=10, max_overflow=20, pool_recycle=1800, pool_pre_ping=True)
    - Development / Testing: SQLite fallback (meditracex.db)
    """
    if DB_TYPE == "mysql" or ENVIRONMENT == "production" or (DATABASE_URL and "mysql" in DATABASE_URL.lower()):
        mysql_url = build_mysql_url()
        try:
            engine = create_engine(
                mysql_url,
                pool_size=10,
                max_overflow=20,
                pool_recycle=1800,
                pool_pre_ping=True
            )
            # Test connectivity if not during cold build/dry run
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"[Database] Successfully connected to MySQL Database ({MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE})")
            return engine
        except Exception as e:
            if ENVIRONMENT == "production":
                raise RuntimeError(
                    f"Production MySQL connection failed: {e}. Ensure DATABASE_URL or (MYSQL_HOST, MYSQL_USER, "
                    f"MYSQL_PASSWORD, MYSQL_DATABASE) are properly configured in environment variables."
                ) from e
            else:
                print(f"[Warning] MySQL connection could not be established ({e}). Falling back to development SQLite database at {SQLITE_PATH}")

    # Development / Testing SQLite Database
    sqlite_url = DATABASE_URL if (DATABASE_URL and "sqlite" in DATABASE_URL.lower()) else f"sqlite:///{SQLITE_PATH}"
    engine = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False}
    )
    return engine

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """FastAPI database dependency provider."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
