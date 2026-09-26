"""
MediTraceX DSA Engine Unit Tests
Tests Trie Prefix Search, Typo/Fuzzy Search, Haversine Distance, and Priority Queue Pharmacy Ranker.
"""

import sys
import os
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.dsa.trie_search import MedicineTrieSearch
from backend.app.dsa.ranker import PharmacyRanker, StockAvailabilityTier

class TestDSAEngine(unittest.TestCase):

    def setUp(self):
        self.trie = MedicineTrieSearch()
        
        # Sample medicines catalog
        self.sample_medicines = [
            {"id": 1, "name": "Paracetamol 500mg", "generic_name": "Paracetamol", "brand_name": "Calpol 500", "dosage": "500mg", "dosage_form": "Tablet", "category": "Analgesic", "unit_price": 18.50},
            {"id": 2, "name": "Paracetamol 650mg", "generic_name": "Paracetamol", "brand_name": "Dolo 650", "dosage": "650mg", "dosage_form": "Tablet", "category": "Analgesic", "unit_price": 32.00},
            {"id": 3, "name": "Paracetamol Syrup", "generic_name": "Paracetamol", "brand_name": "Calpol Pead Syrup", "dosage": "120mg/5ml", "dosage_form": "Syrup", "category": "Analgesic", "unit_price": 45.00},
            {"id": 4, "name": "Amoxicillin 500mg", "generic_name": "Amoxicillin", "brand_name": "Novamox 500", "dosage": "500mg", "dosage_form": "Capsule", "category": "Antibiotic", "unit_price": 78.50},
            {"id": 5, "name": "Cetirizine 10mg", "generic_name": "Cetirizine HCl", "brand_name": "Cetzine 10", "dosage": "10mg", "dosage_form": "Tablet", "category": "Antihistamine", "unit_price": 24.00},
            {"id": 6, "name": "Pantoprazole 40mg", "generic_name": "Pantoprazole Sodium", "brand_name": "Pan 40", "dosage": "40mg", "dosage_form": "Tablet", "category": "Gastrointestinal", "unit_price": 115.00},
        ]

        for med in self.sample_medicines:
            self.trie.insert_medicine(med)

    # -----------------------------------------------------------------
    # 1. Trie Search Tests
    # -----------------------------------------------------------------
    def test_trie_prefix_search(self):
        """Testing 'para' prefix search returns all Paracetamol variants."""
        results = self.trie.search_prefix("para")
        result_names = [r.name for r in results]
        
        self.assertIn("Paracetamol 500mg", result_names)
        self.assertIn("Paracetamol 650mg", result_names)
        self.assertIn("Paracetamol Syrup", result_names)
        self.assertNotIn("Amoxicillin 500mg", result_names)

    def test_trie_brand_alias_search(self):
        """Testing brand lookup 'dolo' maps to Paracetamol 650mg."""
        results = self.trie.search("dolo")
        self.assertTrue(any("650mg" in r.name or "Dolo" in r.brand_name for r in results))

    def test_trie_fuzzy_typo_search(self):
        """Testing typo tolerance 'paractamol' and 'amoxcilin'."""
        typo_para = self.trie.fuzzy_search("paractamol", max_distance=2)
        self.assertGreater(len(typo_para), 0)
        self.assertTrue(any("Paracetamol" in r.name for r in typo_para))

        typo_amox = self.trie.fuzzy_search("amoxcilin", max_distance=2)
        self.assertGreater(len(typo_amox), 0)
        self.assertEqual(typo_amox[0].name, "Amoxicillin 500mg")

    # -----------------------------------------------------------------
    # 2. Pharmacy Ranker Tests
    # -----------------------------------------------------------------
    def test_haversine_distance(self):
        """Test Haversine distance accuracy between known coordinates."""
        # Jubilee Hills (17.4325, 78.4071) to Madhapur (17.4483, 78.3742) ~ 3.9 km
        dist = PharmacyRanker.calculate_haversine_distance(17.4325, 78.4071, 17.4483, 78.3742)
        self.assertAlmostEqual(dist, 3.89, delta=0.5)

    def test_pharmacy_ranking_rule(self):
        """
        Verify Ranking Rules:
        - In Stock pharmacies with shortest distance come first.
        - Low Stock pharmacies come next.
        - Out of Stock pharmacies come last.
        """
        user_lat, user_lon = 17.4400, 78.3800 # User at Hitec City

        test_pharmacies = [
            {"id": 1, "name": "MediCare Pharmacy", "address": "Addr 1", "city": "Hyd", "latitude": 17.4450, "longitude": 78.3850, "stock_quantity": 45, "safety_stock_threshold": 15}, # ~0.8 km, In Stock
            {"id": 2, "name": "HealthPoint Pharmacy", "address": "Addr 2", "city": "Hyd", "latitude": 17.4500, "longitude": 78.3900, "stock_quantity": 6, "safety_stock_threshold": 15}, # ~1.5 km, Low Stock
            {"id": 3, "name": "CityMed Pharmacy", "address": "Addr 3", "city": "Hyd", "latitude": 17.4550, "longitude": 78.3950, "stock_quantity": 80, "safety_stock_threshold": 15}, # ~2.2 km, In Stock
            {"id": 4, "name": "ZeroStock Chemist", "address": "Addr 4", "city": "Hyd", "latitude": 17.4410, "longitude": 78.3810, "stock_quantity": 0, "safety_stock_threshold": 15}, # ~0.1 km, Out of Stock
        ]

        ranked = PharmacyRanker.rank_pharmacies(user_lat, user_lon, test_pharmacies, max_results=10)
        
        self.assertEqual(len(ranked), 4)
        
        # Rank 1 must be MediCare Pharmacy (In Stock, 0.8 km)
        self.assertEqual(ranked[0].pharmacy_name, "MediCare Pharmacy")
        self.assertEqual(ranked[0].stock_status, "Available")

        # Rank 2 must be CityMed Pharmacy (In Stock, 2.2 km - closer than Low stock or prioritised over low stock)
        self.assertEqual(ranked[1].pharmacy_name, "CityMed Pharmacy")
        self.assertEqual(ranked[1].stock_status, "Available")

        # Rank 3 must be HealthPoint Pharmacy (Low Stock, 1.5 km)
        self.assertEqual(ranked[2].pharmacy_name, "HealthPoint Pharmacy")
        self.assertEqual(ranked[2].stock_status, "Low Stock")

        # Rank 4 must be ZeroStock Chemist (Out of Stock, despite being physically closest)
        self.assertEqual(ranked[3].pharmacy_name, "ZeroStock Chemist")
        self.assertEqual(ranked[3].stock_status, "Out of Stock")

if __name__ == "__main__":
    unittest.main()
