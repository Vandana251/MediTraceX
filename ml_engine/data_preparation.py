"""
=============================================================================
MediTraceX Machine Learning Pipeline: Data Preparation & Feature Engineering
=============================================================================
Module: ml_engine.data_preparation

Description:
    Loads historical daily sales transactions from the database, sorts by
    time series per (pharmacy_id, medicine_id), and engineers temporal,
    lag, and rolling aggregation features for medicine demand prediction.
=============================================================================
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Any

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db_config import SessionLocal
from database.models import SalesHistory, Medicine, Pharmacy, Inventory

FEATURE_COLUMNS = [
    "pharmacy_id",
    "medicine_id",
    "day_of_week_num",
    "is_weekend_int",
    "month",
    "day_of_month",
    "lag_1_demand",
    "lag_2_demand",
    "lag_7_demand",
    "rolling_7d_mean",
    "rolling_7d_std",
    "rolling_14d_mean",
    "rolling_30d_mean",
    "unit_price_float"
]

TARGET_COLUMN = "quantity_sold"

def load_sales_dataframe() -> pd.DataFrame:
    """
    Extracts sales records combined with medicine and pharmacy metadata
    from the MediTraceX database into a structured pandas DataFrame.
    """
    session = SessionLocal()
    try:
        query = (
            session.query(
                SalesHistory.id,
                SalesHistory.pharmacy_id,
                SalesHistory.medicine_id,
                SalesHistory.sale_date,
                SalesHistory.quantity_sold,
                SalesHistory.unit_price,
                SalesHistory.day_of_week,
                SalesHistory.is_weekend,
                Medicine.name.label("medicine_name"),
                Medicine.category.label("medicine_category"),
                Pharmacy.name.label("pharmacy_name")
            )
            .join(Medicine, Medicine.id == SalesHistory.medicine_id)
            .join(Pharmacy, Pharmacy.id == SalesHistory.pharmacy_id)
        )
        
        df = pd.read_sql(query.statement, session.bind)
        df["sale_date"] = pd.to_datetime(df["sale_date"])
        df["unit_price_float"] = df["unit_price"].astype(float)
        df["is_weekend_int"] = df["is_weekend"].astype(int)
        df = df.sort_values(by=["pharmacy_id", "medicine_id", "sale_date"]).reset_index(drop=True)
        return df
    finally:
        session.close()

def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Constructs time-series lag and rolling statistics features strictly within
    each (pharmacy_id, medicine_id) grouping to prevent data leakage.
    """
    # 1. Calendar Features
    df["day_of_week_num"] = df["sale_date"].dt.dayofweek # 0=Monday, 6=Sunday
    df["month"] = df["sale_date"].dt.month
    df["day_of_month"] = df["sale_date"].dt.day

    # 2. Lag Features (Previous Day, Previous 2-Day, Previous 7-Day)
    grouped = df.groupby(["pharmacy_id", "medicine_id"])["quantity_sold"]
    
    df["lag_1_demand"] = grouped.shift(1)
    df["lag_2_demand"] = grouped.shift(2)
    df["lag_7_demand"] = grouped.shift(7)

    # 3. Rolling Window Aggregations (computed on shifted series to avoid target leakage)
    shifted = grouped.shift(1)
    
    df["rolling_7d_mean"] = df.groupby(["pharmacy_id", "medicine_id"])["lag_1_demand"].transform(
        lambda s: s.rolling(window=7, min_periods=1).mean()
    )
    df["rolling_7d_std"] = df.groupby(["pharmacy_id", "medicine_id"])["lag_1_demand"].transform(
        lambda s: s.rolling(window=7, min_periods=1).std().fillna(0)
    )
    df["rolling_14d_mean"] = df.groupby(["pharmacy_id", "medicine_id"])["lag_1_demand"].transform(
        lambda s: s.rolling(window=14, min_periods=1).mean()
    )
    df["rolling_30d_mean"] = df.groupby(["pharmacy_id", "medicine_id"])["lag_1_demand"].transform(
        lambda s: s.rolling(window=30, min_periods=1).mean()
    )

    # 4. Drop rows that do not have enough lag history (first 7 days per series)
    processed_df = df.dropna(subset=["lag_1_demand", "lag_7_demand", "rolling_7d_mean"]).reset_index(drop=True)
    return processed_df

def time_based_train_test_split(
    df: pd.DataFrame,
    test_ratio: float = 0.20
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.DataFrame, pd.DataFrame]:
    """
    Performs out-of-time chronological train/test split.
    The earliest (1 - test_ratio) dates form the training set,
    and the latest test_ratio dates form the holdout test set.
    """
    unique_dates = sorted(df["sale_date"].unique())
    split_idx = int(len(unique_dates) * (1.0 - test_ratio))
    split_date = unique_dates[split_idx]

    train_mask = df["sale_date"] < split_date
    test_mask = df["sale_date"] >= split_date

    train_df = df[train_mask].copy()
    test_df = df[test_mask].copy()

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]

    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN]

    print(f"Data Split Summary:")
    print(f"  • Date Range Total : {df['sale_date'].min().strftime('%Y-%m-%d')} to {df['sale_date'].max().strftime('%Y-%m-%d')}")
    print(f"  • Split Cutoff Date: {split_date.strftime('%Y-%m-%d')}")
    print(f"  • Training Samples : {len(train_df):,} rows ({len(train_df)/len(df)*100:.1f}%)")
    print(f"  • Test Samples     : {len(test_df):,} rows ({len(test_df)/len(df)*100:.1f}%)")

    return X_train, X_test, y_train, y_test, train_df, test_df

if __name__ == "__main__":
    raw_df = load_sales_dataframe()
    print(f"Loaded {len(raw_df):,} raw sales records.")
    feat_df = build_feature_matrix(raw_df)
    print(f"Engineered features across {len(feat_df):,} records.")
    X_train, X_test, y_train, y_test, _, _ = time_based_train_test_split(feat_df)
