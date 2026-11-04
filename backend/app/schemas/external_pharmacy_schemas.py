from typing import List, Optional
from pydantic import BaseModel, Field


class ExternalPharmacyItem(BaseModel):
    name: str = Field(..., description="Pharmacy / medical shop name")
    address: Optional[str] = Field(None, description="Street address or locality if available")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    distance_km: float = Field(..., description="Haversine distance from search location in km")
    phone: Optional[str] = Field(None, description="Contact phone number if available")
    opening_hours: Optional[str] = Field(None, description="Opening hours if available")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State name")
    pincode: Optional[str] = Field(None, description="Pincode if available")
    source: str = Field("OpenStreetMap Overpass", description="Data provider source")
    verification_status: str = Field("Inventory Not Verified", description="Status of stock verification")
    is_verified_network: bool = Field(False, description="Whether this pharmacy is an integrated MediTraceX partner")
    osm_id: Optional[str] = Field(None, description="OpenStreetMap node or way identifier")


class ExternalPharmacyResponse(BaseModel):
    search_latitude: float
    search_longitude: float
    radius_km: float
    total_found: int
    data_notice: str = "Nearby pharmacies found from connected location data. Medicine availability is shown only for pharmacies with verified MediTraceX inventory."
    results: List[ExternalPharmacyItem]
