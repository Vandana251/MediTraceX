"""
MediTraceX ML Demand Forecasting & Stock-out Risk Test Suite
"""

import sys
import os
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml_engine.predict import DemandPredictor
from ml_engine.train_model import MODEL_SAVE_PATH, METADATA_SAVE_PATH

class TestMLPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.predictor = DemandPredictor(model_path=MODEL_SAVE_PATH)

    def test_model_artifacts_exist(self):
        self.assertTrue(os.path.exists(MODEL_SAVE_PATH), "Model joblib artifact must exist")
        self.assertTrue(os.path.exists(METADATA_SAVE_PATH), "Model metadata JSON must exist")

    def test_prediction_output_structure(self):
        result = self.predictor.predict_demand(pharmacy_id=2, medicine_id=2, forecast_days=7)
        
        required_keys = [
            "medicine_id", "medicine_name", "pharmacy_id", "pharmacy_name",
            "current_stock", "predicted_next_day_demand", "predicted_7d_demand",
            "daily_forecasts", "stockout_risk", "suggested_restock_quantity",
            "disclaimer"
        ]
        for key in required_keys:
            self.assertIn(key, result, f"Key '{key}' missing from prediction output")

        self.assertIn(result["stockout_risk"], ["LOW", "MEDIUM", "HIGH"])
        self.assertEqual(len(result["daily_forecasts"]), 7)
        self.assertGreaterEqual(result["suggested_restock_quantity"], 0)

    def test_stockout_risk_rules(self):
        # Case A: Low stock -> High Risk
        risk_high, _, restock_high = DemandPredictor.calculate_stockout_risk(
            current_stock=10, predicted_7d_demand=50, safety_threshold=15
        )
        self.assertEqual(risk_high, "HIGH")
        self.assertGreater(restock_high, 0)

        # Case B: Sufficient stock -> Low Risk
        risk_low, _, restock_low = DemandPredictor.calculate_stockout_risk(
            current_stock=120, predicted_7d_demand=50, safety_threshold=15
        )
        self.assertEqual(risk_low, "LOW")
        self.assertEqual(restock_low, 0)

        # Case C: Borderline stock -> Medium Risk
        risk_med, _, restock_med = DemandPredictor.calculate_stockout_risk(
            current_stock=35, predicted_7d_demand=50, safety_threshold=15
        )
        self.assertEqual(risk_med, "MEDIUM")

if __name__ == "__main__":
    unittest.main()
