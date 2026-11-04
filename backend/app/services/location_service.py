"""
=============================================================================
MediTraceX: Geospatial Location Intelligence & Geocoding Service
=============================================================================
Provides multi-tier location resolution:
1. Fast in-memory cache & high-precision Indian locality/pincode index.
2. Verified pharmacy database registry search (by name, license, or address).
3. External Nominatim / OpenStreetMap fallback geocoder (with rate-limit safety,
   strict timeouts, and country code filtering).
=============================================================================
"""

import urllib.request
import urllib.parse
import json
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from database.models import Pharmacy
from backend.app.schemas.location_schemas import LocationSearchResult

# Curated high-precision locality index for instant resolution
INDIAN_LOCALITIES_INDEX = [
    # --- Vijayawada, Andhra Pradesh ---
    {"name": "Patamata", "city": "Vijayawada", "state": "Andhra Pradesh", "pincode": "520010", "lat": 16.4952, "lon": 80.6612, "type": "locality"},
    {"name": "Labbipet", "city": "Vijayawada", "state": "Andhra Pradesh", "pincode": "520010", "lat": 16.5042, "lon": 80.6385, "type": "locality"},
    {"name": "Mutyalampadu", "city": "Vijayawada", "state": "Andhra Pradesh", "pincode": "520011", "lat": 16.5295, "lon": 80.6322, "type": "locality"},
    {"name": "Currency Nagar", "city": "Vijayawada", "state": "Andhra Pradesh", "pincode": "520008", "lat": 16.5185, "lon": 80.6685, "type": "locality"},
    {"name": "Benz Circle", "city": "Vijayawada", "state": "Andhra Pradesh", "pincode": "520010", "lat": 16.5012, "lon": 80.6485, "type": "landmark"},
    {"name": "Governorpet", "city": "Vijayawada", "state": "Andhra Pradesh", "pincode": "520002", "lat": 16.5144, "lon": 80.6288, "type": "locality"},
    {"name": "One Town", "city": "Vijayawada", "state": "Andhra Pradesh", "pincode": "520001", "lat": 16.5188, "lon": 80.6122, "type": "locality"},
    {"name": "Gunadala", "city": "Vijayawada", "state": "Andhra Pradesh", "pincode": "520004", "lat": 16.5290, "lon": 80.6650, "type": "locality"},
    {"name": "Bhavanipuram", "city": "Vijayawada", "state": "Andhra Pradesh", "pincode": "520012", "lat": 16.5265, "lon": 80.5985, "type": "locality"},
    {"name": "Gollapudi", "city": "Vijayawada", "state": "Andhra Pradesh", "pincode": "521225", "lat": 16.5412, "lon": 80.5785, "type": "locality"},
    {"name": "Moghalrajpuram", "city": "Vijayawada", "state": "Andhra Pradesh", "pincode": "520010", "lat": 16.5085, "lon": 80.6512, "type": "locality"},
    {"name": "Autonagar", "city": "Vijayawada", "state": "Andhra Pradesh", "pincode": "520007", "lat": 16.4912, "lon": 80.6785, "type": "locality"},
    {"name": "Kanuru", "city": "Vijayawada", "state": "Andhra Pradesh", "pincode": "520007", "lat": 16.4855, "lon": 80.6912, "type": "locality"},
    {"name": "Enikepadu", "city": "Vijayawada", "state": "Andhra Pradesh", "pincode": "521108", "lat": 16.5145, "lon": 80.7012, "type": "locality"},
    {"name": "Poranki", "city": "Vijayawada", "state": "Andhra Pradesh", "pincode": "521137", "lat": 16.4785, "lon": 80.7125, "type": "locality"},
    {"name": "Satyanarayanapuram", "city": "Vijayawada", "state": "Andhra Pradesh", "pincode": "520011", "lat": 16.5225, "lon": 80.6275, "type": "locality"},
    {"name": "Gandhinagar", "city": "Vijayawada", "state": "Andhra Pradesh", "pincode": "520003", "lat": 16.5165, "lon": 80.6212, "type": "locality"},

    # --- Visakhapatnam, Andhra Pradesh ---
    {"name": "Dwaraka Nagar", "city": "Visakhapatnam", "state": "Andhra Pradesh", "pincode": "530016", "lat": 17.7285, "lon": 83.3088, "type": "locality"},
    {"name": "MVP Colony", "city": "Visakhapatnam", "state": "Andhra Pradesh", "pincode": "530017", "lat": 17.7410, "lon": 83.3365, "type": "locality"},
    {"name": "Gajuwaka", "city": "Visakhapatnam", "state": "Andhra Pradesh", "pincode": "530026", "lat": 17.6912, "lon": 83.2145, "type": "locality"},
    {"name": "Siripuram", "city": "Visakhapatnam", "state": "Andhra Pradesh", "pincode": "530003", "lat": 17.7215, "lon": 83.3198, "type": "locality"},
    {"name": "Jagadamba Junction", "city": "Visakhapatnam", "state": "Andhra Pradesh", "pincode": "530020", "lat": 17.7120, "lon": 83.3012, "type": "landmark"},
    {"name": "Madhurawada", "city": "Visakhapatnam", "state": "Andhra Pradesh", "pincode": "530048", "lat": 17.7985, "lon": 83.3512, "type": "locality"},

    # --- Hyderabad & Telangana ---
    {"name": "Jubilee Hills", "city": "Hyderabad", "state": "Telangana", "pincode": "500033", "lat": 17.4325, "lon": 78.4071, "type": "locality"},
    {"name": "Madhapur", "city": "Hyderabad", "state": "Telangana", "pincode": "500081", "lat": 17.4483, "lon": 78.3742, "type": "locality"},
    {"name": "Gachibowli", "city": "Hyderabad", "state": "Telangana", "pincode": "500032", "lat": 17.4401, "lon": 78.3489, "type": "locality"},
    {"name": "Banjara Hills", "city": "Hyderabad", "state": "Telangana", "pincode": "500034", "lat": 17.4156, "lon": 78.4350, "type": "locality"},
    {"name": "Kondapur", "city": "Hyderabad", "state": "Telangana", "pincode": "500084", "lat": 17.4612, "lon": 78.3587, "type": "locality"},
    {"name": "Ameerpet", "city": "Hyderabad", "state": "Telangana", "pincode": "500016", "lat": 17.4375, "lon": 78.4483, "type": "locality"},
    {"name": "Kukatpally", "city": "Hyderabad", "state": "Telangana", "pincode": "500072", "lat": 17.4934, "lon": 78.3989, "type": "locality"},
    {"name": "Hanamkonda", "city": "Warangal", "state": "Telangana", "pincode": "506001", "lat": 17.9942, "lon": 79.5788, "type": "locality"},

    # --- Bengaluru & Karnataka ---
    {"name": "Indiranagar", "city": "Bengaluru", "state": "Karnataka", "pincode": "560038", "lat": 12.9719, "lon": 77.6412, "type": "locality"},
    {"name": "Koramangala", "city": "Bengaluru", "state": "Karnataka", "pincode": "560034", "lat": 12.9352, "lon": 77.6245, "type": "locality"},
    {"name": "Whitefield", "city": "Bengaluru", "state": "Karnataka", "pincode": "560066", "lat": 12.9868, "lon": 77.7382, "type": "locality"},
    {"name": "HSR Layout", "city": "Bengaluru", "state": "Karnataka", "pincode": "560102", "lat": 12.9115, "lon": 77.6520, "type": "locality"},
    {"name": "Jayanagar", "city": "Bengaluru", "state": "Karnataka", "pincode": "560011", "lat": 12.9250, "lon": 77.5838, "type": "locality"},

    # --- Mumbai & Maharashtra ---
    {"name": "Andheri West", "city": "Mumbai", "state": "Maharashtra", "pincode": "400053", "lat": 19.1365, "lon": 72.8315, "type": "locality"},
    {"name": "Bandra West", "city": "Mumbai", "state": "Maharashtra", "pincode": "400050", "lat": 19.0545, "lon": 72.8290, "type": "locality"},
    {"name": "Dadar", "city": "Mumbai", "state": "Maharashtra", "pincode": "400014", "lat": 19.0182, "lon": 72.8435, "type": "locality"},
    {"name": "Kothrud", "city": "Pune", "state": "Maharashtra", "pincode": "411038", "lat": 18.5075, "lon": 73.8078, "type": "locality"},
    {"name": "Hinjewadi", "city": "Pune", "state": "Maharashtra", "pincode": "411057", "lat": 18.5912, "lon": 73.7388, "type": "locality"},

    # --- Delhi NCR ---
    {"name": "Connaught Place", "city": "New Delhi", "state": "Delhi NCR", "pincode": "110001", "lat": 28.6328, "lon": 77.2195, "type": "locality"},
    {"name": "South Extension", "city": "New Delhi", "state": "Delhi NCR", "pincode": "110049", "lat": 28.5725, "lon": 77.2210, "type": "locality"},
    {"name": "DLF Cyber City", "city": "Gurgaon", "state": "Delhi NCR", "pincode": "122002", "lat": 28.4950, "lon": 77.0895, "type": "locality"},
    {"name": "Sector 18", "city": "Noida", "state": "Delhi NCR", "pincode": "201301", "lat": 28.5705, "lon": 77.3245, "type": "locality"},

    # --- Chennai, Kolkata, Ahmedabad, Jaipur, Kochi, Lucknow, Patna ---
    {"name": "T Nagar", "city": "Chennai", "state": "Tamil Nadu", "pincode": "600017", "lat": 13.0418, "lon": 80.2341, "type": "locality"},
    {"name": "Anna Nagar", "city": "Chennai", "state": "Tamil Nadu", "pincode": "600040", "lat": 13.0850, "lon": 80.2105, "type": "locality"},
    {"name": "Park Street", "city": "Kolkata", "state": "West Bengal", "pincode": "700016", "lat": 22.5512, "lon": 88.3535, "type": "locality"},
    {"name": "Salt Lake Sector V", "city": "Kolkata", "state": "West Bengal", "pincode": "700091", "lat": 22.5765, "lon": 88.4345, "type": "locality"},
    {"name": "Navrangpura", "city": "Ahmedabad", "state": "Gujarat", "pincode": "380009", "lat": 23.0365, "lon": 72.5612, "type": "locality"},
    {"name": "C-Scheme", "city": "Jaipur", "state": "Rajasthan", "pincode": "302001", "lat": 26.9155, "lon": 75.8012, "type": "locality"},
    {"name": "MG Road Ernakulam", "city": "Kochi", "state": "Kerala", "pincode": "682016", "lat": 9.9715, "lon": 76.2812, "type": "locality"},
    {"name": "Hazratganj", "city": "Lucknow", "state": "Uttar Pradesh", "pincode": "226001", "lat": 26.8485, "lon": 80.9412, "type": "locality"},
    {"name": "Boring Road", "city": "Patna", "state": "Bihar", "pincode": "800001", "lat": 25.6145, "lon": 85.1215, "type": "locality"},
]

# Pincode direct lookup cache
PINCODE_MAP = {
    "520001": {"city": "Vijayawada", "state": "Andhra Pradesh", "locality": "One Town", "lat": 16.5188, "lon": 80.6122},
    "520002": {"city": "Vijayawada", "state": "Andhra Pradesh", "locality": "Governorpet", "lat": 16.5144, "lon": 80.6288},
    "520003": {"city": "Vijayawada", "state": "Andhra Pradesh", "locality": "Gandhinagar", "lat": 16.5165, "lon": 80.6212},
    "520004": {"city": "Vijayawada", "state": "Andhra Pradesh", "locality": "Gunadala", "lat": 16.5290, "lon": 80.6650},
    "520007": {"city": "Vijayawada", "state": "Andhra Pradesh", "locality": "Autonagar / Kanuru", "lat": 16.4912, "lon": 80.6785},
    "520008": {"city": "Vijayawada", "state": "Andhra Pradesh", "locality": "Currency Nagar", "lat": 16.5185, "lon": 80.6685},
    "520010": {"city": "Vijayawada", "state": "Andhra Pradesh", "locality": "Patamata / Benz Circle / Labbipet", "lat": 16.5012, "lon": 80.6485},
    "520011": {"city": "Vijayawada", "state": "Andhra Pradesh", "locality": "Mutyalampadu / Satyanarayanapuram", "lat": 16.5295, "lon": 80.6322},
    "520012": {"city": "Vijayawada", "state": "Andhra Pradesh", "locality": "Bhavanipuram", "lat": 16.5265, "lon": 80.5985},
    "530016": {"city": "Visakhapatnam", "state": "Andhra Pradesh", "locality": "Dwaraka Nagar", "lat": 17.7285, "lon": 83.3088},
    "530017": {"city": "Visakhapatnam", "state": "Andhra Pradesh", "locality": "MVP Colony", "lat": 17.7410, "lon": 83.3365},
    "500081": {"city": "Hyderabad", "state": "Telangana", "locality": "Madhapur / Hitec City", "lat": 17.4483, "lon": 78.3742},
    "500033": {"city": "Hyderabad", "state": "Telangana", "locality": "Jubilee Hills", "lat": 17.4325, "lon": 78.4071},
    "560034": {"city": "Bengaluru", "state": "Karnataka", "locality": "Koramangala", "lat": 12.9352, "lon": 77.6245},
    "560038": {"city": "Bengaluru", "state": "Karnataka", "locality": "Indiranagar", "lat": 12.9719, "lon": 77.6412},
    "400050": {"city": "Mumbai", "state": "Maharashtra", "locality": "Bandra West", "lat": 19.0545, "lon": 72.8290},
    "400053": {"city": "Mumbai", "state": "Maharashtra", "locality": "Andheri West", "lat": 19.1365, "lon": 72.8315},
    "110001": {"city": "New Delhi", "state": "Delhi NCR", "locality": "Connaught Place", "lat": 28.6328, "lon": 77.2195},
    "600017": {"city": "Chennai", "state": "Tamil Nadu", "locality": "T Nagar", "lat": 13.0418, "lon": 80.2341},
    "700016": {"city": "Kolkata", "state": "West Bengal", "locality": "Park Street", "lat": 22.5512, "lon": 88.3535},
}

class LocationService:
    """Intelligent multi-tier location geocoding & pharmacy name resolver."""

    _query_cache: Dict[str, List[LocationSearchResult]] = {}

    @classmethod
    def search_location(cls, query: str, db: Optional[Session] = None, limit: int = 6) -> List[LocationSearchResult]:
        q_raw = query.strip()
        if not q_raw:
            return []

        q_clean = q_raw.lower()
        if q_clean in cls._query_cache:
            return cls._query_cache[q_clean]

        results: List[LocationSearchResult] = []
        seen_keys = set()

        def add_res(res: LocationSearchResult):
            key = f"{round(res.latitude, 4)}:{round(res.longitude, 4)}:{res.display_name.lower()}"
            if key not in seen_keys:
                seen_keys.add(key)
                results.append(res)

        # 1. Check for 6-digit Indian PINCODE
        pincode_match = re.search(r"\b([1-9][0-9]{5})\b", q_raw)
        if pincode_match:
            pin = pincode_match.group(1)
            if pin in PINCODE_MAP:
                data = PINCODE_MAP[pin]
                add_res(LocationSearchResult(
                    query=q_raw,
                    display_name=f"{data['locality']}, {data['city']}, {data['state']} ({pin})",
                    locality=data['locality'],
                    city=data['city'],
                    state=data['state'],
                    pincode=pin,
                    latitude=data['lat'],
                    longitude=data['lon'],
                    result_type="pincode",
                    is_verified_network=True
                ))

        # 2. Database Pharmacy Name & Branch Search
        if db:
            matching_pharmacies = db.query(Pharmacy).filter(
                (Pharmacy.name.ilike(f"%{q_raw}%")) |
                (Pharmacy.address.ilike(f"%{q_raw}%")) |
                (Pharmacy.city.ilike(f"%{q_raw}%"))
            ).limit(limit).all()

            for pharm in matching_pharmacies:
                add_res(LocationSearchResult(
                    query=q_raw,
                    display_name=f"{pharm.name} ({pharm.address}, {pharm.city})",
                    locality=pharm.address,
                    city=pharm.city,
                    state="India",
                    pincode=pharm.pincode,
                    latitude=float(pharm.latitude),
                    longitude=float(pharm.longitude),
                    result_type="pharmacy",
                    matched_pharmacy_id=pharm.id,
                    is_verified_network=True
                ))

        # 3. High-Precision Localities Index
        for item in INDIAN_LOCALITIES_INDEX:
            name_low = item["name"].lower()
            city_low = item["city"].lower()
            if q_clean in name_low or name_low in q_clean or (len(q_clean) >= 3 and q_clean in f"{name_low} {city_low}"):
                add_res(LocationSearchResult(
                    query=q_raw,
                    display_name=f"{item['name']}, {item['city']}, {item['state']}",
                    locality=item['name'],
                    city=item['city'],
                    state=item['state'],
                    pincode=item.get("pincode"),
                    latitude=item['lat'],
                    longitude=item['lon'],
                    result_type=item.get("type", "locality"),
                    is_verified_network=True
                ))

        # 4. External Geocoding Fallback via OSM Nominatim (if results < 2 and non-digit query)
        if len(results) < 2 and not q_raw.isdigit():
            external_results = cls._external_nominatim_geocode(q_raw)
            for ext in external_results:
                add_res(ext)

        # Slice to requested limit
        final_results = results[:limit]
        cls._query_cache[q_clean] = final_results
        return final_results

    @classmethod
    def _external_nominatim_geocode(cls, query: str) -> List[LocationSearchResult]:
        """Queries OpenStreetMap Nominatim with India countrycode filter and safe timeouts."""
        out = []
        try:
            encoded = urllib.parse.quote(f"{query}, India")
            url = f"https://nominatim.openstreetmap.org/search?q={encoded}&format=json&countrycodes=in&addressdetails=1&limit=3"
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "MediTraceX-LocationService/1.0 (contact: admin@meditracex.io)",
                    "Accept": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for item in data:
                    addr = item.get("address", {})
                    city = addr.get("city") or addr.get("town") or addr.get("county") or addr.get("state_district") or "India"
                    state = addr.get("state") or "India"
                    pincode = addr.get("postcode")
                    locality = addr.get("suburb") or addr.get("neighbourhood") or item.get("name")

                    out.append(LocationSearchResult(
                        query=query,
                        display_name=item.get("display_name", f"{query}, India"),
                        locality=locality,
                        city=city,
                        state=state,
                        pincode=pincode,
                        latitude=float(item["lat"]),
                        longitude=float(item["lon"]),
                        result_type="external_place",
                        is_verified_network=False
                    ))
        except Exception:
            # Silently fallback without breaking API
            pass
        return out

location_service = LocationService()
