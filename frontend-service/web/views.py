import requests as http
from django.shortcuts import render, redirect
from django.conf import settings

AUTH_URL = settings.AUTH_SERVICE_URL
API_URL = settings.API_SERVICE_URL


def get_token(request):
    return request.COOKIES.get('token', '')


def api_get(url, token='', params=None):
    try:
        return http.get(url, cookies={'token': token}, params=params, timeout=30)
    except Exception:
        return None


def api_post(url, data, token=''):
    try:
        return http.post(url, json=data, cookies={'token': token}, timeout=30)
    except Exception:
        return None


# ─── HOME ──────────────────────────────────────────────────
def home(request):
    return render(request, 'web/home.html')


# ─── AUTH ──────────────────────────────────────────────────
def login_view(request):
    if request.method == 'POST':
        resp = api_post(f"{AUTH_URL}/api/auth/login/", {
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
            'role': request.POST.get('role', 'client'),
        })
        if resp and resp.status_code == 200:
            data = resp.json()
            role = data.get('role', 'client')
            response = redirect(f"/dashboard/{role}/")
            token = resp.cookies.get('token', '')
            if token:
                response.set_cookie('token', token, httponly=True, samesite='Lax', max_age=60*60*24*7)
            return response
        error = resp.json().get('erreur', 'Erreur de connexion') if resp else 'Service indisponible'
        return render(request, 'web/login.html', {'error': error})
    return render(request, 'web/login.html')


def logout_view(request):
    resp = api_post(f"{AUTH_URL}/api/auth/logout/", {}, token=get_token(request))
    response = redirect('/')
    response.delete_cookie('token')
    return response


def register_client(request):
    if request.method == 'POST':
        resp = api_post(f"{AUTH_URL}/api/auth/register/client/", {
            'full_name': request.POST.get('full_name'),
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
            'phone': request.POST.get('phone'),
            'wilaya': request.POST.get('wilaya'),
        })
        if resp and resp.status_code == 201:
            return redirect('/login/')
        error = resp.json().get('erreur', 'Erreur') if resp else 'Service indisponible'
        return render(request, 'web/register_client.html', {'error': error})
    return render(request, 'web/register_client.html')


def register_agency(request):
    if request.method == 'POST':
        resp = api_post(f"{AUTH_URL}/api/auth/register/agency/", {
            'agency_name': request.POST.get('agency_name'),
            'owner_name': request.POST.get('owner_name'),
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
            'phone': request.POST.get('phone'),
            'wilaya': request.POST.get('wilaya'),
            'rc_number': request.POST.get('rc_number'),
        })
        if resp and resp.status_code == 201:
            return redirect('/login/')
        error = resp.json().get('erreur', 'Erreur') if resp else 'Service indisponible'
        return render(request, 'web/register_agency.html', {'error': error})
    return render(request, 'web/register_agency.html')


# ─── CARS ──────────────────────────────────────────────────
def cars_list(request):
    params = {k: v for k, v in request.GET.items() if v}
    resp = api_get(f"{API_URL}/api/cars/", params=params)
    cars = resp.json().get('results', resp.json()) if resp and resp.status_code == 200 else []
    return render(request, 'web/cars.html', {'cars': cars, 'filters': request.GET})


def car_detail(request, car_id):
    token = get_token(request)
    resp = api_get(f"{API_URL}/api/cars/{car_id}/", token)
    if not resp or resp.status_code != 200:
        return redirect('/cars/')
    car = resp.json()

    if request.method == 'POST' and token:
        book_resp = api_post(f"{API_URL}/api/bookings/", {
            'car': car_id,
            'start_date': request.POST.get('start_date'),
            'end_date': request.POST.get('end_date'),
            'message': request.POST.get('message', ''),
        }, token=token)
        if book_resp and book_resp.status_code == 201:
            return redirect('/dashboard/client/')
        error = book_resp.json().get('erreur', 'Erreur') if book_resp else 'Service indisponible'
        return render(request, 'web/car_detail.html', {'car': car, 'error': error})

    return render(request, 'web/car_detail.html', {'car': car})


# ─── DASHBOARDS ────────────────────────────────────────────
def dashboard_client(request):
    token = get_token(request)
    if not token:
        return redirect('/login/')
    resp = api_get(f"{API_URL}/api/bookings/mes-reservations/", token)
    bookings = resp.json() if resp and resp.status_code == 200 else []
    return render(request, 'web/dashboard_client.html', {'bookings': bookings})


def dashboard_agency(request):
    token = get_token(request)
    if not token:
        return redirect('/login/')
    cars_resp = api_get(f"{API_URL}/api/cars/mine/", token)
    bookings_resp = api_get(f"{API_URL}/api/bookings/agence/", token)
    cars = cars_resp.json() if cars_resp and cars_resp.status_code == 200 else []
    bookings = bookings_resp.json() if bookings_resp and bookings_resp.status_code == 200 else []
    return render(request, 'web/dashboard_agency.html', {'cars': cars, 'bookings': bookings})


def dashboard_admin(request):
    token = get_token(request)
    if not token:
        return redirect('/login/')
    stats_resp = api_get(f"{API_URL}/api/admin/stats/", token)
    bookings_resp = api_get(f"{API_URL}/api/admin/bookings/", token)
    stats = stats_resp.json() if stats_resp and stats_resp.status_code == 200 else {}
    bookings = bookings_resp.json() if bookings_resp and bookings_resp.status_code == 200 else []
    return render(request, 'web/dashboard_admin.html', {'stats': stats, 'bookings': bookings})


def confirmer_booking(request, booking_id):
    if request.method == 'POST':
        api_post(f"{API_URL}/api/bookings/{booking_id}/confirmer/", {}, token=get_token(request))
    return redirect('/dashboard/agency/')


def annuler_booking(request, booking_id):
    if request.method == 'POST':
        api_post(f"{API_URL}/api/bookings/{booking_id}/annuler/", {}, token=get_token(request))
    return redirect(request.POST.get('next', '/'))
