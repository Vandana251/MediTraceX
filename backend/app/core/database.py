"""
MediTraceX Database Session Dependency for FastAPI
"""

import sys
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db_config import engine, SessionLocal, get_db

__all__ = ["engine", "SessionLocal", "get_db"]
