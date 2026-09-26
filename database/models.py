"""
SQLAlchemy ORM Models for MediTraceX
Reflects schema.sql with relationships, constraints, and typed fields.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Boolean,
    Numeric, Date, DateTime, Time, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from database.db_config import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    phone = Column(String(20), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False, default="customer") # customer, pharmacy_admin, system_admin
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relationships
    requests = relationship("MedicineRequest", back_populates="user", cascade="all, delete-orphan")
    watchlist_items = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Pharmacy(Base):
    __tablename__ = "pharmacies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    license_number = Column(String(80), nullable=False, unique=True)
    address = Column(String(255), nullable=False)
    city = Column(String(80), nullable=False)
    pincode = Column(String(15), nullable=False)
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    contact_phone = Column(String(25), nullable=False)
    contact_email = Column(String(150), nullable=False)
    opening_time = Column(Time, nullable=False)
    closing_time = Column(Time, nullable=False)
    is_24_7 = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relationships
    inventory_records = relationship("Inventory", back_populates="pharmacy", cascade="all, delete-orphan")
    sales = relationship("SalesHistory", back_populates="pharmacy", cascade="all, delete-orphan")


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(180), nullable=False, index=True)
    generic_name = Column(String(180), nullable=False, index=True)
    brand_name = Column(String(120), nullable=False)
    dosage = Column(String(50), nullable=False)
    dosage_form = Column(String(50), nullable=False, default="Tablet")
    manufacturer = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    is_prescription_required = Column(Boolean, nullable=False, default=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relationships
    inventory_items = relationship("Inventory", back_populates="medicine", cascade="all, delete-orphan")
    sales_records = relationship("SalesHistory", back_populates="medicine", cascade="all, delete-orphan")


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id", ondelete="CASCADE"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="RESTRICT"), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    safety_stock_threshold = Column(Integer, nullable=False, default=15)
    reorder_quantity = Column(Integer, nullable=False, default=50)
    batch_number = Column(String(60), nullable=False)
    expiry_date = Column(Date, nullable=False)
    stock_status = Column(String(30), nullable=False, default="In Stock") # 'In Stock', 'Low Stock', 'Out of Stock'
    last_restocked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        UniqueConstraint("pharmacy_id", "medicine_id", name="uq_pharmacy_medicine"),
        Index("idx_inventory_status_qty", "stock_status", "stock_quantity"),
    )

    # Relationships
    pharmacy = relationship("Pharmacy", back_populates="inventory_records")
    medicine = relationship("Medicine", back_populates="inventory_items")


class SalesHistory(Base):
    __tablename__ = "sales_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id", ondelete="CASCADE"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="RESTRICT"), nullable=False)
    sale_date = Column(Date, nullable=False, index=True)
    quantity_sold = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    day_of_week = Column(String(15), nullable=False)
    is_weekend = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_sales_query", "medicine_id", "sale_date"),
        Index("idx_sales_pharm_date", "pharmacy_id", "sale_date"),
    )

    pharmacy = relationship("Pharmacy", back_populates="sales")
    medicine = relationship("Medicine", back_populates="sales_records")


class MedicineRequest(Base):
    __tablename__ = "medicine_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id", ondelete="SET NULL"), nullable=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="RESTRICT"), nullable=False)
    quantity_requested = Column(Integer, nullable=False, default=1)
    status = Column(String(30), nullable=False, default="PENDING") # PENDING, ACCEPTED, FULFILLED, CANCELLED, NOT_AVAILABLE
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="requests")
    pharmacy = relationship("Pharmacy")
    medicine = relationship("Medicine")


class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False)
    target_pharmacy_id = Column(Integer, ForeignKey("pharmacies.id", ondelete="CASCADE"), nullable=True)
    notify_on_restock = Column(Boolean, nullable=False, default=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "medicine_id", "target_pharmacy_id", name="uq_user_med_pharm"),
    )

    user = relationship("User", back_populates="watchlist_items")
    medicine = relationship("Medicine")
    pharmacy = relationship("Pharmacy")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(40), nullable=False) # RESTOCK_ALERT, DEMAND_SURGE, REQUEST_STATUS, LOW_STOCK_WARNING
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
