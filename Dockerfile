# =====================================================================
# MediTraceX Production Docker Container
# =====================================================================

FROM python:3.11-slim

# Set environment optimizations
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

WORKDIR /app

# Install system dependencies (build-essential / curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source directories and trained ML model artifacts
COPY backend/ /app/backend/
COPY database/ /app/database/
COPY ml_engine/ /app/ml_engine/

# Create non-root system user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose dynamic cloud port
EXPOSE 8000

# Health check probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Launch startup: initialize database schema & start Uvicorn
CMD ["sh", "-c", "python database/init_db.py && uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
