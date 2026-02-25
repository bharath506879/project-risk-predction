#!/bin/bash
# Database initialization script

set -e

echo "???  Creating PostgreSQL database and tables..."

# Create Docker network
docker network create riskguard-network 2>/dev/null || true

# Start PostgreSQL container
docker run -d \
  --name riskguard-postgres \
  --network riskguard-network \
  -e POSTGRES_USER=riskguard_user \
  -e POSTGRES_PASSWORD=RiskGuard2024! \
  -e POSTGRES_DB=riskguard_db \
  -v riskguard_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15-alpine

echo "?  Waiting for PostgreSQL to be ready..."
sleep 10

# Run migrations
python -m alembic upgrade head

echo "? Database initialized successfully!"
