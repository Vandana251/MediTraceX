"""
Medicine Discovery & Catalog API Routes (Powered by Step 2 DSA Trie Engine)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Any

from backend.app.core.database import get_db
from backend.app.schemas.medicine_schemas import MedicineBase, MedicineSearchResponse, MedicineListResponse
from backend.app.services.dsa_service import dsa_service
from backend.app.services.medicine_service import MedicineService

router = APIRouter(prefix="/medicines", tags=["Medicines & DSA Search"])

@router.get("/search", response_model=List[MedicineSearchResponse], summary="Fast Trie Prefix Search with Levenshtein Fuzzy Typo Recovery")
def search_medicines(
    q: str = Query(..., min_length=1, max_length=100, description="Search term, prefix, brand, or molecule name"),
    limit: int = Query(default=10, ge=1, le=50, description="Max results to return"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Sub-millisecond medicine search engine powered by a Prefix Trie and
    Trie-branch Levenshtein dynamic programming for typo recovery.
    """
    results = dsa_service.search_medicines(query=q, limit=limit, db=db)
    return [r.to_dict() for r in results]

@router.get("/{medicine_id}", response_model=MedicineBase, summary="Get medicine details by ID")
def get_medicine_by_id(medicine_id: int, db: Session = Depends(get_db)) -> Any:
    medicine = MedicineService.get_by_id(db, medicine_id=medicine_id)
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine with ID {medicine_id} not found."
        )
    return medicine

@router.get("", response_model=MedicineListResponse, summary="List medicines catalog with category filter & pagination")
def list_medicines(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(default=None, description="Optional therapeutic category filter"),
    db: Session = Depends(get_db)
) -> Any:
    skip = (page - 1) * page_size
    items, total = MedicineService.get_list(db, skip=skip, limit=page_size, category=category)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }
