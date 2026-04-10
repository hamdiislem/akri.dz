#!/bin/bash
# Run this on SERVER 1 (Infra: Traefik, Consul, RabbitMQ, PostgreSQL, Redis)
# Before running: edit traefik/dynamic.yml and replace SERVER2/3/4_IP with real IPs

set -e

echo "=== [Server 1] Deploying infrastructure ==="

# Clone or copy the project
# git clone <your-repo-url> akri.dz
# cd akri.dz

cd deployment/server1-infra

# Edit dynamic.yml with real IPs first!
echo "!! Make sure you've updated traefik/dynamic.yml with real server IPs !!"
sleep 3

docker compose up -d

echo "=== Infrastructure started ==="
echo "Traefik dashboard : http://$(hostname -I | awk '{print $1}'):8080"
echo "Consul UI         : http://$(hostname -I | awk '{print $1}'):8500"
echo "RabbitMQ UI       : http://$(hostname -I | awk '{print $1}'):15672  (guest/guest)"
