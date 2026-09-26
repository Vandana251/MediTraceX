"""
MediTraceX Machine Learning Prediction Service
"""

import sys
import os
from typing import Dict, Any, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml_engine.predict import DemandPredictor
from ml_engine.train_model import MODEL_SAVE_PATH

class MLService:
    _instance: Optional["MLService"] = None
    _predictor: Optional[DemandPredictor] = None

    def __init__(self):
        if os.path.exists(MODEL_SAVE_PATH):
            self._predictor = DemandPredictor(model_path=MODEL_SAVE_PATH)
        else:
            self._predictor = None

    @classmethod
    def get_instance(cls) -> "MLService":
        if cls._instance is None:
            cls._instance = MLService()
        return cls._instance

    def predict_demand(self, pharmacy_id: int, medicine_id: int, forecast_days: int = 7) -> Dict[str, Any]:
        """Runs trained ML model to forecast demand and calculate stock-out risk."""
        if self._predictor is None:
            if os.path.exists(MODEL_SAVE_PATH):
                self._predictor = DemandPredictor(model_path=MODEL_SAVE_PATH)
            else:
                raise RuntimeError("ML model artifact not found. Please train model first.")
        
        return self._predictor.predict_demand(
            pharmacy_id=pharmacy_id,
            medicine_id=medicine_id,
            forecast_days=forecast_days
        )

ml_service = MLService.get_instance()
