# Play with Docker — Setup Guide
# Run these commands on each node AFTER you give me the 5 IPs
# (I will fill in the IPs automatically once you send them)

## Prerequisites on EVERY node (run this first on each node):
```bash
apk add git
git clone https://github.com/YOUR_USERNAME/akri.dz.git
cd akri.dz
```

---

## Node 1 — Infrastructure (Traefik + Consul + RabbitMQ + PostgreSQL + Redis)
```bash
cd deployment/server1-infra
docker compose up -d
```
Wait 30 seconds, then check:
- Consul UI: http://NODE1_IP:8500
- RabbitMQ UI: http://NODE1_IP:15672  (guest / guest)
- Traefik dashboard: http://NODE1_IP:8080

---

## Node 2 — auth-service
```bash
export SERVER1_IP=NODE1_IP
export MY_IP=NODE2_IP
export JWT_SECRET=akri-secret-2025
cd deployment/server2-auth
docker compose up -d --build
```

---

## Node 3 — api-service
```bash
export SERVER1_IP=NODE1_IP
export SERVER2_IP=NODE2_IP
export MY_IP=NODE3_IP
cd deployment/server3-api
docker compose up -d --build
```

---

## Node 4 — frontend-service
```bash
export SERVER2_IP=NODE2_IP
export SERVER3_IP=NODE3_IP
cd deployment/server4-frontend
docker compose up -d --build
```

---

## Node 5 — notification-worker
```bash
export SERVER1_IP=NODE1_IP
export MY_IP=NODE5_IP
cd deployment/server5-worker
docker compose up -d --build
```

---

## Test the full flow
1. Open browser → http://NODE1_IP  (Traefik routes to frontend)
2. Register as client → login → browse cars
3. Register as agency → login → add a car
4. Confirm a booking → check Node 5 logs: `docker compose logs -f`
   You should see the RabbitMQ notification printed
5. Open Consul UI (Node1:8500) → Services → you should see all 4 services registered
