"""
Pydantic Schemas for Medicine Restock Watchlist (Notify Me)
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class WatchlistCreate(BaseModel):
    medicine_id: int = Field(..., description="ID of out-of-stock medicine to watch")
    pharmacy_id: Optional[int] = Field(default=None, description="Optional target pharmacy ID")
    notify_on_restock: bool = Field(default=True, description="Enable notification trigger on restock")

class WatchlistResponse(BaseModel):
    id: int
    user_id: int
    medicine_id: int
    medicine_name: Optional[str] = None
    pharmacy_id: Optional[int] = None
    pharmacy_name: Optional[str] = None
    notify_on_restock: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
