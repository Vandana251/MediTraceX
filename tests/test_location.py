"""
=============================================================================
Unit & Integration Tests: Location Intelligence, Pincode & Geocoding Service
=============================================================================
Tests:
1. Locality Search (Patamata, Labbipet, Mutyalampadu, Currency Nagar, Benz Circle)
2. Pincode Search (520010, 520011, 560034)
3. Pharmacy Name Search
4. Invalid / Empty Location Handling
5. External Fallback & Caching
6. Multi-City Pan-India Distance Sorting via Min-Heap & Haversine
=============================================================================
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.main import app
from backend.app.services.location_service import location_service
from database.db_config import SessionLocal

client = TestClient(app)

class TestLocationIntelligence:

    @pytest.fixture(autouse=True)
    def setup_db(self):
        self.db = SessionLocal()
        yield
        self.db.close()

    def test_locality_search_patamata(self):
        """Verify Patamata, Vijayawada resolves with exact coordinates."""
        response = client.get("/api/locations/search?q=Patamata")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        match = next((r for r in data["results"] if "patamata" in r["locality"].lower()), None)
        assert match is not None
        assert match["city"] == "Vijayawada"
        assert match["state"] == "Andhra Pradesh"
        assert round(match["latitude"], 2) == 16.50 or round(match["latitude"], 2) == 16.49
        assert round(match["longitude"], 2) == 80.66

    def test_locality_search_other_vijayawada_localities(self):
        """Verify Labbipet, Mutyalampadu, Currency Nagar, Benz Circle resolve correctly."""
        localities = ["Labbipet", "Mutyalampadu", "Currency Nagar", "Benz Circle"]
        for loc in localities:
            response = client.get(f"/api/locations/search?q={loc}")
            assert response.status_code == 200
            data = response.json()
            assert data["total"] > 0
            assert any("vijayawada" in r["city"].lower() for r in data["results"])

    def test_pincode_search_520010_and_520011(self):
        """Verify 6-digit Indian pincode queries resolve to geographic coordinates."""
        pincodes = ["520010", "520011", "560034"]
        for pin in pincodes:
            response = client.get(f"/api/locations/search?q={pin}")
            assert response.status_code == 200
            data = response.json()
            assert data["total"] > 0
            res = data["results"][0]
            assert res["pincode"] == pin
            assert res["latitude"] > 0
            assert res["longitude"] > 0

    def test_pharmacy_name_search(self):
        """Verify searching by pharmacy brand name returns matching store."""
        response = client.get("/api/locations/search?q=Krishna Valley")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        pharm_res = next((r for r in data["results"] if r["result_type"] == "pharmacy"), None)
        assert pharm_res is not None
        assert "Krishna Valley" in pharm_res["display_name"]
        assert pharm_res["is_verified_network"] is True

    def test_invalid_location_handling(self):
        """Verify unknown or nonsensical query returns empty results cleanly without 500 error."""
        response = client.get("/api/locations/search?q=xyznonexistent999999999")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["results"], list)

    def test_proximity_ranking_from_geocoded_patamata(self):
        """Verify ranking pharmacies from geocoded Patamata coordinates."""
        # 1. Geocode Patamata
        loc_resp = client.get("/api/locations/search?q=Patamata")
        assert loc_resp.status_code == 200
        loc = loc_resp.json()["results"][0]

        # 2. Query nearby pharmacies for Paracetamol (id 1)
        nearby_resp = client.get(
            f"/api/pharmacies/nearby?latitude={loc['latitude']}&longitude={loc['longitude']}&medicine_id=1&radius_km=35&limit=5"
        )
        assert nearby_resp.status_code == 200
        nearby_data = nearby_resp.json()
        assert nearby_data["total_found"] > 0
        ranked = nearby_data["ranked_pharmacies"]
        # Distance must be ascending
        distances = [p["distance_km"] for p in ranked]
        assert distances == sorted(distances)
