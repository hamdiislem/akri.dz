import json
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
    except Exception as e:
        print(f"[api_get] ERROR calling {url}: {type(e).__name__}: {e}")
        return None


def api_post(url, data, token=''):
    try:
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        resp = http.post(url, json=data, headers=headers, cookies={'token': token} if token else {}, timeout=TIMEOUT)
        print(f"[api_post] {url} → {resp.status_code} | {resp.text[:300]}")
        return resp
    except Exception as e:
        print(f"[api_post] ERROR calling {url}: {type(e).__name__}: {e}")
        return None


def api_delete(url, token=''):
    try:
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        return http.delete(url, headers=headers, cookies={'token': token} if token else {}, timeout=TIMEOUT)
    except Exception as e:
        print(f"[api_delete] ERROR calling {url}: {type(e).__name__}: {e}")
        return None


def api_put(url, data, token=''):
    try:
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        resp = http.put(url, json=data, headers=headers, cookies={'token': token} if token else {}, timeout=TIMEOUT)
        print(f"[api_put] {url} → {resp.status_code} | {resp.text[:300]}")
        return resp
    except Exception as e:
        print(f"[api_put] ERROR calling {url}: {type(e).__name__}: {e}")
        return None


def api_patch(url, data, token=''):
    try:
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        resp = http.patch(url, json=data, headers=headers, cookies={'token': token} if token else {}, timeout=TIMEOUT)
        return resp
    except Exception as e:
        print(f"[api_patch] ERROR calling {url}: {type(e).__name__}: {e}")
        return None


def parse_list(resp):
    if not resp or resp.status_code != 200:
        return []
    data = resp.json()
    if isinstance(data, list):
        return data
    return data.get('results', [])


def enrich_bookings_with_agency(bookings):
    """Attach agency_name and agency_phone to each booking via auth-service."""
    cache = {}
    for b in bookings:
        agency_id = b.get('agency_id')
        if agency_id and agency_id not in cache:
            resp = api_get(f"{AUTH_URL}/api/auth/agencies/{agency_id}/info/")
            cache[agency_id] = resp.json() if resp and resp.status_code == 200 else {}
        b['agency_info'] = cache.get(agency_id, {})
    return bookings


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
            response.set_cookie('role', role, httponly=False, samesite='Lax', max_age=60*60*24*7)
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
    response.delete_cookie('role')
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

    reviews = parse_list(api_get(f"{API_URL}/api/reviews/?car={car_id}"))
    avg_rating = round(sum(r['rating'] for r in reviews) / len(reviews), 1) if reviews else None

    dates_resp = api_get(f"{API_URL}/api/bookings/disponibilite/?car={car_id}")
    booked_dates = dates_resp.json() if dates_resp and dates_resp.status_code == 200 else []
    booked_dates_json = json.dumps(booked_dates)

    can_review = False
    review_booking_id = None
    if token and request.COOKIES.get('role') == 'client':
        reviewed_booking_ids = {r['booking'] for r in reviews}
        my_bookings = parse_list(api_get(f"{API_URL}/api/bookings/mes-reservations/", token))
        for b in my_bookings:
            if b.get('car') == car_id and b.get('status') == 'COMPLETED' and b['id'] not in reviewed_booking_ids:
                can_review = True
                review_booking_id = b['id']
                break

    return render(request, 'web/car_detail.html', {
        'car': car,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'booked_dates_json': booked_dates_json,
        'can_review': can_review,
        'review_booking_id': review_booking_id,
    })


@csrf_exempt
def submit_review(request, booking_id):
    if request.method != 'POST':
        return redirect('/')
    token = get_token(request)
    if not token:
        return redirect('/login/')
    api_post(f"{API_URL}/api/reviews/", {
        'booking': booking_id,
        'rating': int(request.POST.get('rating', 0)),
        'comment': request.POST.get('comment', ''),
    }, token=token)
    car_id = request.POST.get('car_id')
    return redirect(f'/cars/{car_id}/' if car_id else '/dashboard/client/')


def add_car(request):
    token = get_token(request)
    if not token:
        return redirect('/login/')
    if request.method == 'POST':
        image_url = request.POST.get('image_url', '').strip()
        resp = api_post(f"{API_URL}/api/cars/", {
            'make': request.POST.get('make'),
            'model': request.POST.get('model'),
            'year': int(request.POST.get('year', 2020)),
            'price_per_day': request.POST.get('price_per_day'),
            'transmission': request.POST.get('transmission'),
            'fuel_type': request.POST.get('fuel_type'),
            'wilaya': request.POST.get('wilaya'),
            'seats': int(request.POST.get('seats', 5)),
            'description': request.POST.get('description', ''),
            'images': [image_url] if image_url else [],
            'available': True,
        }, token=token)
        if resp and resp.status_code == 201:
            return redirect('/dashboard/agency/')
        error = 'Service indisponible'
        if resp:
            try:
                error = resp.json().get('erreur', str(resp.json()))
            except Exception:
                pass
        return render(request, 'web/add_car.html', {'error': error, 'form': request.POST})
    return render(request, 'web/add_car.html')


# ─── PROFILES ──────────────────────────────────────────────
def profile_client(request):
    token = get_token(request)
    if not token:
        return redirect('/login/')
    resp = api_get(f"{AUTH_URL}/api/auth/me/", token)
    if not resp or resp.status_code != 200:
        return redirect('/dashboard/client/')
    bookings = enrich_bookings_with_agency(parse_list(api_get(f"{API_URL}/api/bookings/mes-reservations/", token)))
    return render(request, 'web/profile_client.html', {'profile': resp.json(), 'bookings': bookings})


def profile_agency(request):
    token = get_token(request)
    if not token:
        return redirect('/login/')
    resp = api_get(f"{AUTH_URL}/api/auth/me/", token)
    if not resp or resp.status_code != 200:
        return redirect('/dashboard/agency/')
    return render(request, 'web/profile_agency.html', {'profile': resp.json()})


# ─── DASHBOARDS ────────────────────────────────────────────
def dashboard_client(request):
    token = get_token(request)
    if not token:
        return redirect('/login/')
    bookings = enrich_bookings_with_agency(parse_list(api_get(f"{API_URL}/api/bookings/mes-reservations/", token)))
    return render(request, 'web/dashboard_client.html', {'bookings': bookings})


def dashboard_agency(request):
    token = get_token(request)
    if not token:
        return redirect('/login/')
    cars = parse_list(api_get(f"{API_URL}/api/cars/mine/", token))
    bookings = parse_list(api_get(f"{API_URL}/api/bookings/agence/", token))
    pending_count = sum(1 for b in bookings if b.get('status') == 'PENDING')
    revenue = sum(float(b.get('total_price', 0) or 0) for b in bookings if b.get('status') == 'COMPLETED')
    return render(request, 'web/dashboard_agency.html', {
        'cars': cars, 'bookings': bookings,
        'pending_count': pending_count, 'revenue': revenue,
    })


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


# ─── CAR ACTIONS ───────────────────────────────────────────
@csrf_exempt
def supprimer_voiture(request, car_id):
    if request.method == 'POST':
        api_delete(f"{API_URL}/api/cars/{car_id}/", token=get_token(request))
    return redirect('/dashboard/agency/')


def modifier_voiture(request, car_id):
    token = get_token(request)
    if not token:
        return redirect('/login/')
    resp = api_get(f"{API_URL}/api/cars/{car_id}/", token)
    if not resp or resp.status_code != 200:
        return redirect('/dashboard/agency/')
    car = resp.json()
    if request.method == 'POST':
        image_url = request.POST.get('image_url', '').strip()
        if not image_url and car.get('images'):
            image_url = car['images'][0]
        update_resp = api_put(f"{API_URL}/api/cars/{car_id}/", {
            'make': request.POST.get('make'),
            'model': request.POST.get('model'),
            'year': int(request.POST.get('year', car.get('year', 2020))),
            'price_per_day': request.POST.get('price_per_day'),
            'transmission': request.POST.get('transmission'),
            'fuel_type': request.POST.get('fuel_type'),
            'wilaya': request.POST.get('wilaya'),
            'seats': int(request.POST.get('seats', car.get('seats', 5))),
            'description': request.POST.get('description', ''),
            'images': [image_url] if image_url else car.get('images', []),
            'available': car.get('available', True),
        }, token=token)
        if update_resp and update_resp.status_code == 200:
            return redirect('/dashboard/agency/')
        error = 'Service indisponible'
        if update_resp:
            try:
                error = update_resp.json().get('erreur', str(update_resp.json()))
            except Exception:
                pass
        return render(request, 'web/edit_car.html', {'car': car, 'error': error})
    return render(request, 'web/edit_car.html', {'car': car})


@csrf_exempt
def toggle_disponibilite(request, car_id):
    if request.method == 'POST':
        token = get_token(request)
        resp = api_get(f"{API_URL}/api/cars/{car_id}/", token)
        if resp and resp.status_code == 200:
            car = resp.json()
            api_put(f"{API_URL}/api/cars/{car_id}/", {
                'make': car.get('make'),
                'model': car.get('model'),
                'year': car.get('year'),
                'price_per_day': car.get('price_per_day'),
                'transmission': car.get('transmission'),
                'fuel_type': car.get('fuel_type'),
                'wilaya': car.get('wilaya'),
                'seats': car.get('seats'),
                'description': car.get('description', ''),
                'images': car.get('images', []),
                'available': not car.get('available', True),
            }, token=token)
    return redirect('/dashboard/agency/')


# ─── BOOKING COMPLETE ──────────────────────────────────────
@csrf_exempt
def completer_booking(request, booking_id):
    if request.method == 'POST':
        api_post(f"{API_URL}/api/bookings/{booking_id}/completer/", {}, token=get_token(request))
    return redirect('/dashboard/agency/')


# ─── ADMIN UNBAN ACTIONS ───────────────────────────────────
@csrf_exempt
def admin_debannir_agence(request, agency_id):
    if request.method == 'POST':
        api_post(f"{AUTH_URL}/api/auth/admin/agencies/{agency_id}/unban/", {}, token=get_token(request))
    return redirect('/dashboard/admin/')


@csrf_exempt
def admin_debannir_client(request, client_id):
    if request.method == 'POST':
        api_post(f"{AUTH_URL}/api/auth/admin/clients/{client_id}/unban/", {}, token=get_token(request))
    return redirect('/dashboard/admin/')


# ─── ADMIN PROFILE ─────────────────────────────────────────
def edit_profile_client(request):
    token = get_token(request)
    if not token:
        return redirect('/login/')
    resp = api_get(f"{AUTH_URL}/api/auth/me/", token)
    if not resp or resp.status_code != 200:
        return redirect('/profile/client/')
    profile = resp.json()
    if request.method == 'POST':
        patch_resp = api_patch(f"{AUTH_URL}/api/auth/me/update/", {
            'full_name': request.POST.get('full_name'),
            'phone': request.POST.get('phone'),
            'wilaya': request.POST.get('wilaya'),
            'driver_license': request.POST.get('driver_license'),
            'age': request.POST.get('age') or None,
            'gender': request.POST.get('gender'),
            'marital_status': request.POST.get('marital_status'),
            'family_size': request.POST.get('family_size') or None,
        }, token=token)
        if patch_resp and patch_resp.status_code == 200:
            return redirect('/profile/client/')
        error = 'Erreur lors de la mise à jour'
        if patch_resp:
            try:
                error = patch_resp.json().get('erreur', error)
            except Exception:
                pass
        return render(request, 'web/edit_profile_client.html', {'profile': profile, 'error': error})
    return render(request, 'web/edit_profile_client.html', {'profile': profile})


def edit_profile_agency(request):
    token = get_token(request)
    if not token:
        return redirect('/login/')
    resp = api_get(f"{AUTH_URL}/api/auth/me/", token)
    if not resp or resp.status_code != 200:
        return redirect('/profile/agency/')
    profile = resp.json()
    if request.method == 'POST':
        patch_resp = api_patch(f"{AUTH_URL}/api/auth/me/update/", {
            'owner_name': request.POST.get('owner_name'),
            'phone': request.POST.get('phone'),
            'wilaya': request.POST.get('wilaya'),
            'address': request.POST.get('address'),
            'description': request.POST.get('description'),
        }, token=token)
        if patch_resp and patch_resp.status_code == 200:
            return redirect('/profile/agency/')
        error = 'Erreur lors de la mise à jour'
        if patch_resp:
            try:
                error = patch_resp.json().get('erreur', error)
            except Exception:
                pass
        return render(request, 'web/edit_profile_agency.html', {'profile': profile, 'error': error})
    return render(request, 'web/edit_profile_agency.html', {'profile': profile})


@csrf_exempt
def delete_account(request):
    if request.method != 'POST':
        return redirect('/')
    token = get_token(request)
    if not token:
        return redirect('/login/')
    api_delete(f"{AUTH_URL}/api/auth/me/delete/", token=token)
    response = redirect('/')
    response.delete_cookie('token')
    response.delete_cookie('role')
    return response


def profile_admin(request):
    token = get_token(request)
    if not token:
        return redirect('/login/')
    resp = api_get(f"{AUTH_URL}/api/auth/me/", token)
    if not resp or resp.status_code != 200:
        return redirect('/dashboard/admin/')
    return render(request, 'web/profile_admin.html', {'profile': resp.json()})
