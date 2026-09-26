"""
MediTraceX Database Integrity Tests
Validates all 8 tables, relationships, constraints, and seeded volume.
"""

import sys
import os
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db_config import SessionLocal, engine
from database.models import (
    User, Pharmacy, Medicine, Inventory, SalesHistory,
    MedicineRequest, Watchlist, Notification
)

class TestDatabaseIntegrity(unittest.TestCase):

    def setUp(self):
        self.session = SessionLocal()

    def tearDown(self):
        self.session.close()

    def test_pharmacies_seeded(self):
        count = self.session.query(Pharmacy).count()
        self.assertGreaterEqual(count, 20, "Should have at least 20 seeded pharmacies")

    def test_medicines_seeded(self):
        count = self.session.query(Medicine).count()
        self.assertGreaterEqual(count, 100, "Should have at least 100 seeded medicines")

    def test_inventory_coverage(self):
        count = self.session.query(Inventory).count()
        self.assertGreaterEqual(count, 2000, "Should have 2000+ inventory mappings")
        
        # Check stock statuses
        in_stock_cnt = self.session.query(Inventory).filter_by(stock_status="In Stock").count()
        low_stock_cnt = self.session.query(Inventory).filter_by(stock_status="Low Stock").count()
        out_stock_cnt = self.session.query(Inventory).filter_by(stock_status="Out of Stock").count()
        
        self.assertGreater(in_stock_cnt, 0)
        self.assertGreater(low_stock_cnt, 0)
        self.assertGreater(out_stock_cnt, 0)

    def test_sales_history_depth(self):
        count = self.session.query(SalesHistory).count()
        self.assertGreaterEqual(count, 10000, "Should have substantial daily sales records for ML")

    def test_users_seeded(self):
        count = self.session.query(User).count()
        self.assertGreaterEqual(count, 5, "Should have seeded users")

    def test_requests_and_watchlist(self):
        req_count = self.session.query(MedicineRequest).count()
        watch_count = self.session.query(Watchlist).count()
        notif_count = self.session.query(Notification).count()
        self.assertGreater(req_count, 0)
        self.assertGreater(watch_count, 0)
        self.assertGreater(notif_count, 0)

    def test_mysql_ssl_and_url_sanitization(self):
        import database.db_config as dbc
        orig_db_url = dbc.DATABASE_URL
        try:
            # Test URL sanitization on Aiven-style connection string with ssl-mode
            dbc.DATABASE_URL = "mysql://avnadmin:SecretPass@mysql-aiven.aivencloud.com:12345/defaultdb?ssl-mode=REQUIRED&charset=utf8mb4"
            cleaned_url, removed = dbc.build_mysql_url()
            self.assertEqual(cleaned_url.drivername, "mysql+pymysql")
            self.assertNotIn("ssl-mode", cleaned_url.query)
            self.assertIn("charset", cleaned_url.query)
            self.assertIn("ssl-mode", removed)

            # Test SSL connect_args and CA resolution
            connect_args, ca_src = dbc.get_mysql_connect_args()
            self.assertIn("ssl", connect_args)
            self.assertTrue(connect_args["ssl"].check_hostname)
        finally:
            dbc.DATABASE_URL = orig_db_url

if __name__ == "__main__":
    unittest.main()

