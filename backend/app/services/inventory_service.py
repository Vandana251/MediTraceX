"""
Inventory Management Services
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import Inventory, Pharmacy, Medicine
from backend.app.schemas.inventory_schemas import InventoryUpdateRequest

class InventoryService:
    @staticmethod
    def get_by_id(db: Session, inventory_id: int) -> Optional[Inventory]:
        return db.query(Inventory).filter(Inventory.id == inventory_id).first()

    @staticmethod
    def get_by_pharmacy(db: Session, pharmacy_id: int) -> List[Inventory]:
        return db.query(Inventory).filter(Inventory.pharmacy_id == pharmacy_id).all()

    @staticmethod
    def get_by_medicine(db: Session, medicine_id: int) -> List[Inventory]:
        return db.query(Inventory).filter(Inventory.medicine_id == medicine_id).all()

    @staticmethod
    def get_pharmacy_medicine_stock(db: Session, pharmacy_id: int, medicine_id: int) -> Optional[Inventory]:
        return db.query(Inventory).filter(
            Inventory.pharmacy_id == pharmacy_id,
            Inventory.medicine_id == medicine_id
        ).first()

    @staticmethod
    def update_stock(db: Session, inventory: Inventory, update_data: InventoryUpdateRequest) -> Inventory:
        inventory.stock_quantity = update_data.stock_quantity
        if update_data.safety_stock_threshold is not None:
            inventory.safety_stock_threshold = update_data.safety_stock_threshold
        if update_data.batch_number is not None:
            inventory.batch_number = update_data.batch_number
        if update_data.expiry_date is not None:
            inventory.expiry_date = update_data.expiry_date

        # Recalculate stock status dynamically
        if inventory.stock_quantity <= 0:
            inventory.stock_status = "Out of Stock"
        elif inventory.stock_quantity < inventory.safety_stock_threshold:
            inventory.stock_status = "Low Stock"
        else:
            inventory.stock_status = "In Stock"

        inventory.last_restocked_at = datetime.now()
        inventory.updated_at = datetime.now()
        db.commit()
        db.refresh(inventory)
        return inventory
