"""
=============================================================================
MediTraceX ML Inference & Inventory Risk Engine
=============================================================================
Module: ml_engine.predict

Description:
    Provides live demand forecasting and stock-out risk assessment for any
    (pharmacy_id, medicine_id) pair. Uses the trained ML model, recent sales
    trajectory, and current stock level to compute:
    - 1-Day & 7-Day Predicted Demand
    - Stock-Out Risk Category (HIGH, MEDIUM, LOW)
    - Suggested Restock Quantity

Disclaimer:
    This prediction is designed strictly for pharmaceutical supply chain
    and inventory planning. It does not constitute medical advice.
=============================================================================
"""

import sys
import os
import json
import joblib
import math
import numpy as np
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from datetime import date, datetime, timedelta
from typing import Dict, Any, Optional, Tuple

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db_config import SessionLocal
from database.models import SalesHistory, Medicine, Pharmacy, Inventory
from ml_engine.train_model import MODEL_SAVE_PATH, METADATA_SAVE_PATH, FEATURE_COLUMNS


class DemandPredictor:
    """
    Inference Engine for MediTraceX demand forecasting and stock-out risk assessment.
    """

    def __init__(self, model_path: str = MODEL_SAVE_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Trained model not found at {model_path}. Run train_model.py first.")
        self.model = joblib.load(model_path)
        with open(METADATA_SAVE_PATH, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    @staticmethod
    def calculate_stockout_risk(
        current_stock: int,
        predicted_7d_demand: float,
        safety_threshold: int = 15
    ) -> Tuple[str, str, int]:
        """
        Assesses inventory stock-out risk category and recommended restock volume.
        
        Rules:
        - HIGH RISK   : Stock <= 0 OR Stock < 50% of 7-day demand OR Stock < safety threshold
        - MEDIUM RISK : 50% of 7-day demand <= Stock < 100% of 7-day demand
        - LOW RISK    : Stock >= 100% of 7-day demand AND Stock >= safety threshold
        """
        # Suggested stock buffer = Predicted Demand + Safety Buffer - Current Stock
        target_buffer = predicted_7d_demand + safety_threshold
        suggested_restock = max(0, int(math.ceil(target_buffer - current_stock)))

        if current_stock <= 0 or current_stock < (0.5 * predicted_7d_demand) or current_stock < safety_threshold:
            risk = "HIGH"
            explanation = f"Current stock ({current_stock}) is insufficient for expected 7-day demand ({predicted_7d_demand:.0f}) or below safety threshold ({safety_threshold})."
        elif current_stock < (1.0 * predicted_7d_demand):
            risk = "MEDIUM"
            explanation = f"Current stock ({current_stock}) covers immediate needs but is likely to deplete within 7 days."
        else:
            risk = "LOW"
            explanation = f"Current stock ({current_stock}) comfortably covers expected 7-day demand ({predicted_7d_demand:.0f})."

        return risk, explanation, suggested_restock

    def predict_demand(
        self,
        pharmacy_id: int,
        medicine_id: int,
        forecast_days: int = 7
    ) -> Dict[str, Any]:
        """
        Performs multi-day demand forecasting and stock-out risk analysis
        for a specific pharmacy and medicine.
        """
        session = SessionLocal()
        try:
            # 1. Fetch metadata
            pharmacy = session.query(Pharmacy).filter(Pharmacy.id == pharmacy_id).first()
            medicine = session.query(Medicine).filter(Medicine.id == medicine_id).first()
            inv = session.query(Inventory).filter(
                Inventory.pharmacy_id == pharmacy_id,
                Inventory.medicine_id == medicine_id
            ).first()

            if not pharmacy or not medicine:
                raise ValueError(f"Invalid pharmacy_id ({pharmacy_id}) or medicine_id ({medicine_id})")

            current_stock = inv.stock_quantity if inv else 0
            safety_threshold = inv.safety_stock_threshold if inv else 15
            unit_price = float(medicine.unit_price)

            # 2. Fetch last 35 days of sales history for feature reconstruction
            recent_sales = (
                session.query(SalesHistory.sale_date, SalesHistory.quantity_sold)
                .filter(
                    SalesHistory.pharmacy_id == pharmacy_id,
                    SalesHistory.medicine_id == medicine_id
                )
                .order_by(SalesHistory.sale_date.desc())
                .limit(35)
                .all()
            )

            # Build historical quantity series
            if recent_sales:
                sales_history_list = [r.quantity_sold for r in reversed(recent_sales)]
            else:
                # Default baseline if no history exists for this pair
                sales_history_list = [10] * 30

            # 3. Iterative Multi-step Forecast for next N days
            daily_forecasts = []
            cur_history = list(sales_history_list)
            cur_date = date.today() + timedelta(days=1)

            for day_offset in range(forecast_days):
                target_date = cur_date + timedelta(days=day_offset)
                
                # Extract lag features from current rolling buffer
                lag_1 = cur_history[-1] if len(cur_history) >= 1 else 10
                lag_2 = cur_history[-2] if len(cur_history) >= 2 else 10
                lag_7 = cur_history[-7] if len(cur_history) >= 7 else 10
                
                last_7 = cur_history[-7:]
                last_14 = cur_history[-14:]
                last_30 = cur_history[-30:]

                roll_7_mean = float(np.mean(last_7))
                roll_7_std = float(np.std(last_7))
                roll_14_mean = float(np.mean(last_14))
                roll_30_mean = float(np.mean(last_30))

                feature_dict = {
                    "pharmacy_id": pharmacy_id,
                    "medicine_id": medicine_id,
                    "day_of_week_num": target_date.weekday(),
                    "is_weekend_int": 1 if target_date.weekday() >= 5 else 0,
                    "month": target_date.month,
                    "day_of_month": target_date.day,
                    "lag_1_demand": lag_1,
                    "lag_2_demand": lag_2,
                    "lag_7_demand": lag_7,
                    "rolling_7d_mean": roll_7_mean,
                    "rolling_7d_std": roll_7_std,
                    "rolling_14d_mean": roll_14_mean,
                    "rolling_30d_mean": roll_30_mean,
                    "unit_price_float": unit_price
                }

                input_df = pd.DataFrame([feature_dict])[FEATURE_COLUMNS]
                pred_qty = float(self.model.predict(input_df)[0])
                pred_qty = max(0.0, pred_qty)
                
                daily_forecasts.append({
                    "date": target_date.strftime("%Y-%m-%d"),
                    "day_name": target_date.strftime("%A"),
                    "predicted_demand": round(pred_qty, 1)
                })

                # Append prediction to buffer for next lag step
                cur_history.append(int(round(pred_qty)))

            next_1d_demand = daily_forecasts[0]["predicted_demand"]
            predicted_7d_demand = sum(d["predicted_demand"] for d in daily_forecasts[:7])
            
            risk_category, risk_explanation, suggested_restock = self.calculate_stockout_risk(
                current_stock=current_stock,
                predicted_7d_demand=predicted_7d_demand,
                safety_threshold=safety_threshold
            )

            return {
                "medicine_id": medicine.id,
                "medicine_name": medicine.name,
                "medicine_category": medicine.category,
                "pharmacy_id": pharmacy.id,
                "pharmacy_name": pharmacy.name,
                "pharmacy_address": pharmacy.address,
                "current_stock": current_stock,
                "safety_stock_threshold": safety_threshold,
                "predicted_next_day_demand": round(next_1d_demand, 1),
                "predicted_7d_demand": round(predicted_7d_demand, 1),
                "daily_forecasts": daily_forecasts,
                "stockout_risk": risk_category,
                "risk_explanation": risk_explanation,
                "suggested_restock_quantity": suggested_restock,
                "model_used": self.metadata.get("selected_model", "Machine Learning Model"),
                "disclaimer": "This prediction is for supply chain and inventory planning only, not medical advice."
            }

        finally:
            session.close()

if __name__ == "__main__":
    predictor = DemandPredictor()
    sample_result = predictor.predict_demand(pharmacy_id=2, medicine_id=2)
    print(json.dumps(sample_result, indent=2))
