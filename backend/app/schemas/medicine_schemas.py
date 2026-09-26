"""
Pydantic Schemas for Medicine Discovery & Catalog
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MedicineBase(BaseModel):
    id: int
    name: str
    generic_name: str
    brand_name: str
    dosage: str
    dosage_form: str
    manufacturer: str
    category: str
    is_prescription_required: bool
    unit_price: float

    class Config:
        from_attributes = True

class MedicineSearchResponse(BaseModel):
    id: int
    name: str
    generic_name: str
    brand_name: str
    dosage: str
    dosage_form: str
    category: str
    unit_price: float
    match_type: str = "prefix" # "exact", "prefix", "fuzzy"
    edit_distance: int = 0

class MedicineListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[MedicineBase]
