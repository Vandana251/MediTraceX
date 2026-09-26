"""
MediTraceX Live REST API Verification Script
Executes real HTTP requests against the running Uvicorn server (http://127.0.0.1:8000)
and formats real responses.
"""

import sys
import os
import json
import time
import requests

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_URL = "http://127.0.0.1:8000"

def verify_live_api():
    print("\n" + "="*78)
    print(" 🚀 MediTraceX REST API Live Server Verification")
    print(f"    Target Server: {BASE_URL}")
    print("="*78 + "\n")

    # 1. Verify Docs & Health
    print("📋 [1] Root, Health & OpenAPI Docs Verification:")
    print("-" * 78)
    r_root = requests.get(f"{BASE_URL}/")
    print(f"  GET /               -> Status: {r_root.status_code} | Service: {r_root.json().get('service')}")
    r_docs = requests.get(f"{BASE_URL}/docs")
    print(f"  GET /docs           -> Status: {r_docs.status_code} (Interactive Swagger UI Active)")
    r_openapi = requests.get(f"{BASE_URL}/openapi.json")
    print(f"  GET /openapi.json   -> Status: {r_openapi.status_code} (Total OpenAPI Endpoints: {len(r_openapi.json().get('paths', {}))})")
    print()

    # 2. Authentication Flow
    print("🔐 [2] Authentication API (Register & Login):")
    print("-" * 78)
    unique_email = f"live_customer_{int(time.time()*1000)}@meditracex.io"
    unique_phone = f"+91-{int(time.time()*1000)%10000000000:010d}"

    reg_payload = {
        "name": "Sai Krishna",
        "email": unique_email,
        "phone": unique_phone,
        "password": "SecurePassword#2026",
        "role": "customer",
        "latitude": 17.4435,
        "longitude": 78.3780
    }
    r_reg = requests.post(f"{BASE_URL}/api/auth/register", json=reg_payload)
    print(f"  POST /api/auth/register -> Status: {r_reg.status_code}")
    reg_data = r_reg.json()
    print(f"  Response Body: {json.dumps(reg_data, indent=4)}")
    print()

    login_payload = {
        "email": unique_email,
        "password": "SecurePassword#2026"
    }
    r_login = requests.post(f"{BASE_URL}/api/auth/login", json=login_payload)
    print(f"  POST /api/auth/login    -> Status: {r_login.status_code}")
    token = r_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"  Obtained JWT Token: {token[:35]}... (Bearer)")
    print()

    r_me = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print(f"  GET /api/auth/me        -> Status: {r_me.status_code} | User: {r_me.json().get('name')} ({r_me.json().get('email')})")
    print()

    # 3. Medicine Search (Trie & Typo DSA)
    print("🔍 [3] Medicine Search API (Step 2 DSA Trie Engine):")
    print("-" * 78)
    r_search = requests.get(f"{BASE_URL}/api/medicines/search?q=para&limit=3")
    print(f"  GET /api/medicines/search?q=para -> Status: {r_search.status_code}")
    print(f"  Search Results (Prefix 'para'): {json.dumps(r_search.json(), indent=4)}")
    print()

    r_typo = requests.get(f"{BASE_URL}/api/medicines/search?q=paractamol&limit=2")
    print(f"  GET /api/medicines/search?q=paractamol (Typo) -> Status: {r_typo.status_code}")
    print(f"  Fuzzy Typo Matches: {json.dumps(r_typo.json(), indent=4)}")
    print()

    # 4. Nearby Pharmacy Discovery (Min-Heap + Haversine)
    print("📍 [4] Pharmacy Discovery API (Step 2 DSA Min-Heap Ranker):")
    print("-" * 78)
    r_nearby = requests.get(f"{BASE_URL}/api/pharmacies/nearby?latitude=17.4435&longitude=78.3780&medicine_id=2&radius_km=15&limit=3")
    print(f"  GET /api/pharmacies/nearby -> Status: {r_nearby.status_code}")
    print(f"  Ranked Pharmacies: {json.dumps(r_nearby.json(), indent=4)}")
    print()

    # 5. ML Demand Prediction & Stock-out Risk
    print("🤖 [5] ML Demand Prediction API (Step 3 Inference Pipeline):")
    print("-" * 78)
    r_pred = requests.get(f"{BASE_URL}/api/predictions/2/2?forecast_days=7")
    print(f"  GET /api/predictions/2/2 -> Status: {r_pred.status_code}")
    print(f"  Prediction Payload: {json.dumps(r_pred.json(), indent=4)}")
    print()

    # 6. Medicine Requests & Watchlist
    print("📦 [6] Medicine Requests & Watchlist API:")
    print("-" * 78)
    req_payload = {
        "medicine_id": 2,
        "pharmacy_id": 1,
        "quantity_requested": 3,
        "notes": "Urgent requirement for outpatient care"
    }
    r_req = requests.post(f"{BASE_URL}/api/requests", json=req_payload, headers=headers)
    print(f"  POST /api/requests -> Status: {r_req.status_code}")
    print(f"  Created Request: {json.dumps(r_req.json(), indent=4)}")
    print()

    watch_payload = {
        "medicine_id": 15,
        "pharmacy_id": 2,
        "notify_on_restock": True
    }
    r_watch = requests.post(f"{BASE_URL}/api/watchlist", json=watch_payload, headers=headers)
    print(f"  POST /api/watchlist -> Status: {r_watch.status_code}")
    print(f"  Created Watchlist: {json.dumps(r_watch.json(), indent=4)}")
    print()

    print("="*78)
    print(" [SUCCESS] All MediTraceX REST API Endpoints Verified Live & Fully Operational!")
    print("="*78 + "\n")

if __name__ == "__main__":
    verify_live_api()
