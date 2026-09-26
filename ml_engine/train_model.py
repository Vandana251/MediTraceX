"""
=============================================================================
MediTraceX ML Training & Model Selection Engine
=============================================================================
Module: ml_engine.train_model

Description:
    Trains and compares multiple regression models for medicine demand forecasting:
    1. Random Forest Regressor
    2. Gradient Boosting Regressor / HistGradientBoostingRegressor
    Evaluates both on MAE, RMSE, and R2 using time-based holdout validation,
    selects the superior model, and serializes it using joblib.
=============================================================================
"""

import sys
import os
import json
import time
import joblib
import numpy as np
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from typing import Dict, Any, Tuple
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

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

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

MODEL_SAVE_PATH = os.path.join(MODELS_DIR, "demand_forecast_model.joblib")
METADATA_SAVE_PATH = os.path.join(MODELS_DIR, "model_metadata.json")

def evaluate_predictions(y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, float]:
    """Calculates MAE, RMSE, and R2 regression metrics."""
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred))
    return {
        "MAE": round(mae, 4),
        "RMSE": round(rmse, 4),
        "R2": round(r2, 4)
    }

def train_and_evaluate_models() -> Tuple[Any, Dict[str, Any]]:
    """
    Executes end-to-end model training, comparative evaluation, and serialization.
    """
    print("=" * 78)
    print("  🏥 MediTraceX Machine Learning Training & Model Selection")
    print("=" * 78)

    # 1. Prepare Data
    print("\n[1/4] Loading sales database and engineering time-series lag features...")
    raw_df = load_sales_dataframe()
    feat_df = build_feature_matrix(raw_df)
    X_train, X_test, y_train, y_test, train_df, test_df = time_based_train_test_split(feat_df, test_ratio=0.20)

    # 2. Define Candidate Models
    candidate_models = {
        "Random Forest Regressor": RandomForestRegressor(
            n_estimators=100,
            max_depth=12,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        ),
        "Gradient Boosting Regressor": HistGradientBoostingRegressor(
            max_iter=120,
            max_depth=8,
            learning_rate=0.08,
            min_samples_leaf=15,
            random_state=42
        )
    }

    results = {}
    fitted_models = {}

    print("\n[2/4] Training and evaluating candidate models...")
    for model_name, model in candidate_models.items():
        print(f"\n  Training {model_name}...")
        t0 = time.perf_counter()
        model.fit(X_train, y_train)
        train_duration = time.perf_counter() - t0

        # Predict on holdout test set
        y_pred = model.predict(X_test)
        # Ensure non-negative demand predictions
        y_pred = np.clip(y_pred, 0, None)

        metrics = evaluate_predictions(y_test, y_pred)
        metrics["Training_Time_Sec"] = round(train_duration, 2)

        results[model_name] = metrics
        fitted_models[model_name] = model

        print(f"  --> {model_name} Results on Holdout Test Set:")
        print(f"      • MAE  : {metrics['MAE']:.4f} units")
        print(f"      • RMSE : {metrics['RMSE']:.4f} units")
        print(f"      • R²   : {metrics['R2']:.4f}")
        print(f"      • Fit Time: {metrics['Training_Time_Sec']}s")

    # 3. Model Comparison & Selection
    print("\n[3/4] Comparative Model Analysis:")
    print("-" * 78)
    print(f"{'Model Name':<32} | {'MAE':<8} | {'RMSE':<8} | {'R²':<8} | {'Fit Time':<8}")
    print("-" * 78)
    for m_name, m_metrics in results.items():
        print(f"{m_name:<32} | {m_metrics['MAE']:<8} | {m_metrics['RMSE']:<8} | {m_metrics['R2']:<8} | {m_metrics['Training_Time_Sec']}s")
    print("-" * 78)

    # Select model with lowest RMSE on out-of-time test set
    best_model_name = min(results.keys(), key=lambda k: results[k]["RMSE"])
    best_model = fitted_models[best_model_name]
    best_metrics = results[best_model_name]

    selection_rationale = (
        f"{best_model_name} demonstrated superior predictive accuracy with the lowest "
        f"RMSE ({best_metrics['RMSE']}) and MAE ({best_metrics['MAE']}), explaining {best_metrics['R2']*100:.2f}% "
        f"of variance on the chronologically holdout test dataset."
    )
    print(f"\n🏆 Selected Model: {best_model_name}")
    print(f"   Rationale: {selection_rationale}")

    # 4. Save Artifacts
    print("\n[4/4] Serializing model and metadata...")
    joblib.dump(best_model, MODEL_SAVE_PATH)
    
    metadata = {
        "selected_model": best_model_name,
        "features": FEATURE_COLUMNS,
        "target": TARGET_COLUMN,
        "metrics": best_metrics,
        "all_model_results": results,
        "selection_rationale": selection_rationale,
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_records_trained": int(len(X_train)),
        "total_records_tested": int(len(X_test))
    }

    with open(METADATA_SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"  Saved trained model to   : {MODEL_SAVE_PATH}")
    print(f"  Saved model metadata to : {METADATA_SAVE_PATH}")
    print("\n[SUCCESS] Model training pipeline completed successfully!")

    return best_model, metadata

if __name__ == "__main__":
    train_and_evaluate_models()
