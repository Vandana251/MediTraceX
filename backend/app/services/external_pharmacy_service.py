import heapq
import json
import logging
import math
import time
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Tuple

from backend.app.schemas.external_pharmacy_schemas import (
    ExternalPharmacyItem,
    ExternalPharmacyResponse,
)

logger = logging.getLogger("meditracex.external_pharmacy")

OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

CACHE_TTL_SECONDS = 3600  # 1 hour in-memory cache


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Great Circle distance between two coordinates in kilometers."""
    r = 6371.0  # Earth radius in kilometers
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r * c, 2)


class ExternalPharmacyService:
    """Service to discover real-world external pharmacies and medical shops via Overpass API."""

    def __init__(self):
        self._cache: Dict[str, Tuple[float, List[ExternalPharmacyItem]]] = {}

    def _get_cache_key(self, lat: float, lon: float, radius_km: float) -> str:
        return f"{round(lat, 3)}:{round(lon, 3)}:{round(radius_km, 1)}"

    def _query_overpass_mirror(
        self, mirror_url: str, query: str, timeout_seconds: float = 6.5
    ) -> Optional[dict]:
        try:
            data = urllib.parse.urlencode({"data": query}).encode("utf-8")
            req = urllib.request.Request(
                mirror_url,
                data=data,
                headers={
                    "User-Agent": "MediTraceX-HealthPOI/1.0 (India Pharmacy Proximity Discovery)",
                    "Accept": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
                if response.status == 200:
                    raw_data = response.read().decode("utf-8")
                    return json.loads(raw_data)
        except Exception as exc:
            logger.debug("Overpass mirror %s failed: %s", mirror_url, exc)
            return None
        return None

    def fetch_from_overpass(
        self, lat: float, lon: float, radius_km: float
    ) -> List[dict]:
        radius_m = int(min(max(radius_km, 0.5), 100.0) * 1000)
        query = f"""
        [out:json][timeout:10];
        (
          node["amenity"="pharmacy"](around:{radius_m},{lat},{lon});
          node["healthcare"="pharmacy"](around:{radius_m},{lat},{lon});
          node["shop"="chemist"](around:{radius_m},{lat},{lon});
          node["shop"="medical_supply"](around:{radius_m},{lat},{lon});
          way["amenity"="pharmacy"](around:{radius_m},{lat},{lon});
          way["healthcare"="pharmacy"](around:{radius_m},{lat},{lon});
          way["shop"="chemist"](around:{radius_m},{lat},{lon});
        );
        out center 60;
        """

        for mirror in OVERPASS_MIRRORS:
            result = self._query_overpass_mirror(mirror, query, timeout_seconds=6.5)
            if result and "elements" in result and len(result["elements"]) > 0:
                return result.get("elements", [])

        return []

    def get_nearby_external_pharmacies(
        self,
        lat: float,
        lon: float,
        radius_km: float = 5.0,
        limit: int = 25,
    ) -> ExternalPharmacyResponse:
        """Discover real-world external pharmacies within radius_km, ranked by distance."""
        cache_key = self._get_cache_key(lat, lon, radius_km)
        now = time.time()

        # Check in-memory cache
        if cache_key in self._cache:
            timestamp, cached_items = self._cache[cache_key]
            if now - timestamp < CACHE_TTL_SECONDS:
                return ExternalPharmacyResponse(
                    search_latitude=lat,
                    search_longitude=lon,
                    radius_km=radius_km,
                    total_found=len(cached_items[:limit]),
                    results=cached_items[:limit],
                )

        elements = self.fetch_from_overpass(lat, lon, radius_km)
        if not elements:
            return ExternalPharmacyResponse(
                search_latitude=lat,
                search_longitude=lon,
                radius_km=radius_km,
                total_found=0,
                results=[],
            )

        seen_coords = set()
        seen_names = set()
        min_heap: List[Tuple[float, int, ExternalPharmacyItem]] = []
        counter = 0

        for el in elements:
            tags = el.get("tags", {})
            item_lat = el.get("lat") or el.get("center", {}).get("lat")
            item_lon = el.get("lon") or el.get("center", {}).get("lon")

            if item_lat is None or item_lon is None:
                continue

            try:
                item_lat = float(item_lat)
                item_lon = float(item_lon)
            except (ValueError, TypeError):
                continue

            # Deduplication by geographic precision (approx 10 meters)
            coord_key = (round(item_lat, 4), round(item_lon, 4))
            if coord_key in seen_coords:
                continue
            seen_coords.add(coord_key)

            # Name resolution
            name = (
                tags.get("name")
                or tags.get("name:en")
                or tags.get("brand")
                or tags.get("operator")
                or "Local Medical Shop / Chemist"
            ).strip()

            # Deduplicate exact name in exact 50m radius
            norm_name_key = f"{name.lower()}:{round(item_lat, 3)}:{round(item_lon, 3)}"
            if norm_name_key in seen_names:
                continue
            seen_names.add(norm_name_key)

            # Distance via Haversine
            dist = haversine_distance(lat, lon, item_lat, item_lon)
            if dist > radius_km:
                continue

            # Address synthesis
            address_parts = [
                tags.get("addr:housenumber"),
                tags.get("addr:housename"),
                tags.get("addr:street") or tags.get("road"),
                tags.get("addr:suburb") or tags.get("neighbourhood"),
                tags.get("addr:city"),
            ]
            address = ", ".join([p for p in address_parts if p]) or tags.get("addr:full")

            # Contact and hours
            phone = (
                tags.get("phone")
                or tags.get("contact:phone")
                or tags.get("contact:mobile")
            )
            hours = tags.get("opening_hours")
            city = tags.get("addr:city") or tags.get("city")
            state = tags.get("addr:state") or tags.get("state")
            pincode = tags.get("addr:postcode") or tags.get("postal_code")
            osm_id = f"{el.get('type', 'node')}/{el.get('id', '')}"

            item = ExternalPharmacyItem(
                name=name,
                address=address,
                latitude=item_lat,
                longitude=item_lon,
                distance_km=dist,
                phone=phone,
                opening_hours=hours,
                city=city,
                state=state,
                pincode=pincode,
                source="OpenStreetMap Overpass",
                verification_status="Inventory Not Verified",
                is_verified_network=False,
                osm_id=osm_id,
            )

            # Min-Heap push: sorted by distance
            counter += 1
            heapq.heappush(min_heap, (dist, counter, item))

        # Extract sorted results from min-heap
        sorted_results: List[ExternalPharmacyItem] = []
        while min_heap:
            _, _, item = heapq.heappop(min_heap)
            sorted_results.append(item)

        # Cache results for 1 hour
        self._cache[cache_key] = (now, sorted_results)

        # Evict oldest cache entries if cache grows beyond 500 entries
        if len(self._cache) > 500:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][0])
            self._cache.pop(oldest_key, None)

        final_slice = sorted_results[:limit]
        return ExternalPharmacyResponse(
            search_latitude=lat,
            search_longitude=lon,
            radius_km=radius_km,
            total_found=len(final_slice),
            results=final_slice,
        )


external_pharmacy_service = ExternalPharmacyService()
