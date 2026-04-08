#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

# Seed demo data if enabled and the DB is empty
python -c "
from app.config import settings
if not settings.seed_demo_data:
    print('SEED_DEMO_DATA is disabled — skipping seed.')
    exit(0)
from app.database import SessionLocal
from app.models.case import Case
db = SessionLocal()
if db.query(Case).count() == 0:
    print('No cases found — seeding demo refinery...')
    from app.seed.demo_refinery import seed
    seed(db)
else:
    print('Cases already exist — skipping seed.')
db.close()
"

# In development, enable hot reload
if [ "$ENVIRONMENT" = "development" ]; then
    echo "Starting backend (development, --reload)..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    echo "Starting backend (production)..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
