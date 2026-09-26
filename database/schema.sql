-- =====================================================================
-- MediTraceX: Intelligent Medicine Availability & Pharmacy Discovery Platform
-- Complete Database Schema (MySQL Compatible)
-- =====================================================================

-- 1. Database Creation (if not exists)
CREATE DATABASE IF NOT EXISTS meditracex_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE meditracex_db;

-- ---------------------------------------------------------------------
-- 2. Drop Tables in reverse dependency order for clean recreation
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS watchlist;
DROP TABLE IF EXISTS medicine_requests;
DROP TABLE IF EXISTS sales_history;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS medicines;
DROP TABLE IF EXISTS pharmacies;
DROP TABLE IF EXISTS users;

-- ---------------------------------------------------------------------
-- Table: users
-- Roles: 'customer', 'pharmacy_admin', 'system_admin'
-- ---------------------------------------------------------------------
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('customer', 'pharmacy_admin', 'system_admin') NOT NULL DEFAULT 'customer',
    latitude DECIMAL(10, 8) NULL,
    longitude DECIMAL(11, 8) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_role (role),
    INDEX idx_user_location (latitude, longitude)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table: pharmacies
-- Represents physical or network pharmacies with precise GPS coordinates
-- ---------------------------------------------------------------------
CREATE TABLE pharmacies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    license_number VARCHAR(80) NOT NULL UNIQUE,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(80) NOT NULL,
    pincode VARCHAR(15) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    contact_phone VARCHAR(25) NOT NULL,
    contact_email VARCHAR(150) NOT NULL,
    opening_time TIME NOT NULL DEFAULT '08:00:00',
    closing_time TIME NOT NULL DEFAULT '22:00:00',
    is_24_7 BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_pharmacy_geo (latitude, longitude),
    INDEX idx_pharmacy_city (city),
    INDEX idx_pharmacy_active (is_active)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table: medicines
-- Catalog of medicines, active ingredients, forms, and pricing
-- ---------------------------------------------------------------------
CREATE TABLE medicines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(180) NOT NULL,
    generic_name VARCHAR(180) NOT NULL,
    brand_name VARCHAR(120) NOT NULL,
    dosage VARCHAR(50) NOT NULL,
    dosage_form ENUM('Tablet', 'Capsule', 'Syrup', 'Injection', 'Ointment', 'Inhaler', 'Drops', 'Powder') NOT NULL DEFAULT 'Tablet',
    manufacturer VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    is_prescription_required BOOLEAN NOT NULL DEFAULT FALSE,
    unit_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_medicine_name (name),
    INDEX idx_medicine_generic (generic_name),
    INDEX idx_medicine_category (category)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table: inventory
-- Real-time stock levels of medicines across different pharmacies
-- ---------------------------------------------------------------------
CREATE TABLE inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pharmacy_id INT NOT NULL,
    medicine_id INT NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    safety_stock_threshold INT NOT NULL DEFAULT 15,
    reorder_quantity INT NOT NULL DEFAULT 50,
    batch_number VARCHAR(60) NOT NULL,
    expiry_date DATE NOT NULL,
    stock_status ENUM('In Stock', 'Low Stock', 'Out of Stock') NOT NULL DEFAULT 'In Stock',
    last_restocked_at TIMESTAMP NULL DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_pharmacy_medicine UNIQUE (pharmacy_id, medicine_id),
    CONSTRAINT fk_inventory_pharmacy FOREIGN KEY (pharmacy_id) REFERENCES pharmacies (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_inventory_medicine FOREIGN KEY (medicine_id) REFERENCES medicines (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_inventory_stock_status (stock_status),
    INDEX idx_inventory_qty (stock_quantity)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table: sales_history
-- Granular daily sales records (used for ML Demand Prediction)
-- ---------------------------------------------------------------------
CREATE TABLE sales_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pharmacy_id INT NOT NULL,
    medicine_id INT NOT NULL,
    sale_date DATE NOT NULL,
    quantity_sold INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    day_of_week VARCHAR(15) NOT NULL,
    is_weekend BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sales_pharmacy FOREIGN KEY (pharmacy_id) REFERENCES pharmacies (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_sales_medicine FOREIGN KEY (medicine_id) REFERENCES medicines (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_sales_date_med (medicine_id, sale_date),
    INDEX idx_sales_pharm_date (pharmacy_id, sale_date)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table: medicine_requests
-- Customer requests for urgent or out-of-stock medicines
-- ---------------------------------------------------------------------
CREATE TABLE medicine_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    pharmacy_id INT NULL,
    medicine_id INT NOT NULL,
    quantity_requested INT NOT NULL DEFAULT 1,
    status ENUM('PENDING', 'ACCEPTED', 'FULFILLED', 'CANCELLED', 'NOT_AVAILABLE') NOT NULL DEFAULT 'PENDING',
    notes TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_req_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_req_pharmacy FOREIGN KEY (pharmacy_id) REFERENCES pharmacies (id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_req_medicine FOREIGN KEY (medicine_id) REFERENCES medicines (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_req_status (status)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table: watchlist
-- Users can subscribe to medicine restock alerts when unavailable
-- ---------------------------------------------------------------------
CREATE TABLE watchlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    medicine_id INT NOT NULL,
    target_pharmacy_id INT NULL,
    notify_on_restock BOOLEAN NOT NULL DEFAULT TRUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_med_pharm UNIQUE (user_id, medicine_id, target_pharmacy_id),
    CONSTRAINT fk_watch_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_watch_medicine FOREIGN KEY (medicine_id) REFERENCES medicines (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_watch_pharmacy FOREIGN KEY (target_pharmacy_id) REFERENCES pharmacies (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Table: notifications
-- User & Pharmacy in-app notifications
-- ---------------------------------------------------------------------
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('RESTOCK_ALERT', 'DEMAND_SURGE', 'REQUEST_STATUS', 'LOW_STOCK_WARNING') NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notif_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_notif_user_read (user_id, is_read)
) ENGINE=InnoDB;
