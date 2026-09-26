"""
Nearby Pharmacy Discovery API (Powered by Step 2 Min-Heap + Haversine DSA Ranker)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Any

from backend.app.core.database import get_db
from backend.app.schemas.pharmacy_schemas import NearbyPharmacySearchResponse, RankedPharmacyResponse, PharmacyBase
from backend.app.services.dsa_service import dsa_service
from backend.app.services.medicine_service import MedicineService
from backend.app.services.pharmacy_service import PharmacyService

router = APIRouter(prefix="/pharmacies", tags=["Nearby Pharmacy Discovery & DSA Ranking"])

@router.get("/nearby", response_model=NearbyPharmacySearchResponse, summary="Discover & rank nearby pharmacies for medicine using Min-Heap + Haversine")
def get_nearby_ranked_pharmacies(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="User current latitude (e.g. 17.4435)"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="User current longitude (e.g. 78.3780)"),
    medicine_id: int = Query(..., description="Target medicine ID to check availability for"),
    radius_km: float = Query(default=25.0, ge=0.5, le=100.0, description="Search radius in kilometers"),
    limit: int = Query(default=10, ge=1, le=50, description="Max ranked pharmacies to return"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Ranks nearby physical pharmacies for the requested medicine using:
    1. Availability Tier (In Stock > Low Stock > Out of Stock)
    2. Haversine Distance (Min-Heap / shortest physical distance)
    3. Stock Quantity as tie-breaker
    """
    medicine = MedicineService.get_by_id(db, medicine_id=medicine_id)
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target medicine with ID {medicine_id} not found."
        )

    ranked = dsa_service.rank_nearby_pharmacies_for_medicine(
        db=db,
        medicine_id=medicine_id,
        user_lat=latitude,
        user_lon=longitude,
        radius_km=radius_km,
        limit=limit
    )

    formatted_ranked = [
        RankedPharmacyResponse(
            rank=p.rank,
            pharmacy_id=p.pharmacy_id,
            pharmacy_name=p.pharmacy_name,
            address=p.address,
            city=p.city,
            distance_km=round(p.distance_km, 2),
            availability_status=p.stock_status,
            stock_quantity=p.stock_quantity,
            stock_freshness="Live Synced",
            safety_stock_threshold=15,
            contact_phone=p.contact_phone,
            is_24_7=p.is_24_7,
            operating_hours=f"{p.opening_time} - {p.closing_time}" if not p.is_24_7 else "Open 24/7",
            latitude=p.latitude,
            longitude=p.longitude
        )
        for p in ranked
    ]

    return NearbyPharmacySearchResponse(
        target_medicine_id=medicine.id,
        target_medicine_name=medicine.name,
        user_latitude=latitude,
        user_longitude=longitude,
        search_radius_km=radius_km,
        total_found=len(formatted_ranked),
        ranked_pharmacies=formatted_ranked
    )

@router.get("/{pharmacy_id}", response_model=PharmacyBase, summary="Get pharmacy details by ID")
def get_pharmacy_by_id(pharmacy_id: int, db: Session = Depends(get_db)) -> Any:
    pharmacy = PharmacyService.get_by_id(db, pharmacy_id=pharmacy_id)
    if not pharmacy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pharmacy with ID {pharmacy_id} not found."
        )
    return pharmacy

@router.get("", response_model=List[PharmacyBase], summary="List all active pharmacies")
def list_pharmacies(db: Session = Depends(get_db)) -> Any:
    return PharmacyService.get_all_active(db)
