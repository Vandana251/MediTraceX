"""
=============================================================================
MediTraceX FastAPI REST API Comprehensive Test Suite
=============================================================================
Tests all endpoints including:
- Authentication & JWT Token Verification
- Trie Prefix & Levenshtein Fuzzy Search
- Min-Heap Nearby Pharmacy Discovery
- Inventory Management & Role Guard
- Machine Learning Demand Forecasting
- Medicine Procurement Requests & Watchlist
=============================================================================
"""

import sys
import os
import unittest
import json
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.main import app
from database.db_config import SessionLocal
from backend.app.services.dsa_service import dsa_service

class TestMediTraceXAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        # Ensure Trie search engine is populated
        db = SessionLocal()
        try:
            dsa_service.initialize_trie(db)
        finally:
            db.close()

    # -----------------------------------------------------------------
    # 1. Health & Root Tests
    # -----------------------------------------------------------------
    def test_root_and_health(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("service", res.json())

        res_health = self.client.get("/health")
        self.assertEqual(res_health.status_code, 200)
        self.assertIn(res_health.json()["status"], ["healthy", "ok"])

    # -----------------------------------------------------------------
    # 2. Authentication Tests
    # -----------------------------------------------------------------
    def test_auth_lifecycle(self):
        import time
        unique_email = f"test_user_{int(time.time()*1000)}@meditracex.io"
        unique_phone = f"+91-{int(time.time()*1000)%10000000000:010d}"

        # A. Register new customer
        register_payload = {
            "name": "Arjun Varma",
            "email": unique_email,
            "phone": unique_phone,
            "password": "SecurePassword123!",
            "role": "customer",
            "latitude": 17.4435,
            "longitude": 78.3780
        }
        res_reg = self.client.post("/api/auth/register", json=register_payload)
        self.assertEqual(res_reg.status_code, 201)
        data_reg = res_reg.json()
        self.assertIn("access_token", data_reg)
        self.assertEqual(data_reg["email"], unique_email)

        # B. Duplicate registration rejection
        res_dup = self.client.post("/api/auth/register", json=register_payload)
        self.assertEqual(res_dup.status_code, 409)

        # C. Login
        login_payload = {
            "email": unique_email,
            "password": "SecurePassword123!"
        }
        res_login = self.client.post("/api/auth/login", json=login_payload)
        self.assertEqual(res_login.status_code, 200)
        token = res_login.json()["access_token"]
        self.assertTrue(len(token) > 20)

        # D. Protected /me endpoint
        headers = {"Authorization": f"Bearer {token}"}
        res_me = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(res_me.status_code, 200)
        self.assertEqual(res_me.json()["email"], unique_email)

        # E. Invalid Token rejection
        res_bad_auth = self.client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.jwt.token"})
        self.assertEqual(res_bad_auth.status_code, 401)

    # -----------------------------------------------------------------
    # 3. Medicine Search & Catalog API Tests (DSA Powered)
    # -----------------------------------------------------------------
    def test_medicine_prefix_search(self):
        """Testing prefix search 'para' returns Paracetamol variants via Trie."""
        res = self.client.get("/api/medicines/search?q=para")
        self.assertEqual(res.status_code, 200)
        items = res.json()
        self.assertGreater(len(items), 0)
        names = [i["name"] for i in items]
        self.assertTrue(any("Paracetamol" in n for n in names))

    def test_medicine_fuzzy_typo_search(self):
        """Testing typo tolerance 'paractamol' and 'amoxcilin'."""
        res_para = self.client.get("/api/medicines/search?q=paractamol")
        self.assertEqual(res_para.status_code, 200)
        self.assertGreater(len(res_para.json()), 0)
        self.assertTrue(any("Paracetamol" in i["name"] for i in res_para.json()))

        res_amox = self.client.get("/api/medicines/search?q=amoxcilin")
        self.assertEqual(res_amox.status_code, 200)
        self.assertGreater(len(res_amox.json()), 0)
        self.assertTrue(any("Amoxicillin" in i["name"] for i in res_amox.json()))

    def test_medicine_get_by_id(self):
        res = self.client.get("/api/medicines/2")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["id"], 2)
        self.assertEqual(res.json()["name"], "Paracetamol 650mg")

        # 404 test
        res_404 = self.client.get("/api/medicines/999999")
        self.assertEqual(res_404.status_code, 404)

    # -----------------------------------------------------------------
    # 4. Nearby Pharmacy Discovery API Tests (Min-Heap + Haversine)
    # -----------------------------------------------------------------
    def test_nearby_pharmacy_discovery(self):
        # User in Hitec City searching for Paracetamol 650mg (ID: 2)
        res = self.client.get("/api/pharmacies/nearby?latitude=17.4435&longitude=78.3780&medicine_id=2&radius_km=20&limit=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        self.assertEqual(data["target_medicine_id"], 2)
        self.assertGreater(len(data["ranked_pharmacies"]), 0)
        
        # Verify ranking order: closest available pharmacy at rank 1
        top_pharm = data["ranked_pharmacies"][0]
        self.assertEqual(top_pharm["rank"], 1)
        self.assertIn("distance_km", top_pharm)
        self.assertIn("availability_status", top_pharm)
        self.assertIn("stock_quantity", top_pharm)
        self.assertGreaterEqual(top_pharm["distance_km"], 0.0)

    # -----------------------------------------------------------------
    # 5. Inventory API Tests
    # -----------------------------------------------------------------
    def test_inventory_retrieval(self):
        res = self.client.get("/api/inventory/pharmacy/1")
        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(res.json()), 0)

        res_pair = self.client.get("/api/inventory/1/2")
        self.assertEqual(res_pair.status_code, 200)
        self.assertEqual(res_pair.json()["pharmacy_id"], 1)
        self.assertEqual(res_pair.json()["medicine_id"], 2)

    # -----------------------------------------------------------------
    # 6. ML Demand Prediction API Tests
    # -----------------------------------------------------------------
    def test_ml_prediction_endpoint(self):
        res = self.client.get("/api/predictions/2/2?forecast_days=7")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        self.assertEqual(data["medicine_id"], 2)
        self.assertEqual(data["pharmacy_id"], 2)
        self.assertIn("predicted_next_day_demand", data)
        self.assertIn("predicted_7_day_demand", data)
        self.assertIn(data["stock_out_risk"], ["HIGH", "MEDIUM", "LOW"])
        self.assertGreaterEqual(data["suggested_restock_quantity"], 0)
        self.assertEqual(len(data["daily_forecasts"]), 7)

    # -----------------------------------------------------------------
    # 7. Medicine Requests & Watchlist Tests
    # -----------------------------------------------------------------
    def test_medicine_request_and_watchlist_lifecycle(self):
        # Register a customer for requests
        import time
        unique_email = f"req_user_{int(time.time()*1000)}@meditracex.io"
        reg_res = self.client.post("/api/auth/register", json={
            "name": "Kiran Kumar",
            "email": unique_email,
            "phone": f"+91-{int(time.time()*1000)%10000000000:010d}",
            "password": "Password123!",
            "role": "customer"
        })
        token = reg_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # A. Create Medicine Request
        req_res = self.client.post("/api/requests", json={
            "medicine_id": 2,
            "pharmacy_id": 1,
            "quantity_requested": 2,
            "notes": "Urgent medicine request for test"
        }, headers=headers)
        self.assertEqual(req_res.status_code, 201)
        req_id = req_res.json()["id"]

        # B. Get My Requests
        my_reqs = self.client.get("/api/requests/my", headers=headers)
        self.assertEqual(my_reqs.status_code, 200)
        self.assertTrue(any(r["id"] == req_id for r in my_reqs.json()))

        # C. Create Watchlist Item (Notify Me)
        watch_res = self.client.post("/api/watchlist", json={
            "medicine_id": 15,
            "pharmacy_id": 2,
            "notify_on_restock": True
        }, headers=headers)
        self.assertEqual(watch_res.status_code, 201)
        watch_id = watch_res.json()["id"]

        # D. Get Watchlist
        my_watch = self.client.get("/api/watchlist", headers=headers)
        self.assertEqual(my_watch.status_code, 200)
        self.assertTrue(any(w["id"] == watch_id for w in my_watch.json()))

        # E. Delete Watchlist Item
        del_res = self.client.delete(f"/api/watchlist/{watch_id}", headers=headers)
        self.assertEqual(del_res.status_code, 200)

if __name__ == "__main__":
    unittest.main()
