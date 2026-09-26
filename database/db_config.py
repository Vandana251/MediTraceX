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
import ssl
from urllib.parse import quote_plus, urlparse, parse_qs, urlencode, urlunparse
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
    """
    Builds a standardized SQLAlchemy MySQL connection URL.
    - Converts mysql:// scheme to mysql+pymysql://
    - Strips driver-incompatible query parameters (ssl-mode, sslmode, ssl_mode)
    - Preserves all other valid query parameters
    """
    if DATABASE_URL and ("mysql" in DATABASE_URL.lower()):
        raw_url = DATABASE_URL
        if raw_url.startswith("mysql://"):
            raw_url = raw_url.replace("mysql://", "mysql+pymysql://", 1)
        elif not raw_url.startswith("mysql+pymysql://") and raw_url.startswith("mysql"):
            raw_url = "mysql+pymysql://" + raw_url.split("://", 1)[-1]

        parsed = urlparse(raw_url)
        if parsed.query:
            query_params = parse_qs(parsed.query)
            # Remove ssl-mode / sslmode / ssl_mode which cause PyMySQL TypeError
            filtered_params = {
                k: v for k, v in query_params.items()
                if k.lower() not in ("ssl-mode", "sslmode", "ssl_mode")
            }
            new_query = urlencode(filtered_params, doseq=True)
            return urlunparse(parsed._replace(query=new_query))
        return raw_url

    # Fallback to discrete environment variables
    safe_password = quote_plus(MYSQL_PASSWORD) if MYSQL_PASSWORD else ""
    return f"mysql+pymysql://{MYSQL_USER}:{safe_password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

def get_mysql_connect_args() -> dict:
    """
    Constructs PyMySQL-compatible SSL connection arguments.
    Enables TLS for remote cloud MySQL providers (e.g. Aiven, AWS RDS, PlanetScale).
    """
    connect_args = {}
    is_remote_host = (
        (MYSQL_HOST and MYSQL_HOST not in ("localhost", "127.0.0.1", "mysql")) or
        (DATABASE_URL and not any(local in DATABASE_URL.lower() for local in ("@localhost", "@127.0.0.1", "@mysql")))
    )

    has_ssl_hint = False
    if DATABASE_URL:
        db_lower = DATABASE_URL.lower()
        if any(term in db_lower for term in ("ssl", "aiven", "rds", "railway", "planetscale")):
            has_ssl_hint = True

    if is_remote_host or has_ssl_hint or (ENVIRONMENT == "production" and DB_TYPE == "mysql"):
        try:
            # Use standard SSLContext which validates trusted public CAs (Aiven, Let's Encrypt, etc.)
            ssl_context = ssl.create_default_context()
            connect_args["ssl"] = ssl_context
        except Exception:
            connect_args["ssl"] = {"check_hostname": False}

    return connect_args

def get_engine() -> Engine:
    """
    Initializes the SQLAlchemy Database Engine based on environment and DB_TYPE.
    - Production: MySQL with connection pooling (pool_size=10, max_overflow=20, pool_recycle=1800, pool_pre_ping=True)
    - Development / Testing: SQLite fallback (meditracex.db)
    """
    if DB_TYPE == "mysql" or ENVIRONMENT == "production" or (DATABASE_URL and "mysql" in DATABASE_URL.lower()):
        mysql_url = build_mysql_url()
        mysql_connect_args = get_mysql_connect_args()
        try:
            engine = create_engine(
                mysql_url,
                connect_args=mysql_connect_args,
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
