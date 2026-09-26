"""
Pharmacy Database Query Services
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from database.models import Pharmacy

class PharmacyService:
    @staticmethod
    def get_by_id(db: Session, pharmacy_id: int) -> Optional[Pharmacy]:
        return db.query(Pharmacy).filter(Pharmacy.id == pharmacy_id).first()

    @staticmethod
    def get_all_active(db: Session) -> List[Pharmacy]:
        return db.query(Pharmacy).filter(Pharmacy.is_active == True).all()
