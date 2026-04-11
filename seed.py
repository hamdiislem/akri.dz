"""
Akri.dz — Seed Script
Creates test data by calling the live APIs.
Usage: python seed.py
"""

import requests

# ── CONFIGURE YOUR RENDER URLS HERE ─────────────────────────────
AUTH_URL = "https://akri-auth.onrender.com"
API_URL  = "https://akri-api.onrender.com"
# ────────────────────────────────────────────────────────────────

s = requests.Session()

def ok(label, r):
    if r.status_code in (200, 201):
        print(f"  ✓ {label}")
        return r.json()
    else:
        print(f"  ✗ {label} [{r.status_code}] {r.text[:120]}")
        return None

# ============================================================
# 1. CREATE AGENCIES
# ============================================================
print("\n── Agences ──────────────────────────────────")

agencies = [
    {"agency_name": "Auto Elite Alger",   "owner_name": "Karim Mansouri",  "email": "elite@akri.dz",    "password": "Pass1234!", "phone": "0550100001", "wilaya": "Alger",    "rc_number": "RC-ALG-001"},
    {"agency_name": "Sahara Drive Oran",  "owner_name": "Fatima Benali",   "email": "sahara@akri.dz",   "password": "Pass1234!", "phone": "0550100002", "wilaya": "Oran",     "rc_number": "RC-ORA-002"},
    {"agency_name": "Atlas Cars Tizi",    "owner_name": "Yacine Aït",      "email": "atlas@akri.dz",    "password": "Pass1234!", "phone": "0550100003", "wilaya": "Tizi Ouzou","rc_number": "RC-TIZ-003"},
]

agency_ids = []
agency_tokens = []
for a in agencies:
    r = ok(f"Register {a['agency_name']}", requests.post(f"{AUTH_URL}/api/auth/register/agency/", json=a))
    if r:
        agency_ids.append(r['id'])

# Login agencies to get tokens
for a in agencies:
    s2 = requests.Session()
    r = s2.post(f"{AUTH_URL}/api/auth/login/", json={"email": a['email'], "password": a['password'], "role": "agency"})
    ok(f"Login {a['agency_name']}", r)
    agency_tokens.append(s2)

# ============================================================
# 2. CREATE CLIENTS
# ============================================================
print("\n── Clients ──────────────────────────────────")

clients = [
    {"full_name": "Ahmed Bouzid",    "email": "ahmed@akri.dz",   "password": "Pass1234!", "phone": "0660200001", "wilaya": "Alger"},
    {"full_name": "Sara Meziani",    "email": "sara@akri.dz",    "password": "Pass1234!", "phone": "0660200002", "wilaya": "Oran"},
    {"full_name": "Mourad Khelifi",  "email": "mourad@akri.dz",  "password": "Pass1234!", "phone": "0660200003", "wilaya": "Constantine"},
    {"full_name": "Nadia Hamidi",    "email": "nadia@akri.dz",   "password": "Pass1234!", "phone": "0660200004", "wilaya": "Annaba"},
    {"full_name": "Bilal Saadi",     "email": "bilal@akri.dz",   "password": "Pass1234!", "phone": "0660200005", "wilaya": "Blida"},
]

for c in clients:
    ok(f"Register {c['full_name']}", requests.post(f"{AUTH_URL}/api/auth/register/client/", json=c))

# ============================================================
# 3. CREATE CARS (as each agency)
# ============================================================
print("\n── Voitures ─────────────────────────────────")

cars_by_agency = [
    # Agency 0 — Auto Elite Alger
    [
        {"make": "Toyota", "model": "Corolla", "year": 2022, "fuel_type": "PETROL",   "transmission": "AUTOMATIC", "seats": 5, "price_per_day": 4500, "wilaya": "Alger",      "available": True,  "description": "Voiture économique, idéale pour la ville."},
        {"make": "Hyundai","model": "Tucson",  "year": 2023, "fuel_type": "DIESEL",   "transmission": "AUTOMATIC", "seats": 5, "price_per_day": 6500, "wilaya": "Alger",      "available": True,  "description": "SUV confortable pour les longs trajets."},
        {"make": "Renault","model": "Symbol",  "year": 2021, "fuel_type": "PETROL",   "transmission": "MANUAL",    "seats": 5, "price_per_day": 3500, "wilaya": "Alger",      "available": True,  "description": "Compacte et facile à conduire."},
    ],
    # Agency 1 — Sahara Drive Oran
    [
        {"make": "Dacia",  "model": "Duster",  "year": 2022, "fuel_type": "DIESEL",   "transmission": "MANUAL",    "seats": 5, "price_per_day": 5000, "wilaya": "Oran",       "available": True,  "description": "Parfait pour les pistes du désert."},
        {"make": "Kia",    "model": "Sportage","year": 2023, "fuel_type": "PETROL",   "transmission": "AUTOMATIC", "seats": 5, "price_per_day": 7000, "wilaya": "Oran",       "available": True,  "description": "SUV premium avec toutes les options."},
        {"make": "Peugeot","model": "208",     "year": 2021, "fuel_type": "PETROL",   "transmission": "MANUAL",    "seats": 5, "price_per_day": 3800, "wilaya": "Oran",       "available": False, "description": "Citadine sportive."},
    ],
    # Agency 2 — Atlas Cars Tizi
    [
        {"make": "Toyota", "model": "RAV4",    "year": 2023, "fuel_type": "HYBRID",   "transmission": "AUTOMATIC", "seats": 5, "price_per_day": 8000, "wilaya": "Tizi Ouzou", "available": True,  "description": "SUV hybride économique."},
        {"make": "Suzuki", "model": "Vitara",  "year": 2022, "fuel_type": "PETROL",   "transmission": "MANUAL",    "seats": 5, "price_per_day": 5500, "wilaya": "Tizi Ouzou", "available": True,  "description": "Compact idéal pour la montagne."},
    ],
]

for i, (agency_session, cars) in enumerate(zip(agency_tokens, cars_by_agency)):
    for car in cars:
        ok(f"Car {car['brand']} {car['model']} (agence {i+1})",
           agency_session.post(f"{API_URL}/api/cars/", json=car))

# ============================================================
# 4. SUMMARY
# ============================================================
print("\n── Résumé ───────────────────────────────────")
print(f"  Agences créées : {len(agencies)}")
print(f"  Clients créés  : {len(clients)}")
print(f"  Voitures créées: {sum(len(c) for c in cars_by_agency)}")

print("\n── Comptes de test ──────────────────────────")
print("  ADMIN    : admin@akri.dz / Admin123456")
print("  AGENCE 1 : elite@akri.dz / Pass1234!")
print("  AGENCE 2 : sahara@akri.dz / Pass1234!")
print("  AGENCE 3 : atlas@akri.dz / Pass1234!")
print("  CLIENT 1 : ahmed@akri.dz / Pass1234!")
print("  CLIENT 2 : sara@akri.dz / Pass1234!")
print()
