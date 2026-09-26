"""
Pydantic Schemas for Nearby Pharmacy Discovery & Metadata
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class RankedPharmacyResponse(BaseModel):
    rank: int
    pharmacy_id: int
    pharmacy_name: str
    address: str
    city: str
    distance_km: float
    availability_status: str # "Available", "Low Stock", "Out of Stock"
    stock_quantity: int
    stock_freshness: str = "Live Synced"
    safety_stock_threshold: int = 15
    contact_phone: str
    is_24_7: bool
    operating_hours: str
    latitude: float
    longitude: float

class NearbyPharmacySearchResponse(BaseModel):
    target_medicine_id: int
    target_medicine_name: str
    user_latitude: float
    user_longitude: float
    search_radius_km: float
    total_found: int
    ranked_pharmacies: List[RankedPharmacyResponse]

class PharmacyBase(BaseModel):
    id: int
    name: str
    license_number: str
    address: str
    city: str
    pincode: str
    latitude: float
    longitude: float
    contact_phone: str
    contact_email: str
    is_24_7: bool
    is_active: bool

    class Config:
        from_attributes = True
