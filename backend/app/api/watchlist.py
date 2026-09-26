"""
Medicine Restock Watchlist (Notify Me) API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.schemas.watchlist_schemas import WatchlistCreate, WatchlistResponse
from database.models import User, Watchlist, Medicine, Pharmacy

router = APIRouter(prefix="/watchlist", tags=["Restock Watchlist / Notify Me"])

def _format_watchlist_response(w: Watchlist) -> WatchlistResponse:
    return WatchlistResponse(
        id=w.id,
        user_id=w.user_id,
        medicine_id=w.medicine_id,
        medicine_name=w.medicine.name if w.medicine else None,
        pharmacy_id=w.target_pharmacy_id,
        pharmacy_name=w.pharmacy.name if w.pharmacy else None,
        notify_on_restock=w.notify_on_restock,
        is_active=w.is_active,
        created_at=w.created_at
    )

@router.post("", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED, summary="Subscribe to medicine restock notification (Notify Me)")
def add_to_watchlist(
    payload: WatchlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    medicine = db.query(Medicine).filter(Medicine.id == payload.medicine_id).first()
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine with ID {payload.medicine_id} not found."
        )

    if payload.pharmacy_id:
        pharmacy = db.query(Pharmacy).filter(Pharmacy.id == payload.pharmacy_id).first()
        if not pharmacy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pharmacy with ID {payload.pharmacy_id} not found."
            )

    # Check existing subscription
    existing = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id,
        Watchlist.medicine_id == payload.medicine_id,
        Watchlist.target_pharmacy_id == payload.pharmacy_id
    ).first()

    if existing:
        existing.is_active = True
        existing.notify_on_restock = payload.notify_on_restock
        db.commit()
        db.refresh(existing)
        return _format_watchlist_response(existing)

    item = Watchlist(
        user_id=current_user.id,
        medicine_id=payload.medicine_id,
        target_pharmacy_id=payload.pharmacy_id,
        notify_on_restock=payload.notify_on_restock,
        is_active=True
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return _format_watchlist_response(item)

@router.get("", response_model=List[WatchlistResponse], summary="Get all active restock watchlist items for current user")
def get_my_watchlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    items = (
        db.query(Watchlist)
        .filter(Watchlist.user_id == current_user.id, Watchlist.is_active == True)
        .order_by(Watchlist.created_at.desc())
        .all()
    )
    return [_format_watchlist_response(w) for w in items]

@router.delete("/{watchlist_id}", status_code=status.HTTP_200_OK, summary="Remove an item from restock watchlist")
def remove_from_watchlist(
    watchlist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    item = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Watchlist item with ID {watchlist_id} not found."
        )

    if item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only delete your own watchlist items."
        )

    db.delete(item)
    db.commit()
    return {"message": "Watchlist subscription successfully removed."}
