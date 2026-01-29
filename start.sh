#!/bin/bash
# Startup script for production deployment
# Runs database migrations before starting the API server

set -e  # Exit on error

echo "Starting Gardening Helper Service..."

# Wait for database to be ready
echo "Waiting for database connection..."
until python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')" 2>/dev/null; do
  echo "Database not ready, waiting..."
  sleep 2
done
echo "Database connection established."

# Run Alembic migrations
echo "Running database migrations..."
alembic upgrade head
echo "Migrations complete."

# Load seed data if needed (only in development)
if [ "$APP_ENV" = "development" ]; then
  echo "Loading seed data..."
  python -m seed_data.plant_varieties || echo "Seed data already loaded or failed."
fi

# Start the API server
echo "Starting API server on port ${PORT:-8080}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8080}"
