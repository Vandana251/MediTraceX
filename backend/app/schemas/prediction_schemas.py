"""
Pydantic Schemas for ML Demand Forecast & Stock-out Risk
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class DailyDemandForecast(BaseModel):
    date: str
    day_name: str
    predicted_demand: float

class DemandPredictionResponse(BaseModel):
    medicine_id: int
    medicine_name: str
    medicine_category: str
    pharmacy_id: int
    pharmacy_name: str
    pharmacy_address: str
    current_stock: int
    safety_threshold: int
    predicted_next_day_demand: float
    predicted_7_day_demand: float
    stock_out_risk: str # "HIGH", "MEDIUM", "LOW"
    risk_reason: str
    suggested_restock_quantity: int
    daily_forecasts: List[DailyDemandForecast]
    model_used: str
    disclaimer: str = "This prediction is for supply chain and inventory planning only, not medical advice."
