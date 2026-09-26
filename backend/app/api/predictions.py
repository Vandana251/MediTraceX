"""
Machine Learning Demand Forecasting & Stock-Out Risk API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Any

from backend.app.core.database import get_db
from backend.app.schemas.prediction_schemas import DemandPredictionResponse, DailyDemandForecast
from backend.app.services.ml_service import ml_service
from database.models import Pharmacy, Medicine

router = APIRouter(prefix="/predictions", tags=["ML Demand Forecasting & Stock-out Risk"])

@router.get("/{pharmacy_id}/{medicine_id}", response_model=DemandPredictionResponse, summary="Get ML demand prediction & stock-out risk assessment")
def get_demand_forecast_and_risk(
    pharmacy_id: int,
    medicine_id: int,
    forecast_days: int = Query(default=7, ge=1, le=14, description="Forecast horizon in days (default: 7)"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Executes the trained Gradient Boosting ML pipeline to predict:
    - 1-Day & 7-Day Medicine Demand
    - Stock-Out Risk Level (HIGH, MEDIUM, LOW)
    - Suggested Restock Quantity
    
    Disclaimer: For supply chain/inventory planning only; not medical advice.
    """
    pharmacy = db.query(Pharmacy).filter(Pharmacy.id == pharmacy_id).first()
    if not pharmacy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pharmacy with ID {pharmacy_id} not found."
        )

    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine with ID {medicine_id} not found."
        )

    try:
        res = ml_service.predict_demand(
            pharmacy_id=pharmacy_id,
            medicine_id=medicine_id,
            forecast_days=forecast_days
        )

        return DemandPredictionResponse(
            medicine_id=res["medicine_id"],
            medicine_name=res["medicine_name"],
            medicine_category=res["medicine_category"],
            pharmacy_id=res["pharmacy_id"],
            pharmacy_name=res["pharmacy_name"],
            pharmacy_address=res["pharmacy_address"],
            current_stock=res["current_stock"],
            safety_threshold=res.get("safety_stock_threshold", 15),
            predicted_next_day_demand=res["predicted_next_day_demand"],
            predicted_7_day_demand=res.get("predicted_7d_demand", res.get("predicted_7_day_demand")),
            stock_out_risk=res.get("stockout_risk", res.get("stock_out_risk")),
            risk_reason=res.get("risk_explanation", res.get("risk_reason")),
            suggested_restock_quantity=res["suggested_restock_quantity"],
            daily_forecasts=[
                DailyDemandForecast(
                    date=d["date"],
                    day_name=d["day_name"],
                    predicted_demand=d["predicted_demand"]
                )
                for d in res["daily_forecasts"]
            ],
            model_used=res["model_used"],
            disclaimer=res.get("disclaimer", "This prediction is for supply chain and inventory planning only, not medical advice.")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction pipeline error: {str(e)}"
        )
