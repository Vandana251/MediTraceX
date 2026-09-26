"""
Medicine Database Query Services
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from database.models import Medicine

class MedicineService:
    @staticmethod
    def get_by_id(db: Session, medicine_id: int) -> Optional[Medicine]:
        return db.query(Medicine).filter(Medicine.id == medicine_id).first()

    @staticmethod
    def get_list(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        category: Optional[str] = None
    ) -> Tuple[List[Medicine], int]:
        query = db.query(Medicine)
        if category:
            query = query.filter(Medicine.category.ilike(f"%{category}%"))
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total
