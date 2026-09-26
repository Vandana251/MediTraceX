"""
Pydantic Schemas for Pharmacy Inventory Management
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class InventoryItemResponse(BaseModel):
    id: int
    pharmacy_id: int
    pharmacy_name: Optional[str] = None
    medicine_id: int
    medicine_name: Optional[str] = None
    generic_name: Optional[str] = None
    stock_quantity: int
    safety_stock_threshold: int
    reorder_quantity: int
    batch_number: str
    expiry_date: date
    stock_status: str
    last_restocked_at: Optional[datetime] = None
    updated_at: datetime

    class Config:
        from_attributes = True

class InventoryUpdateRequest(BaseModel):
    stock_quantity: int = Field(..., ge=0, description="New available physical stock quantity")
    safety_stock_threshold: Optional[int] = Field(default=15, ge=1, description="Threshold below which stock is considered Low")
    batch_number: Optional[str] = Field(default=None, description="Batch reference code")
    expiry_date: Optional[date] = Field(default=None, description="Batch expiry date")
