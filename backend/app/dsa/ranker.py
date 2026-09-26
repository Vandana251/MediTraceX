"""
=============================================================================
MediTraceX: Pharmacy Ranking & Discovery Engine (DSA Module)
=============================================================================
Module: backend.app.dsa.ranker

Description:
    Provides transparent, priority-queue-driven geospatial ranking of nearby
    pharmacies for any target medicine based on:
    1. Stock Availability Tier (In Stock > Low Stock > Out of Stock)
    2. Haversine Geographic Distance (Min-Heap / Shortest Distance First)
    3. Available Stock Quantity as tie-breaker

Note:
    Pharmacy store ratings are explicitly NOT used as the primary ranking factor,
    prioritizing patient health urgency and shortest physical accessibility.

Algorithm & Complexity:
    - Distance Calculation: O(1) per pharmacy using Great-Circle Haversine Formula.
    - Priority Queue / Min-Heap Sorting:
        - Insertion / Heapify: O(P log K) or O(P) where P is total candidate
          pharmacies and K is desired top-N results.
        - Extraction: O(K log P) for retrieving top-K closest ranked stores.
    - Space Complexity: O(P) to maintain the min-heap and candidate state.
=============================================================================
"""

import math
import heapq
from enum import IntEnum
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field


class StockAvailabilityTier(IntEnum):
    """
    Priority Tiers for stock availability.
    Lower numerical values receive higher priority in Min-Heap.
    """
    IN_STOCK = 0      # Full availability (quantity >= safety threshold)
    LOW_STOCK = 1     # Limited units (1 <= quantity < safety threshold)
    OUT_OF_STOCK = 2  # Stock is 0 (can place restock request / watchlist)


@dataclass(order=True)
class PharmacyCandidate:
    """
    Heap element wrapper designed for transparent Min-Heap ordering.
    Tuples are naturally sorted by:
    1. tier (IN_STOCK=0, LOW_STOCK=1, OUT_OF_STOCK=2)
    2. distance_km (ascending: shortest distance first)
    3. negative stock_quantity (descending: higher stock preferred on tie)
    """
    tier: int
    distance_km: float
    neg_stock: int
    pharmacy_id: int
    payload: Dict[str, Any] = field(compare=False)


@dataclass
class PharmacyRankingResult:
    """Standardized output structure for ranked pharmacy response."""
    rank: int
    pharmacy_id: int
    pharmacy_name: str
    address: str
    city: str
    distance_km: float
    stock_quantity: int
    stock_status: str
    availability_tier: str
    contact_phone: str
    is_24_7: bool
    opening_time: str
    closing_time: str
    latitude: float
    longitude: float

    def format_display_line(self) -> str:
        """Returns clean human-readable CLI/Log line."""
        return f"{self.rank}. {self.pharmacy_name} — {self.distance_km:.1f} km — {self.stock_status} (Stock: {self.stock_quantity})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "pharmacy_id": self.pharmacy_id,
            "pharmacy_name": self.pharmacy_name,
            "address": self.address,
            "city": self.city,
            "distance_km": round(self.distance_km, 2),
            "stock_quantity": self.stock_quantity,
            "stock_status": self.stock_status,
            "availability_tier": self.availability_tier,
            "contact_phone": self.contact_phone,
            "is_24_7": self.is_24_7,
            "opening_time": self.opening_time,
            "closing_time": self.closing_time,
            "latitude": self.latitude,
            "longitude": self.longitude
        }


class PharmacyRanker:
    """
    Geospatial & Inventory Ranking Engine using Priority Queue (Min-Heap).
    """

    EARTH_RADIUS_KM: float = 6371.0088

    @classmethod
    def calculate_haversine_distance(
        cls,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculates Great-Circle distance between two coordinates using the Haversine formula.
        
        Formula:
            a = sin^2(dlat/2) + cos(lat1) * cos(lat2) * sin^2(dlon/2)
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            d = R * c
            
        Time Complexity: O(1)
        """
        # Convert decimal degrees to radians
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        # Haversine calculation
        a = (
            math.sin(delta_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        distance = cls.EARTH_RADIUS_KM * c
        return distance

    @classmethod
    def determine_availability_tier(cls, stock_qty: int, safety_threshold: int = 15) -> Tuple[StockAvailabilityTier, str]:
        """Classifies stock quantity into transparent availability tiers."""
        if stock_qty <= 0:
            return StockAvailabilityTier.OUT_OF_STOCK, "Out of Stock"
        elif stock_qty < safety_threshold:
            return StockAvailabilityTier.LOW_STOCK, "Low Stock"
        else:
            return StockAvailabilityTier.IN_STOCK, "Available"

    @classmethod
    def rank_pharmacies(
        cls,
        user_lat: float,
        user_lon: float,
        pharmacy_inventory_records: List[Dict[str, Any]],
        max_results: int = 10,
        max_radius_km: Optional[float] = None
    ) -> List[PharmacyRankingResult]:
        """
        Ranks candidate pharmacies using a Min-Heap Priority Queue.
        
        Parameters:
            user_lat (float): User's current latitude
            user_lon (float): User's current longitude
            pharmacy_inventory_records (List[Dict]): List of pharmacy records joined with inventory for a medicine
            max_results (int): Maximum number of top ranked pharmacies to return
            max_radius_km (Optional[float]): Optional filter to limit search radius
            
        Returns:
            List[PharmacyRankingResult]: Ranked list ordered by Availability Tier, Distance, and Stock.
            
        Time Complexity:
            O(P log K) where P is total pharmacies and K is max_results.
        """
        min_heap: List[PharmacyCandidate] = []

        for record in pharmacy_inventory_records:
            pharm_lat = float(record["latitude"])
            pharm_lon = float(record["longitude"])
            stock_qty = int(record.get("stock_quantity", 0))
            safety_threshold = int(record.get("safety_stock_threshold", 15))

            dist_km = cls.calculate_haversine_distance(user_lat, user_lon, pharm_lat, pharm_lon)

            # Optional radius filtering
            if max_radius_km is not None and dist_km > max_radius_km:
                continue

            tier, tier_label = cls.determine_availability_tier(stock_qty, safety_threshold)

            candidate = PharmacyCandidate(
                tier=int(tier),
                distance_km=dist_km,
                neg_stock=-stock_qty,
                pharmacy_id=int(record["id"]),
                payload={
                    "record": record,
                    "tier_label": tier_label,
                    "stock_qty": stock_qty
                }
            )
            heapq.heappush(min_heap, candidate)

        # Extract top K elements in priority order from the Min-Heap
        ranked_results: List[PharmacyRankingResult] = []
        rank_idx = 1

        while min_heap and len(ranked_results) < max_results:
            top = heapq.heappop(min_heap)
            rec = top.payload["record"]
            tier_label = top.payload["tier_label"]
            stock_qty = top.payload["stock_qty"]

            # Map stock status cleanly
            if stock_qty == 0:
                display_status = "Out of Stock"
            elif stock_qty < int(rec.get("safety_stock_threshold", 15)):
                display_status = "Low Stock"
            else:
                display_status = "Available"

            ranked_results.append(PharmacyRankingResult(
                rank=rank_idx,
                pharmacy_id=int(rec["id"]),
                pharmacy_name=rec["name"],
                address=rec["address"],
                city=rec["city"],
                distance_km=top.distance_km,
                stock_quantity=stock_qty,
                stock_status=display_status,
                availability_tier=tier_label,
                contact_phone=rec.get("contact_phone", "N/A"),
                is_24_7=bool(rec.get("is_24_7", False)),
                opening_time=str(rec.get("opening_time", "08:00")),
                closing_time=str(rec.get("closing_time", "22:00")),
                latitude=float(rec["latitude"]),
                longitude=float(rec["longitude"])
            ))
            rank_idx += 1

        return ranked_results
