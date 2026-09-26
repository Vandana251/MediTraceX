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

    def test_sales_history_table(self):
        count = self.session.query(SalesHistory).count()
        self.assertIsInstance(count, int, "SalesHistory table should be queryable")

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

    def test_empty_db_startup_seeds_core_catalog_only(self):
        """
        Validates requirement: On an empty database, init_db / seed_core_catalog
        must seed the minimum essential catalog (pharmacies, medicines, inventory, users)
        and NOT generate the 100,800+ historical sales records.
        """
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from database.db_config import Base
        from database.seed_data import seed_core_catalog, seed_historical_sales

        mem_engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(bind=mem_engine)
        MemSession = sessionmaker(bind=mem_engine)
        session = MemSession()

        try:
            # Seed core catalog only
            seed_core_catalog(session)
            session.commit()

            pharm_cnt = session.query(Pharmacy).count()
            med_cnt = session.query(Medicine).count()
            user_cnt = session.query(User).count()
            inv_cnt = session.query(Inventory).count()
            sales_cnt = session.query(SalesHistory).count()

            self.assertGreaterEqual(pharm_cnt, 20)
            self.assertGreaterEqual(med_cnt, 100)
            self.assertGreaterEqual(user_cnt, 5)
            self.assertGreaterEqual(inv_cnt, 2000)
            # Crucial requirement: No 100,800 sales records on normal startup
            self.assertEqual(sales_cnt, 0, "Normal startup must not generate heavy sales records")

            # Test explicitly calling historical sales simulation
            seed_historical_sales(session, days_history=3)
            session.commit()
            sales_after = session.query(SalesHistory).count()
            self.assertGreater(sales_after, 0, "Explicit historical sales simulation should seed records")

        finally:
            session.close()

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

