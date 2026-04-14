import requests as http
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

AUTH_URL = settings.AUTH_SERVICE_URL
API_URL = settings.API_SERVICE_URL

TIMEOUT = 60


def get_token(request):
    return request.COOKIES.get('token', '')


def api_get(url, token='', params=None):
    try:
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        return http.get(url, headers=headers, cookies={'token': token} if token else {}, params=params, timeout=TIMEOUT)
    except Exception:
        return None


def api_post(url, data, token=''):
    try:
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        return http.post(url, json=data, headers=headers, cookies={'token': token} if token else {}, timeout=TIMEOUT)
    except Exception:
        return None


def parse_list(resp):
    """Handle both list and paginated DRF responses."""
    if not resp or resp.status_code != 200:
        return []
    data = resp.json()
    if isinstance(data, list):
        return data
    return data.get('results', [])


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
            # Extract token from cookie set by auth-service
            token = resp.cookies.get('token', '')
            if token:
                response.set_cookie('token', token, httponly=True, samesite='Lax', max_age=60*60*24*7)
            return response
        error = 'Service indisponible'
        if resp:
            try:
                error = resp.json().get('erreur', 'Erreur de connexion')
            except Exception:
                pass
        return render(request, 'web/login.html', {'error': error})
    return render(request, 'web/login.html')


def logout_view(request):
    api_post(f"{AUTH_URL}/api/auth/logout/", {}, token=get_token(request))
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
        error = 'Service indisponible'
        if resp:
            try:
                error = resp.json().get('erreur', 'Erreur')
            except Exception:
                pass
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
        error = 'Service indisponible'
        if resp:
            try:
                error = resp.json().get('erreur', 'Erreur')
            except Exception:
                pass
        return render(request, 'web/register_agency.html', {'error': error})
    return render(request, 'web/register_agency.html')


# ─── CARS ──────────────────────────────────────────────────
def cars_list(request):
    params = {k: v for k, v in request.GET.items() if v}
    resp = api_get(f"{API_URL}/api/cars/", params=params)
    cars = parse_list(resp)
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
        error = 'Service indisponible'
        if book_resp:
            try:
                error = book_resp.json().get('erreur', 'Erreur')
            except Exception:
                pass
        return render(request, 'web/car_detail.html', {'car': car, 'error': error})

    return render(request, 'web/car_detail.html', {'car': car})


# ─── DASHBOARDS ────────────────────────────────────────────
def dashboard_client(request):
    token = get_token(request)
    if not token:
        return redirect('/login/')
    bookings = parse_list(api_get(f"{API_URL}/api/bookings/mes-reservations/", token))
    return render(request, 'web/dashboard_client.html', {'bookings': bookings})


def dashboard_agency(request):
    token = get_token(request)
    if not token:
        return redirect('/login/')
    cars = parse_list(api_get(f"{API_URL}/api/cars/mine/", token))
    bookings = parse_list(api_get(f"{API_URL}/api/bookings/agence/", token))
    return render(request, 'web/dashboard_agency.html', {'cars': cars, 'bookings': bookings})


def dashboard_admin(request):
    token = get_token(request)
    if not token:
        return redirect('/login/')
    stats_resp = api_get(f"{API_URL}/api/admin/stats/", token)
    bookings_resp = api_get(f"{API_URL}/api/admin/bookings/", token)
    agencies_resp = api_get(f"{AUTH_URL}/api/auth/admin/agencies/", token)
    clients_resp = api_get(f"{AUTH_URL}/api/auth/admin/clients/", token)
    stats = stats_resp.json() if stats_resp and stats_resp.status_code == 200 else {}
    bookings = bookings_resp.json() if bookings_resp and bookings_resp.status_code == 200 else []
    if isinstance(bookings, dict):
        bookings = bookings.get('results', [])
    agencies = agencies_resp.json() if agencies_resp and agencies_resp.status_code == 200 else []
    clients = clients_resp.json() if clients_resp and clients_resp.status_code == 200 else []
    return render(request, 'web/dashboard_admin.html', {
        'stats': stats, 'bookings': bookings,
        'agencies': agencies, 'clients': clients,
    })


# ─── ADMIN ACTIONS ─────────────────────────────────────────
@csrf_exempt
def admin_verifier_agence(request, agency_id):
    if request.method == 'POST':
        api_post(f"{AUTH_URL}/api/auth/admin/agencies/{agency_id}/verify/", {}, token=get_token(request))
    return redirect('/dashboard/admin/')


@csrf_exempt
def admin_bannir_agence(request, agency_id):
    if request.method == 'POST':
        api_post(f"{AUTH_URL}/api/auth/admin/agencies/{agency_id}/ban/", {}, token=get_token(request))
    return redirect('/dashboard/admin/')


@csrf_exempt
def admin_bannir_client(request, client_id):
    if request.method == 'POST':
        api_post(f"{AUTH_URL}/api/auth/admin/clients/{client_id}/ban/", {}, token=get_token(request))
    return redirect('/dashboard/admin/')


# ─── BOOKING ACTIONS ───────────────────────────────────────
@csrf_exempt
def confirmer_booking(request, booking_id):
    if request.method == 'POST':
        api_post(f"{API_URL}/api/bookings/{booking_id}/confirmer/", {}, token=get_token(request))
    return redirect('/dashboard/agency/')


@csrf_exempt
def annuler_booking(request, booking_id):
    if request.method == 'POST':
        api_post(f"{API_URL}/api/bookings/{booking_id}/annuler/", {}, token=get_token(request))
    return redirect(request.POST.get('next', '/'))
