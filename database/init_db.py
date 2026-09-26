"""
=============================================================================
MediTraceX Production Database Initializer & Migration Tool
=============================================================================
Usage:
    python database/init_db.py            # Creates tables if missing (non-destructive)
    python database/init_db.py --seed     # Populates synthetic demonstration dataset
=============================================================================
"""

import sys
import os
import argparse
from sqlalchemy import text

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db_config import Base, engine, SessionLocal, DB_TYPE, ENVIRONMENT
from database.models import (
    User, Pharmacy, Medicine, Inventory, SalesHistory,
    MedicineRequest, Watchlist, Notification
)
from database.seed_data import seed_core_catalog, seed_historical_sales

def init_production_database(auto_seed_if_empty: bool = True, include_full_history: bool = False):
    """
    Safely verifies connection and creates all missing tables in the target database.
    Does NOT drop existing production tables.
    If database is completely empty, seeds essential catalog data (< 1 sec) so the
    web service and endpoints function immediately without blocking cloud port scan.
    """
    print("\n" + "="*78)
    print(" 🛠️  MediTraceX Database Initialization & Schema Verification")
    print(f"     Target Engine: {DB_TYPE.upper()} | Environment: {ENVIRONMENT.upper()}")
    print("="*78 + "\n")

    # 1. Verify Connectivity
    print("[1/3] Testing database connection...")
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("      Database connection confirmed active.")
    except Exception as e:
        print(f"      [ERROR] Could not connect to database: {e}")
        sys.exit(1)

    # 2. Create missing tables (non-destructive)
    print("[2/3] Verifying and applying relational schema tables...")
    Base.metadata.create_all(bind=engine)
    print("      All 8 core tables are verified and present.")

    # 3. Check table population
    session = SessionLocal()
    try:
        pharmacy_count = session.query(Pharmacy).count()
        medicine_count = session.query(Medicine).count()
        print(f"[3/3] Current Records: {pharmacy_count} Pharmacies | {medicine_count} Medicines")

        if pharmacy_count == 0 and auto_seed_if_empty:
            print("\n      [Notice] Empty database detected. Seeding essential catalog & inventory...")
            seed_core_catalog(session)
            if include_full_history:
                print("      [Notice] Seeding optional 240-day sales history simulation...")
                seed_historical_sales(session)
            session.commit()
            print("      [Ready] Essential catalog seeded. Web service ready to serve requests.")
        else:
            print("\n      [Ready] Database initialized and ready for production operation.")

    except Exception as e:
        session.rollback()
        print(f"      [ERROR] Initialization failed: {e}")
        raise
    finally:
        session.close()

    print("="*78 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize MediTraceX Database")
    parser.add_argument("--seed", action="store_true", help="Force populate essential catalog data")
    parser.add_argument("--full-history", "--seed-all", action="store_true", dest="full_history", help="Also generate 240-day historical sales records for ML simulation")
    args = parser.parse_args()

    init_production_database(auto_seed_if_empty=True, include_full_history=args.full_history)
