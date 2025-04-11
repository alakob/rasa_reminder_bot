#!/bin/bash

echo "Building ARM64-specific containers for M1/M2 Macs..."

# Stop any running containers
docker-compose down

# Build and start using the ARM64-specific compose file
docker-compose -f docker-compose.arm64.yml build --no-cache
docker-compose -f docker-compose.arm64.yml up -d postgres
sleep 5  # Give PostgreSQL time to initialize
docker-compose -f docker-compose.arm64.yml up -d action-server
docker-compose -f docker-compose.arm64.yml up rasa

echo "Containers started successfully!" 