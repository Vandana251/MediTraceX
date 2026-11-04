"""
Geospatial Location Search & Geocoding API Router
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Any

from backend.app.core.database import get_db
from backend.app.schemas.location_schemas import LocationSearchResponse
from backend.app.services.location_service import location_service

router = APIRouter(prefix="/locations", tags=["Location Search & Geocoding"])

@router.get("/search", response_model=LocationSearchResponse, summary="Search and geocode Indian localities, pincodes, landmarks, and pharmacy names")
def search_location(
    q: str = Query(..., min_length=2, description="Location query (e.g. 'Patamata', 'Benz Circle', '520010', 'Indiranagar')"),
    limit: int = Query(default=6, ge=1, le=20, description="Max suggestions to return"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Resolves search query to verified coordinates and geographic metadata:
    1. Direct Indian pincode matching (e.g. 520010, 520011, 560034)
    2. High-precision Indian locality & landmark resolution (e.g. Patamata, Labbipet, Currency Nagar)
    3. Pharmacy shop name matching from registered database
    4. Real-time OpenStreetMap / Nominatim fallback
    """
    results = location_service.search_location(query=q, db=db, limit=limit)
    return LocationSearchResponse(
        query=q,
        total=len(results),
        results=results
    )
