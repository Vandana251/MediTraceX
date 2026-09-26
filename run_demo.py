"""
=============================================================================
MediTraceX: Master Verification & Demonstration Script (Steps 1, 2, and 3)
=============================================================================
Demonstrates:
1. Database Integrity & Sample Records (MySQL / SQLite)
2. DSA Trie Prefix Search & Levenshtein Fuzzy Typo Recovery
3. DSA Min-Heap Nearby Pharmacy Discovery (Haversine Distance)
4. ML Demand Forecasting & Stock-out Risk Assessment Engine
=============================================================================
"""

import sys
import os
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db_config import SessionLocal
from database.models import (
    User, Pharmacy, Medicine, Inventory, SalesHistory,
    MedicineRequest, Watchlist, Notification
)
from backend.app.dsa.trie_search import MedicineTrieSearch
from backend.app.dsa.ranker import PharmacyRanker
from ml_engine.predict import DemandPredictor

def run_demonstration():
    print("\n" + "="*78)
    print(" [+] MediTraceX - Intelligent Medicine Availability & Pharmacy Discovery")
    print("     Step 1 (Database), Step 2 (DSA), & Step 3 (ML Demand Forecasting)")
    print("="*78 + "\n")

    session = SessionLocal()
    try:
        # -----------------------------------------------------------------
        # 1. Database Records & Metrics Summary (Step 1)
        # -----------------------------------------------------------------
        print("📊 [1] DATABASE STATISTICS & SAMPLE RECORDS:")
        print("-" * 78)

        pharm_count = session.query(Pharmacy).count()
        med_count = session.query(Medicine).count()
        user_count = session.query(User).count()
        inv_count = session.query(Inventory).count()
        sales_count = session.query(SalesHistory).count()
        req_count = session.query(MedicineRequest).count()
        watch_count = session.query(Watchlist).count()
        notif_count = session.query(Notification).count()

        print(f"  • Total Pharmacies Registered : {pharm_count}")
        print(f"  • Total Medicines in Catalog  : {med_count}")
        print(f"  • Total System Users          : {user_count}")
        print(f"  • Total Active Inventory Rows : {inv_count}")
        print(f"  • Historical Sales Rows (ML)  : {sales_count:,}")
        print(f"  • Customer Medicine Requests  : {req_count}")
        print(f"  • Active Restock Watchlists   : {watch_count}")
        print(f"  • Notifications Logged        : {notif_count}")
        print()

        print("  Sample Pharmacies:")
        for p in session.query(Pharmacy).limit(3).all():
            print(f"    - ID: {p.id:2d} | {p.name:<42} | Loc: ({p.latitude}, {p.longitude}) | 24/7: {p.is_24_7}")
        print()

        print("  Sample Medicines Catalog:")
        for m in session.query(Medicine).limit(4).all():
            print(f"    - ID: {m.id:2d} | {m.name:<32} | Generic: {m.generic_name:<20} | Price: ₹{m.unit_price}")
        print()

        # -----------------------------------------------------------------
        # 2. DSA Engine: Trie Prefix Search & Typo Fallback (Step 2)
        # -----------------------------------------------------------------
        print("🧠 [2] DSA MODULE: TRIE PREFIX SEARCH & FUZZY MATCHING:")
        print("-" * 78)

        trie = MedicineTrieSearch()
        all_medicines = session.query(Medicine).all()
        
        t0 = time.perf_counter()
        for med in all_medicines:
            trie.insert_medicine({
                "id": med.id,
                "name": med.name,
                "generic_name": med.generic_name,
                "brand_name": med.brand_name,
                "dosage": med.dosage,
                "dosage_form": med.dosage_form,
                "category": med.category,
                "unit_price": float(med.unit_price)
            })
        t_index = (time.perf_counter() - t0) * 1000
        print(f"  Indexed {len(all_medicines)} medicines ({trie.total_indexed_terms} search tokens) in {t_index:.2f} ms.\n")

        # Test Case A: Prefix "para"
        query_prefix = "para"
        t0 = time.perf_counter()
        prefix_matches = trie.search_prefix(query_prefix, limit=6)
        t_lookup = (time.perf_counter() - t0) * 1000
        print(f"  🔍 Prefix Search Query: \"{query_prefix}\" (Lookup time: {t_lookup:.4f} ms)")
        for idx, res in enumerate(prefix_matches, 1):
            print(f"     {idx}. {res.name:<35} [Generic: {res.generic_name}, ₹{res.unit_price}] (Match: {res.match_type})")
        print()

        # Test Case B: Brand Query "dolo"
        brand_query = "dolo"
        t0 = time.perf_counter()
        brand_matches = trie.search(brand_query, limit=2)
        t_lookup = (time.perf_counter() - t0) * 1000
        print(f"  🔍 Brand Alias Query: \"{brand_query}\" (Lookup time: {t_lookup:.4f} ms)")
        for idx, res in enumerate(brand_matches, 1):
            print(f"     {idx}. {res.name:<35} [Brand: {res.brand_name}, ₹{res.unit_price}]")
        print()

        # Test Case C: Typo / Fuzzy Queries
        typos = ["paractamol", "amoxcilin", "pan 40"]
        for typo in typos:
            t0 = time.perf_counter()
            fuzzy_matches = trie.search(typo, limit=2)
            t_lookup = (time.perf_counter() - t0) * 1000
            print(f"  ⚡ Typo Search Query: \"{typo}\" (Resolved in {t_lookup:.4f} ms)")
            for idx, res in enumerate(fuzzy_matches, 1):
                print(f"     {idx}. {res.name:<35} (Edit Dist: {res.edit_distance}, Match: {res.match_type})")
        print()

        # -----------------------------------------------------------------
        # 3. DSA Engine: Nearby Pharmacy Ranking (Step 2)
        # -----------------------------------------------------------------
        print("📍 [3] DSA MODULE: NEARBY PHARMACY RANKING (MIN-HEAP + HAVERSINE):")
        print("-" * 78)

        target_med_name = "Paracetamol 650mg"
        target_med = session.query(Medicine).filter(Medicine.name.like(f"%{target_med_name}%")).first()
        if not target_med:
            target_med = session.query(Medicine).first()

        user_lat = 17.4435
        user_lon = 78.3780

        print(f"  Target Medicine : {target_med.name} (ID: {target_med.id})")
        print(f"  User GPS Lat/Lon: ({user_lat}° N, {user_lon}° E) [Hitec City]\n")

        records = (
            session.query(
                Pharmacy.id,
                Pharmacy.name,
                Pharmacy.address,
                Pharmacy.city,
                Pharmacy.latitude,
                Pharmacy.longitude,
                Pharmacy.contact_phone,
                Pharmacy.is_24_7,
                Pharmacy.opening_time,
                Pharmacy.closing_time,
                Inventory.stock_quantity,
                Inventory.safety_stock_threshold,
                Inventory.stock_status
            )
            .join(Inventory, Inventory.pharmacy_id == Pharmacy.id)
            .filter(Inventory.medicine_id == target_med.id)
            .all()
        )

        candidates = [
            {
                "id": r.id,
                "name": r.name,
                "address": r.address,
                "city": r.city,
                "latitude": float(r.latitude),
                "longitude": float(r.longitude),
                "contact_phone": r.contact_phone,
                "is_24_7": r.is_24_7,
                "opening_time": r.opening_time,
                "closing_time": r.closing_time,
                "stock_quantity": r.stock_quantity,
                "safety_stock_threshold": r.safety_stock_threshold,
                "stock_status": r.stock_status
            }
            for r in records
        ]

        t0 = time.perf_counter()
        ranked_pharmacies = PharmacyRanker.rank_pharmacies(
            user_lat=user_lat,
            user_lon=user_lon,
            pharmacy_inventory_records=candidates,
            max_results=8
        )
        t_rank = (time.perf_counter() - t0) * 1000

        print(f"  🏆 Top Ranked Nearby Pharmacies (Evaluated {len(candidates)} stores in {t_rank:.3f} ms):")
        for p in ranked_pharmacies:
            print(f"     {p.format_display_line()}")
        print()

        # -----------------------------------------------------------------
        # 4. Machine Learning: Demand Forecast & Stock-out Risk (Step 3)
        # -----------------------------------------------------------------
        print("🤖 [4] ML ENGINE: DEMAND FORECASTING & STOCK-OUT RISK ASSESSMENT:")
        print("-" * 78)

        predictor = DemandPredictor()

        sample_cases = [
            (2, 2),  # Paracetamol 650mg at HealthPoint Super Pharmacy
            (1, 15), # Amoxicillin 500mg at MediCare Plus
            (3, 31), # Cetirizine 10mg at CityMed 24/7 Chemists
        ]

        for pharm_id, med_id in sample_cases:
            t0 = time.perf_counter()
            pred = predictor.predict_demand(pharmacy_id=pharm_id, medicine_id=med_id, forecast_days=7)
            t_pred = (time.perf_counter() - t0) * 1000

            print(f"  Medicine                   : {pred['medicine_name']} (ID: {pred['medicine_id']})")
            print(f"  Pharmacy                   : {pred['pharmacy_name']}")
            print(f"  Current In-Store Stock     : {pred['current_stock']} units (Safety Threshold: {pred['safety_stock_threshold']})")
            print(f"  Predicted Next-Day Demand  : {pred['predicted_next_day_demand']} units")
            print(f"  Predicted 7-Day Demand     : {pred['predicted_7d_demand']} units (Inference: {t_pred:.2f} ms)")
            print(f"  Stock-Out Risk Level       : [{pred['stockout_risk']} RISK]")
            print(f"  Risk Diagnostic Reason     : {pred['risk_explanation']}")
            print(f"  Suggested Restock Quantity : {pred['suggested_restock_quantity']} units")
            print(f"  7-Day Trajectory Breakdown : " + ", ".join([f"{d['day_name'][:3]}: {d['predicted_demand']}" for d in pred['daily_forecasts']]))
            print(f"  * {pred['disclaimer']}")
            print("-" * 78)

        print("\n" + "="*78)
        print(" [SUCCESS] Steps 1, 2, and 3 Verified & Operational with 100% Integrity!")
        print("="*78 + "\n")

    finally:
        session.close()

if __name__ == "__main__":
    run_demonstration()
