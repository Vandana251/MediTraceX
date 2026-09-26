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
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url, URL
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

def build_mysql_url():
    """
    Builds and sanitizes a SQLAlchemy URL object for MySQL.
    - Parses DATABASE_URL safely using SQLAlchemy's make_url
    - Converts drivername to mysql+pymysql
    - Removes only incompatible query parameters: ssl-mode, sslmode, ssl_mode
    - Preserves normal parameters such as charset
    - Returns (url_object, removed_params_list)
    """
    if DATABASE_URL and ("mysql" in DATABASE_URL.lower()):
        url_obj = make_url(DATABASE_URL)
        if not url_obj.drivername.startswith("mysql+pymysql"):
            url_obj = url_obj.set(drivername="mysql+pymysql")

        # Safely remove only incompatible SSL query parameters from the URL
        query_dict = dict(url_obj.query)
        removed_params = [
            k for k in list(query_dict.keys())
            if k.lower() in ("ssl-mode", "sslmode", "ssl_mode")
        ]
        for k in removed_params:
            del query_dict[k]

        cleaned_url = url_obj.set(query=query_dict)
        return cleaned_url, removed_params

    # Fallback to discrete environment variables
    safe_password = quote_plus(MYSQL_PASSWORD) if MYSQL_PASSWORD else ""
    raw_str = f"mysql+pymysql://{MYSQL_USER}:{safe_password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    return make_url(raw_str), []

def get_mysql_connect_args() -> tuple[dict, str]:
    """
    Constructs PyMySQL-compatible SSL connection arguments.
    Enables TLS for remote cloud MySQL providers (e.g. Aiven, AWS RDS, PlanetScale).
    Resolves CA certificates from:
      1. MYSQL_SSL_CA / SSL_CA_PATH environment variable (file path)
      2. Project certs directory (certs/aiven_ca.pem, certs/ca.pem, database/ca.pem)
      3. Render secret files (/etc/secrets/ca.pem, /etc/secrets/aiven_ca.pem)
      4. MYSQL_SSL_CA_CONTENT / AIVEN_CA_CERT environment variable (raw PEM text)
      5. System default trusted CAs (fallback)
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

    ca_source = "None"
    if is_remote_host or has_ssl_hint or (ENVIRONMENT == "production" and DB_TYPE == "mysql"):
        ssl_context = ssl.create_default_context()
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.check_hostname = True
        ca_source = "System Default Trust Store"

        # Check candidate file paths
        ca_env_path = os.getenv("MYSQL_SSL_CA", os.getenv("SSL_CA_PATH", "")).strip()
        ca_content = os.getenv("MYSQL_SSL_CA_CONTENT", os.getenv("AIVEN_CA_CERT", "")).strip()

        candidate_paths = []
        if ca_env_path:
            candidate_paths.append(ca_env_path)

        candidate_paths.extend([
            os.path.join(PROJECT_ROOT, "certs", "aiven_ca.pem"),
            os.path.join(PROJECT_ROOT, "certs", "ca.pem"),
            os.path.join(PROJECT_ROOT, "database", "ca.pem"),
            "/etc/secrets/ca.pem",
            "/etc/secrets/aiven_ca.pem"
        ])

        ca_file_found = None
        for p in candidate_paths:
            if p and os.path.isfile(p):
                ca_file_found = p
                break

        if ca_file_found:
            ssl_context.load_verify_locations(cafile=ca_file_found)
            ca_source = f"File ({os.path.basename(ca_file_found)})"
        elif ca_content:
            ssl_context.load_verify_locations(cadata=ca_content)
            ca_source = "Environment Variable (MYSQL_SSL_CA_CONTENT)"

        connect_args["ssl"] = ssl_context

    return connect_args, ca_source

def get_engine() -> Engine:
    """
    Initializes the SQLAlchemy Database Engine based on environment and DB_TYPE.
    - Production: MySQL with connection pooling (pool_size=10, max_overflow=20, pool_recycle=1800, pool_pre_ping=True)
    - Development / Testing: SQLite fallback (meditracex.db)
    """
    if DB_TYPE == "mysql" or ENVIRONMENT == "production" or (DATABASE_URL and "mysql" in DATABASE_URL.lower()):
        mysql_url, removed_params = build_mysql_url()
        mysql_connect_args, ca_source = get_mysql_connect_args()

        # Safe non-secret diagnostics
        print(f"[Database Config] Initializing MySQL Engine:")
        print(f"  • Driver: {mysql_url.drivername}")
        print(f"  • SSL connect argument configured: {'ssl' in mysql_connect_args}")
        print(f"  • CA certificate source: {ca_source}")
        if removed_params:
            print(f"  • Removed incompatible URL query parameters: {', '.join(removed_params)}")
        if mysql_url.query:
            print(f"  • Preserved URL parameters: {', '.join(mysql_url.query.keys())}")

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
            print(f"[Database] Successfully connected to MySQL Database")
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

