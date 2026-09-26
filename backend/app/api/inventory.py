"""
Pharmacy Inventory Management API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user, require_roles
from backend.app.schemas.inventory_schemas import InventoryItemResponse, InventoryUpdateRequest
from backend.app.services.inventory_service import InventoryService
from database.models import User, Inventory, Pharmacy, Medicine

router = APIRouter(prefix="/inventory", tags=["Pharmacy Inventory"])

def _format_inventory_item(inv: Inventory) -> InventoryItemResponse:
    return InventoryItemResponse(
        id=inv.id,
        pharmacy_id=inv.pharmacy_id,
        pharmacy_name=inv.pharmacy.name if inv.pharmacy else None,
        medicine_id=inv.medicine_id,
        medicine_name=inv.medicine.name if inv.medicine else None,
        generic_name=inv.medicine.generic_name if inv.medicine else None,
        stock_quantity=inv.stock_quantity,
        safety_stock_threshold=inv.safety_stock_threshold,
        reorder_quantity=inv.reorder_quantity,
        batch_number=inv.batch_number,
        expiry_date=inv.expiry_date,
        stock_status=inv.stock_status,
        last_restocked_at=inv.last_restocked_at,
        updated_at=inv.updated_at
    )

@router.get("/pharmacy/{pharmacy_id}", response_model=List[InventoryItemResponse], summary="Get full inventory catalog for a pharmacy")
def get_inventory_by_pharmacy(pharmacy_id: int, db: Session = Depends(get_db)) -> Any:
    pharmacy = db.query(Pharmacy).filter(Pharmacy.id == pharmacy_id).first()
    if not pharmacy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pharmacy with ID {pharmacy_id} not found."
        )
    items = InventoryService.get_by_pharmacy(db, pharmacy_id=pharmacy_id)
    return [_format_inventory_item(i) for i in items]

@router.get("/medicine/{medicine_id}", response_model=List[InventoryItemResponse], summary="Get inventory records for a medicine across all pharmacies")
def get_inventory_by_medicine(medicine_id: int, db: Session = Depends(get_db)) -> Any:
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine with ID {medicine_id} not found."
        )
    items = InventoryService.get_by_medicine(db, medicine_id=medicine_id)
    return [_format_inventory_item(i) for i in items]

@router.get("/{pharmacy_id}/{medicine_id}", response_model=InventoryItemResponse, summary="Get exact stock for a pharmacy-medicine pair")
def get_specific_stock(pharmacy_id: int, medicine_id: int, db: Session = Depends(get_db)) -> Any:
    item = InventoryService.get_pharmacy_medicine_stock(db, pharmacy_id=pharmacy_id, medicine_id=medicine_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No inventory record found for pharmacy {pharmacy_id} and medicine {medicine_id}."
        )
    return _format_inventory_item(item)

@router.put("/{inventory_id}", response_model=InventoryItemResponse, summary="Update pharmacy stock quantity & batch info (Protected)")
def update_inventory_stock(
    inventory_id: int,
    payload: InventoryUpdateRequest,
    current_user: User = Depends(require_roles(["pharmacy_admin", "pharmacy", "system_admin"])),
    db: Session = Depends(get_db)
) -> Any:
    """
    Updates medicine stock levels and recalculates stock status dynamically.
    Restricted to pharmacy administrators and system admins.
    """
    item = InventoryService.get_by_id(db, inventory_id=inventory_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory record with ID {inventory_id} not found."
        )

    updated = InventoryService.update_stock(db, inventory=item, update_data=payload)
    return _format_inventory_item(updated)
