#!/bin/bash
# Run this on SERVER 5 (notification-worker)
# Set SERVER1_IP before running

set -e

SERVER1_IP="${SERVER1_IP:?Set SERVER1_IP env var}"
MY_IP="${MY_IP:-$(hostname -I | awk '{print $1}')}"

echo "=== [Server 5] Deploying notification-worker ==="

cd deployment/server5-worker

SERVER1_IP=$SERVER1_IP \
MY_IP=$MY_IP \
docker compose up -d --build

echo "=== notification-worker started ==="
echo "Check logs: docker compose logs -f notification-worker"
