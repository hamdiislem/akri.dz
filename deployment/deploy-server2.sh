#!/bin/bash
# Run this on SERVER 2 (auth-service)
# Set SERVER1_IP and MY_IP before running

set -e

SERVER1_IP="${SERVER1_IP:?Set SERVER1_IP env var}"
MY_IP="${MY_IP:-$(hostname -I | awk '{print $1}')}"
JWT_SECRET="${JWT_SECRET:-change-me-to-random-string}"

echo "=== [Server 2] Deploying auth-service ==="
echo "Infra server : $SERVER1_IP"
echo "My IP        : $MY_IP"

cd deployment/server2-auth

SERVER1_IP=$SERVER1_IP \
MY_IP=$MY_IP \
JWT_SECRET=$JWT_SECRET \
docker compose up -d --build

echo "=== auth-service started on port 8000 ==="
echo "Check Consul UI on server1 to confirm registration"
