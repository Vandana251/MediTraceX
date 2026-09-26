"""
=============================================================================
MediTraceX ML Evaluation & Diagnostics Reporter
=============================================================================
Module: ml_engine.evaluate_model

Description:
    Loads the trained model artifact from ml_engine/models/ and generates a
    granular evaluation report with per-category metrics, residual errors,
    and out-of-sample performance benchmarks.
=============================================================================
"""

import sys
import os
import json
import joblib
import numpy as np
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from typing import Dict, Any

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml_engine.data_preparation import (
    load_sales_dataframe,
    build_feature_matrix,
    time_based_train_test_split,
    FEATURE_COLUMNS,
    TARGET_COLUMN
)
from ml_engine.train_model import evaluate_predictions, MODEL_SAVE_PATH, METADATA_SAVE_PATH

def generate_evaluation_report() -> Dict[str, Any]:
    """Runs out-of-time evaluation and generates structured diagnostics."""
    if not os.path.exists(MODEL_SAVE_PATH) or not os.path.exists(METADATA_SAVE_PATH):
        raise FileNotFoundError(f"Model artifact not found. Run train_model.py first.")

    model = joblib.load(MODEL_SAVE_PATH)
    with open(METADATA_SAVE_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    raw_df = load_sales_dataframe()
    feat_df = build_feature_matrix(raw_df)
    _, X_test, _, y_test, _, test_df = time_based_train_test_split(feat_df, test_ratio=0.20)

    y_pred = model.predict(X_test)
    y_pred = np.clip(y_pred, 0, None)

    overall_metrics = evaluate_predictions(y_test, y_pred)
    test_df = test_df.copy()
    test_df["predicted_demand"] = y_pred
    test_df["absolute_error"] = np.abs(test_df[TARGET_COLUMN] - test_df["predicted_demand"])

    # Category-wise evaluation breakdown
    category_metrics = []
    for cat, group in test_df.groupby("medicine_category"):
        cat_mae = float(np.mean(group["absolute_error"]))
        cat_actual_mean = float(np.mean(group[TARGET_COLUMN]))
        cat_pred_mean = float(np.mean(group["predicted_demand"]))
        category_metrics.append({
            "category": cat,
            "sample_count": len(group),
            "actual_avg_demand": round(cat_actual_mean, 1),
            "predicted_avg_demand": round(cat_pred_mean, 1),
            "mae": round(cat_mae, 3)
        })

    print("=" * 78)
    print("  📈 MediTraceX Machine Learning Model Evaluation Report")
    print("=" * 78)
    print(f"  • Selected Model       : {metadata['selected_model']}")
    print(f"  • Overall Holdout MAE  : {overall_metrics['MAE']} units/day")
    print(f"  • Overall Holdout RMSE : {overall_metrics['RMSE']} units/day")
    print(f"  • Overall Holdout R²   : {overall_metrics['R2']}")
    print(f"  • Total Test Samples   : {len(test_df):,} rows")
    print("\n  Category-wise Performance Breakdown:")
    print("-" * 78)
    print(f"{'Therapeutic Category':<28} | {'Samples':<8} | {'Actual Avg':<11} | {'Pred Avg':<10} | {'MAE':<8}")
    print("-" * 78)
    for c in sorted(category_metrics, key=lambda x: x["sample_count"], reverse=True):
        print(f"{c['category']:<28} | {c['sample_count']:<8} | {c['actual_avg_demand']:<11} | {c['predicted_avg_demand']:<10} | {c['mae']:<8}")
    print("-" * 78)

    return {
        "overall_metrics": overall_metrics,
        "category_metrics": category_metrics,
        "metadata": metadata
    }

if __name__ == "__main__":
    generate_evaluation_report()
