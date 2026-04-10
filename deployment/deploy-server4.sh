#!/bin/bash
# Run this on SERVER 4 (frontend-service)
# Set SERVER2_IP and SERVER3_IP before running

set -e

SERVER2_IP="${SERVER2_IP:?Set SERVER2_IP env var}"
SERVER3_IP="${SERVER3_IP:?Set SERVER3_IP env var}"

echo "=== [Server 4] Deploying frontend-service ==="

cd deployment/server4-frontend

SERVER2_IP=$SERVER2_IP \
SERVER3_IP=$SERVER3_IP \
docker compose up -d --build

echo "=== frontend-service started on port 8000 ==="
