#!/bin/bash
# Run this on SERVER 3 (api-service)
# Set SERVER1_IP, SERVER2_IP and MY_IP before running

set -e

SERVER1_IP="${SERVER1_IP:?Set SERVER1_IP env var}"
SERVER2_IP="${SERVER2_IP:?Set SERVER2_IP env var}"
MY_IP="${MY_IP:-$(hostname -I | awk '{print $1}')}"

echo "=== [Server 3] Deploying api-service ==="

cd deployment/server3-api

SERVER1_IP=$SERVER1_IP \
SERVER2_IP=$SERVER2_IP \
MY_IP=$MY_IP \
docker compose up -d --build

echo "=== api-service started on port 8000 ==="
