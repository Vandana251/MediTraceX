"""
Pydantic Schemas for Medicine Procurement Requests
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MedicineRequestCreate(BaseModel):
    medicine_id: int = Field(..., description="ID of the medicine requested")
    pharmacy_id: Optional[int] = Field(default=None, description="Optional target pharmacy (or leave null for broadcast)")
    quantity_requested: int = Field(default=1, ge=1, description="Quantity of units required")
    notes: Optional[str] = Field(default=None, max_length=500, description="Notes/prescription details")

class MedicineRequestStatusUpdate(BaseModel):
    status: str = Field(..., description="New status: PENDING, ACCEPTED, FULFILLED, CANCELLED, NOT_AVAILABLE")

class MedicineRequestResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    pharmacy_id: Optional[int] = None
    pharmacy_name: Optional[str] = None
    medicine_id: int
    medicine_name: Optional[str] = None
    quantity_requested: int
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
