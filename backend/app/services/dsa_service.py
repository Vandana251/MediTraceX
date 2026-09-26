"""
MediTraceX DSA Service
Integrates in-memory Trie Search and Min-Heap Nearby Pharmacy Discovery
"""

import sys
import os
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.dsa.trie_search import MedicineTrieSearch, SearchResult
from backend.app.dsa.ranker import PharmacyRanker, PharmacyRankingResult
from database.models import Medicine, Pharmacy, Inventory

class DSAService:
    _instance: Optional["DSAService"] = None
    _trie: Optional[MedicineTrieSearch] = None

    def __init__(self):
        self._trie = MedicineTrieSearch()
        self._is_indexed = False

    @classmethod
    def get_instance(cls) -> "DSAService":
        if cls._instance is None:
            cls._instance = DSAService()
        return cls._instance

    def initialize_trie(self, db: Session) -> int:
        """Loads all medicines into Trie prefix tree on startup or on-demand."""
        medicines = db.query(Medicine).all()
        self._trie = MedicineTrieSearch()
        for med in medicines:
            self._trie.insert_medicine({
                "id": med.id,
                "name": med.name,
                "generic_name": med.generic_name,
                "brand_name": med.brand_name,
                "dosage": med.dosage,
                "dosage_form": med.dosage_form,
                "category": med.category,
                "unit_price": float(med.unit_price)
            })
        self._is_indexed = True
        return len(medicines)

    def search_medicines(self, query: str, limit: int = 15, db: Optional[Session] = None) -> List[SearchResult]:
        """
        Executes sub-millisecond Trie Prefix Search with Levenshtein Fuzzy Typo fallback.
        """
        if (self._trie is None or len(self._trie.medicine_catalog) == 0) and db is not None:
            self.initialize_trie(db)
        
        return self._trie.search(query, limit=limit)

    def rank_nearby_pharmacies_for_medicine(
        self,
        db: Session,
        medicine_id: int,
        user_lat: float,
        user_lon: float,
        radius_km: float = 25.0,
        limit: int = 10
    ) -> List[PharmacyRankingResult]:
        """
        Queries all candidate pharmacy inventories for target medicine and executes
        Min-Heap Priority Queue ranking based on Availability Tier and Haversine Distance.
        """
        records = (
            db.query(
                Pharmacy.id,
                Pharmacy.name,
                Pharmacy.address,
                Pharmacy.city,
                Pharmacy.latitude,
                Pharmacy.longitude,
                Pharmacy.contact_phone,
                Pharmacy.is_24_7,
                Pharmacy.opening_time,
                Pharmacy.closing_time,
                Inventory.stock_quantity,
                Inventory.safety_stock_threshold,
                Inventory.stock_status,
                Inventory.updated_at
            )
            .join(Inventory, Inventory.pharmacy_id == Pharmacy.id)
            .filter(Inventory.medicine_id == medicine_id, Pharmacy.is_active == True)
            .all()
        )

        candidates = [
            {
                "id": r.id,
                "name": r.name,
                "address": r.address,
                "city": r.city,
                "latitude": float(r.latitude),
                "longitude": float(r.longitude),
                "contact_phone": r.contact_phone,
                "is_24_7": r.is_24_7,
                "opening_time": str(r.opening_time),
                "closing_time": str(r.closing_time),
                "stock_quantity": r.stock_quantity,
                "safety_stock_threshold": r.safety_stock_threshold,
                "stock_status": r.stock_status,
                "updated_at": r.updated_at
            }
            for r in records
        ]

        ranked_results = PharmacyRanker.rank_pharmacies(
            user_lat=user_lat,
            user_lon=user_lon,
            pharmacy_inventory_records=candidates,
            max_results=limit,
            max_radius_km=radius_km
        )

        return ranked_results

dsa_service = DSAService.get_instance()
