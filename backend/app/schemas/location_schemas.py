"""
Pydantic Schemas for Location Search & Geocoding Service
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class LocationSearchResult(BaseModel):
    query: str
    display_name: str
    locality: Optional[str] = None
    city: str
    state: str
    pincode: Optional[str] = None
    latitude: float
    longitude: float
    result_type: str = "locality" # "locality", "pincode", "city", "pharmacy", "landmark"
    matched_pharmacy_id: Optional[int] = None
    is_verified_network: bool = False

class LocationSearchResponse(BaseModel):
    query: str
    total: int
    results: List[LocationSearchResult]
