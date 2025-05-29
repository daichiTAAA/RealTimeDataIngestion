#!/bin/bash

echo "Waiting for Debezium Connect to be ready..."
while [ $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8083/connectors) -ne 200 ]; do
    echo "Debezium Connect not ready yet, waiting..."
    sleep 10
done

echo "Debezium Connect is ready. Creating PostgreSQL connector..."

# Create the PostgreSQL connector
curl -X POST \
  -H "Content-Type: application/json" \
  -d @debezium/postgres-connector.json \
  http://localhost:8083/connectors

echo "PostgreSQL connector created successfully!"

# Check connector status
echo "Checking connector status..."
curl -X GET http://localhost:8083/connectors/postgres-connector/status | jq .