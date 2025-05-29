#!/bin/bash

echo "Real-Time Data Ingestion System Test"
echo "===================================="

# Test if Docker Compose is available
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose is not available"
    exit 1
fi

echo "✅ Docker Compose is available"

# Validate Docker Compose configuration
echo "📋 Validating Docker Compose configuration..."
if docker compose config --quiet; then
    echo "✅ Docker Compose configuration is valid"
else
    echo "❌ Docker Compose configuration has errors"
    exit 1
fi

# Check if all required files exist
echo "📁 Checking required files..."
required_files=(
    "docker-compose.yml"
    "fastapi/Dockerfile"
    "fastapi/main.py"
    "fastapi/requirements.txt"
    "postgres/postgresql.conf"
    "postgres/init/01-init.sql"
    "sqlserver/init/01-init.sql"
    "sqlserver/init/entrypoint.sh"
    "debezium/postgres-connector.json"
    "debezium/sqlserver-connector.json"
    "setup-debezium.sh"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file is missing"
        exit 1
    fi
done

echo ""
echo "🎉 All tests passed! The system is ready to deploy."
echo ""
echo "To start the system:"
echo "  docker compose up -d"
echo ""
echo "To setup Debezium connector (after services are running):"
echo "  ./setup-debezium.sh"