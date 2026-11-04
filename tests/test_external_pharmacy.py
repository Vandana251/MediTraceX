import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.main import app
from backend.app.services.external_pharmacy_service import (
    ExternalPharmacyService,
    external_pharmacy_service,
    haversine_distance,
)

client = TestClient(app)


class TestExternalPharmacyDiscovery:
    """Test suite for Real-World External Pharmacy Discovery via Overpass API."""

    def test_haversine_distance_accuracy(self):
        # Distance between Patamata (16.4952, 80.6612) and Benz Circle (16.5012, 80.6485)
        dist = haversine_distance(16.4952, 80.6612, 16.5012, 80.6485)
        assert 1.3 <= dist <= 1.7

    def test_patamata_vijayawada_external_discovery(self):
        """Test real external pharmacy discovery near Patamata, Vijayawada."""
        response = client.get(
            "/api/pharmacies/external-nearby",
            params={"latitude": 16.4952, "longitude": 80.6612, "radius_km": 5.0, "limit": 15},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["search_latitude"] == 16.4952
        assert data["search_longitude"] == 80.6612
        assert "results" in data
        assert isinstance(data["results"], list)
        assert "Nearby pharmacies found from connected location data" in data["data_notice"]

        # If live network is available, check fields of returned items
        if data["total_found"] > 0:
            first = data["results"][0]
            assert "name" in first
            assert "latitude" in first
            assert "longitude" in first
            assert "distance_km" in first
            assert first["verification_status"] == "Inventory Not Verified"
            assert first["is_verified_network"] is False
            # Verify sorted by distance ascending
            distances = [item["distance_km"] for item in data["results"]]
            assert distances == sorted(distances)

    def test_labbipet_and_520010_discovery(self):
        """Test external discovery in Labbipet / 520010 Vijayawada."""
        response = client.get(
            "/api/pharmacies/external-nearby",
            params={"latitude": 16.5012, "longitude": 80.6485, "radius_km": 5.0, "limit": 10},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_found"] >= 0

    def test_major_metros_discovery(self):
        """Test external discovery across Hyderabad, Bengaluru, Mumbai."""
        metros = [
            ("Hyderabad", 17.4435, 78.3780),
            ("Bengaluru", 12.9352, 77.6245),
            ("Mumbai", 19.0760, 72.8777),
        ]
        for name, lat, lon in metros:
            response = client.get(
                "/api/pharmacies/external-nearby",
                params={"latitude": lat, "longitude": lon, "radius_km": 5.0, "limit": 10},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["search_latitude"] == lat
            assert data["search_longitude"] == lon

    def test_radius_filtering_1km_vs_5km(self):
        """Test that smaller radius strictly filters out farther results."""
        res_1km = client.get(
            "/api/pharmacies/external-nearby",
            params={"latitude": 16.4952, "longitude": 80.6612, "radius_km": 1.0, "limit": 25},
        )
        assert res_1km.status_code == 200
        data_1km = res_1km.json()
        for item in data_1km["results"]:
            assert item["distance_km"] <= 1.05

        res_5km = client.get(
            "/api/pharmacies/external-nearby",
            params={"latitude": 16.4952, "longitude": 80.6612, "radius_km": 5.0, "limit": 25},
        )
        assert res_5km.status_code == 200
        data_5km = res_5km.json()
        for item in data_5km["results"]:
            assert item["distance_km"] <= 5.05

    def test_invalid_coordinates_validation(self):
        """Test API validation for out-of-range latitude/longitude."""
        response = client.get(
            "/api/pharmacies/external-nearby",
            params={"latitude": 195.0, "longitude": 80.0},
        )
        assert response.status_code == 422

    def test_mirror_fallback_and_graceful_failure(self, monkeypatch):
        """Test that service gracefully handles mirror failure without crashing."""
        service = ExternalPharmacyService()
        
        # Simulate all mirrors raising exceptions
        def broken_query(mirror_url, query, timeout_seconds=3.5):
            return None

        monkeypatch.setattr(service, "_query_overpass_mirror", broken_query)

        result = service.get_nearby_external_pharmacies(16.4952, 80.6612, radius_km=5.0)
        assert result.total_found == 0
        assert result.results == []

    def test_deduplication_logic(self, monkeypatch):
        """Test that duplicate coordinate nodes and identical nearby names are deduplicated."""
        service = ExternalPharmacyService()

        # Mock raw Overpass elements with duplicates
        mock_elements = [
            {
                "type": "node",
                "id": 1001,
                "lat": 16.4950,
                "lon": 80.6610,
                "tags": {"name": "Apollo Pharmacy", "phone": "0866123456"},
            },
            {
                "type": "node",
                "id": 1002,
                "lat": 16.4950,  # Duplicate exact coordinate
                "lon": 80.6610,
                "tags": {"name": "Apollo Pharmacy Duplicate", "phone": "0866123456"},
            },
            {
                "type": "node",
                "id": 1003,
                "lat": 16.4980,
                "lon": 80.6630,
                "tags": {"name": "Unique Meds Store"},
            },
        ]

        monkeypatch.setattr(service, "fetch_from_overpass", lambda lat, lon, radius_km: mock_elements)

        result = service.get_nearby_external_pharmacies(16.4952, 80.6612, radius_km=5.0)
        assert result.total_found == 2
        names = [item.name for item in result.results]
        assert "Apollo Pharmacy" in names
        assert "Unique Meds Store" in names
        assert "Apollo Pharmacy Duplicate" not in names
