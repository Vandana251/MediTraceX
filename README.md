# MediTraceX – Intelligent Medicine Availability & Pharmacy Discovery Platform

> **Find. Verify. Reach.**

MediTraceX is a full-stack healthcare technology solution designed to solve the critical problem of emergency medicine stockouts and localized pharmaceutical access.

---

## 🏗️ System Architecture

```
Android Kotlin App (Jetpack Compose)
           │
           │ HTTPS / REST
           ▼
FastAPI Backend (Python 3.11 / Uvicorn)
  ├── DSA Search & Ranking Engine (Trie, Levenshtein, Min-Heap)
  ├── Machine Learning Engine (HistGradientBoostingRegressor)
  └── Database Layer (SQLAlchemy ORM)
           │
           ▼
Production MySQL Database (or SQLite in Development)
```

---

## ⚡ Core Engineering Highlights

1. **DSA Search & Discovery**:
   - **Trie Search (`O(L)`)**: High-speed medicine prefix matching and brand alias resolution (< 0.1ms).
   - **Levenshtein Fuzzy Distance**: Real-time typo tolerance and phonetic fallback matching.
   - **Min-Heap + Haversine Ranking**: Dynamic proximity ranking of in-stock pharmacies nearest to user coordinates.

2. **Machine Learning Pipeline**:
   - **Model**: `sklearn.ensemble.HistGradientBoostingRegressor`
   - **Capabilities**: 7-day rolling demand forecasting, stock-out risk level classification (`HIGH`, `MEDIUM`, `LOW`), and automated replenishment quantity recommendation.
   - **Artifact**: `ml_engine/models/demand_forecast_model.joblib`

3. **Backend REST API (FastAPI)**:
   - Robust JWT Authentication & Role-Based Access Control (`customer`, `pharmacy_admin`, `system_admin`).
   - Clean modular architecture with Pydantic validation schemas.
   - Automated Swagger UI (`/docs`) and OpenAPI specifications (`/openapi.json`).

4. **Android Native Mobile App**:
   - Built with **Kotlin** and **Jetpack Compose** (Material 3).
   - Clean MVVM architecture with StateFlow, Coroutines, and Retrofit 2 networking.
   - Real-time stock queries, pharmacy discovery with map navigation, demand insight viewing, and restock notifications.

---

## 📁 Repository Structure

```
MediTraceX/
├── android/                 # Native Android application (Kotlin, Jetpack Compose)
├── backend/                 # FastAPI REST API backend service
│   └── app/
│       ├── api/             # API routes (auth, medicines, pharmacies, inventory, etc.)
│       ├── core/            # Configuration, database session, and security
│       ├── dsa/             # Trie search and Min-Heap ranker implementations
│       ├── schemas/         # Pydantic request/response schemas
│       └── services/        # Business logic and domain services
├── database/                # Relational models, MySQL schema, and seed logic
│   ├── db_config.py         # Dynamic engine (MySQL in prod / SQLite in dev)
│   ├── models.py            # SQLAlchemy relational models (8 core tables)
│   ├── schema.sql           # Production MySQL DDL script
│   └── init_db.py           # Safe, non-destructive schema migration utility
├── ml_engine/               # ML training and inference pipeline
│   ├── models/              # Trained model artifacts (.joblib and metadata)
│   └── predict.py           # Demand forecasting & stockout risk predictor
├── tests/                   # Automated backend test suite (Pytest)
├── Dockerfile               # Production container definition
├── Procfile                 # Cloud deployment process configuration
├── requirements.txt         # Runtime Python dependencies
├── .env.example             # Environment variable template
└── run_demo.py              # Master verification & demonstration script
```

---

## 🗄️ Database Tables

1. `users` — System users and role-based permissions.
2. `pharmacies` — Pharmacy registry with geospatial GPS coordinates and operating hours.
3. `medicines` — Comprehensive pharmaceutical catalog and pricing.
4. `inventory` — Real-time multi-pharmacy stock tracking and safety thresholds.
5. `sales_history` — Historical transactional records for ML demand forecasting (synthetic/demo dataset).
6. `medicine_requests` — Customer-submitted urgent medicine requests.
7. `watchlist` — Restock notifications and alerts.
8. `notifications` — Logged alerts and customer notifications.

---

## 🚀 Getting Started

### Local Development Setup

1. **Clone the repository and install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

3. **Initialize the database**:
   ```bash
   python database/init_db.py
   ```

4. **Run the backend test suite**:
   ```bash
   pytest -v
   ```

5. **Start the local FastAPI development server**:
   ```bash
   uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   Interactive API docs will be accessible at: `http://127.0.0.1:8000/docs`

---

## 🔒 Security & Deployment Notes

- Real secrets, passwords, and tokens must **never** be committed to version control.
- In production, configure `DATABASE_URL` with your managed MySQL instance and provide a secure `JWT_SECRET_KEY`.
- The dataset included for initial demonstration consists of **synthetic demonstration data**.
