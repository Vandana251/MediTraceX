"""
=============================================================================
MediTraceX: Intelligent Medicine Availability & Pharmacy Discovery Platform
FastAPI REST API Server Entrypoint (Production & Cloud Ready)
=============================================================================
"""

import sys
import os
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.core.config import settings
from backend.app.core.database import SessionLocal, engine
from backend.app.services.dsa_service import dsa_service
from backend.app.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown event handler.
    Initializes the in-memory Trie prefix search index from the database.
    """
    print("\n" + "="*78)
    print(" 🚀 Starting MediTraceX REST API Server...")
    print(f"    • Environment   : {settings.ENVIRONMENT.upper()}")
    print(f"    • Database Type : {settings.DB_TYPE.upper()}")
    print("    • Initializing in-memory Trie DSA search engine from database...")
    db = SessionLocal()
    try:
        count = dsa_service.initialize_trie(db)
        print(f"    • Loaded and indexed {count} medicines into Trie prefix tree.")
    except Exception as e:
        print(f"    • [Warning] Trie index initialization deferred: {e}")
    finally:
        db.close()
    print("    • Server ready to accept client connections.")
    print("="*78 + "\n")
    yield
    print(" 🛑 Shutting down MediTraceX REST API Server...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Production-ready backend REST API for **MediTraceX – Intelligent Medicine Availability & Pharmacy Discovery Platform**.\n\n"
        "Tagline: **Find. Verify. Reach.**\n\n"
        "Integrates:\n"
        "- **DSA Engine**: Sub-millisecond Prefix Trie Search, Levenshtein Typo Recovery, and Min-Heap Haversine Pharmacy Discovery.\n"
        "- **ML Engine**: Time-series Demand Forecasting and Stock-out Risk Assessment.\n"
        "- **Secure Relational DB**: Real-time multi-pharmacy inventory and transactional management."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Cross-Origin Resource Sharing (CORS) Middleware for Mobile / Client Apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach API routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["System Health"], summary="Root service metadata")
def root_endpoint() -> Dict[str, Any]:
    return {
        "service": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "status": "OPERATIONAL",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "database": settings.DB_TYPE,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_v1_prefix": settings.API_V1_STR
    }

@app.get("/health", tags=["System Health"], summary="Healthcheck probe for cloud orchestrators")
def healthcheck() -> Dict[str, Any]:
    # Check DB live connection
    db_status = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    is_healthy = (db_status == "connected")
    return {
        "status": "healthy" if is_healthy else "degraded",
        "health": "ok" if is_healthy else "degraded",
        "database": db_status,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=(settings.ENVIRONMENT == "development")
    )
