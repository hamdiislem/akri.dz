import json
import jwt
import redis
import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from django.conf import settings
from .models import Client, Agency, Admin


def get_redis():
    return redis.from_url(settings.REDIS_URL)


def generate_token(user_id, role):
    payload = {
        'id': user_id,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=settings.JWT_EXPIRY_DAYS),
        'iat': datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')


def decode_token(token):
    return jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])


def get_token_from_request(request):
    token = request.COOKIES.get('token')
    if not token:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]
    return token


# ============================================================
# REGISTER CLIENT — POST /api/auth/register/client/
# ============================================================
@csrf_exempt
def register_client(request):
    if request.method != 'POST':
        return JsonResponse({'erreur': 'Méthode non autorisée'}, status=405)
    try:
        data = json.loads(request.body)
        if Client.objects.filter(email=data.get('email')).exists():
            return JsonResponse({'erreur': 'Email déjà utilisé'}, status=409)
        client = Client.objects.create(
            full_name=data.get('full_name', ''),
            email=data.get('email', ''),
            password=data.get('password', ''),
            phone=data.get('phone', ''),
            wilaya=data.get('wilaya', ''),
        )
        return JsonResponse({'message': 'Client créé avec succès', 'id': client.id}, status=201)
    except Exception as e:
        return JsonResponse({'erreur': str(e)}, status=400)


# ============================================================
# REGISTER AGENCY — POST /api/auth/register/agency/
# ============================================================
@csrf_exempt
def register_agency(request):
    if request.method != 'POST':
        return JsonResponse({'erreur': 'Méthode non autorisée'}, status=405)
    try:
        data = json.loads(request.body)
        if Agency.objects.filter(email=data.get('email')).exists():
            return JsonResponse({'erreur': 'Email déjà utilisé'}, status=409)
        if Agency.objects.filter(rc_number=data.get('rc_number')).exists():
            return JsonResponse({'erreur': 'Numéro RC déjà utilisé'}, status=409)
        agency = Agency.objects.create(
            agency_name=data.get('agency_name', ''),
            owner_name=data.get('owner_name', ''),
            email=data.get('email', ''),
            password=data.get('password', ''),
            phone=data.get('phone', ''),
            wilaya=data.get('wilaya', ''),
            rc_number=data.get('rc_number', ''),
        )
        return JsonResponse({'message': 'Agence créée avec succès', 'id': agency.id}, status=201)
    except Exception as e:
        return JsonResponse({'erreur': str(e)}, status=400)


# ============================================================
# LOGIN — POST /api/auth/login/
# ============================================================
@csrf_exempt
def login(request):
    if request.method != 'POST':
        return JsonResponse({'erreur': 'Méthode non autorisée'}, status=405)
    try:
        data = json.loads(request.body)
        email = data.get('email', '')
        password = data.get('password', '')
        role = data.get('role', 'client')  # 'client', 'agency', or 'admin'

        user = None
        user_id = None

        if role == 'client':
            try:
                user = Client.objects.get(email=email)
                user_id = user.id
                if user.status == 'BANNED':
                    return JsonResponse({'erreur': 'Compte banni'}, status=403)
            except Client.DoesNotExist:
                return JsonResponse({'erreur': 'Identifiants incorrects'}, status=401)

        elif role == 'agency':
            try:
                user = Agency.objects.get(email=email)
                user_id = user.id
                if user.status == 'BANNED':
                    return JsonResponse({'erreur': 'Compte banni'}, status=403)
                if user.status == 'PENDING':
                    return JsonResponse({'erreur': 'Compte en attente de validation'}, status=403)
            except Agency.DoesNotExist:
                return JsonResponse({'erreur': 'Identifiants incorrects'}, status=401)

        elif role == 'admin':
            try:
                user = Admin.objects.get(email=email)
                user_id = user.id
            except Admin.DoesNotExist:
                return JsonResponse({'erreur': 'Identifiants incorrects'}, status=401)

        else:
            return JsonResponse({'erreur': 'Rôle invalide'}, status=400)

        if not check_password(password, user.password):
            return JsonResponse({'erreur': 'Identifiants incorrects'}, status=401)

        token = generate_token(user_id, role)

        response = JsonResponse({'message': 'Connexion réussie', 'role': role, 'id': user_id})
        response.set_cookie(
            'token', token,
            httponly=True,
            samesite='Lax',
            max_age=60 * 60 * 24 * settings.JWT_EXPIRY_DAYS,
        )
        return response

    except Exception as e:
        return JsonResponse({'erreur': str(e)}, status=400)


# ============================================================
# LOGOUT — POST /api/auth/logout/
# ============================================================
@csrf_exempt
def logout(request):
    if request.method != 'POST':
        return JsonResponse({'erreur': 'Méthode non autorisée'}, status=405)
    token = get_token_from_request(request)
    if token:
        try:
            payload = decode_token(token)
            exp = payload.get('exp', 0)
            ttl = exp - int(datetime.datetime.utcnow().timestamp())
            if ttl > 0:
                r = get_redis()
                r.setex(f"blacklist:{token}", ttl, '1')
        except Exception:
            pass
    response = JsonResponse({'message': 'Déconnexion réussie'})
    response.delete_cookie('token')
    return response


# ============================================================
# VERIFY — GET /api/auth/verify/
# Called by api-service middleware to validate a token
# ============================================================
def verify(request):
    token = get_token_from_request(request)
    if not token:
        return JsonResponse({'erreur': 'Token manquant'}, status=401)
    try:
        r = get_redis()
        if r.exists(f"blacklist:{token}"):
            return JsonResponse({'erreur': 'Token invalidé'}, status=401)
        payload = decode_token(token)
        return JsonResponse({
            'id': payload['id'],
            'role': payload['role'],
            'valid': True,
        })
    except jwt.ExpiredSignatureError:
        return JsonResponse({'erreur': 'Token expiré'}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({'erreur': 'Token invalide'}, status=401)


# ============================================================
# ME — GET /api/auth/me/
# ============================================================
def me(request):
    token = get_token_from_request(request)
    if not token:
        return JsonResponse({'erreur': 'Non authentifié'}, status=401)
    try:
        r = get_redis()
        if r.exists(f"blacklist:{token}"):
            return JsonResponse({'erreur': 'Token invalidé'}, status=401)
        payload = decode_token(token)
        user_id = payload['id']
        role = payload['role']

        if role == 'client':
            user = Client.objects.get(id=user_id)
            return JsonResponse({
                'id': user.id, 'role': role,
                'full_name': user.full_name, 'email': user.email,
                'phone': user.phone, 'wilaya': user.wilaya, 'status': user.status,
            })
        elif role == 'agency':
            user = Agency.objects.get(id=user_id)
            return JsonResponse({
                'id': user.id, 'role': role,
                'agency_name': user.agency_name, 'owner_name': user.owner_name,
                'email': user.email, 'phone': user.phone,
                'wilaya': user.wilaya, 'status': user.status,
            })
        elif role == 'admin':
            user = Admin.objects.get(id=user_id)
            return JsonResponse({'id': user.id, 'role': role, 'email': user.email})

    except Exception as e:
        return JsonResponse({'erreur': str(e)}, status=401)
