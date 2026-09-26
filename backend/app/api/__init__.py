"""
MediTraceX API Routers Bundle
"""

from fastapi import APIRouter
from backend.app.api.auth import router as auth_router
from backend.app.api.medicines import router as medicines_router
from backend.app.api.pharmacies import router as pharmacies_router
from backend.app.api.inventory import router as inventory_router
from backend.app.api.predictions import router as predictions_router
from backend.app.api.requests import router as requests_router
from backend.app.api.watchlist import router as watchlist_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(medicines_router)
api_router.include_router(pharmacies_router)
api_router.include_router(inventory_router)
api_router.include_router(predictions_router)
api_router.include_router(requests_router)
api_router.include_router(watchlist_router)
