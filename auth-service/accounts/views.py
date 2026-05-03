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


@csrf_exempt
def register_client(request):
    if request.method != 'POST':
        return JsonResponse({'erreur': 'Méthode non autorisée'}, status=405)
    try:
        data = json.loads(request.body)
        if Client.objects.filter(email=data.get('email')).exists():
            return JsonResponse({'erreur': 'Email déjà utilisé'}, status=409)
        age_raw = data.get('age')
        family_size_raw = data.get('family_size')
        client = Client.objects.create(
            full_name=data.get('full_name', ''),
            email=data.get('email', ''),
            password=data.get('password', ''),
            phone=data.get('phone', ''),
            wilaya=data.get('wilaya', ''),
            driver_license=data.get('driver_license', ''),
            age=int(age_raw) if age_raw else None,
            gender=data.get('gender', ''),
            marital_status=data.get('marital_status', ''),
            family_size=int(family_size_raw) if family_size_raw else None,
        )
        return JsonResponse({'message': 'Client créé avec succès', 'id': client.id}, status=201)
    except Exception as e:
        return JsonResponse({'erreur': str(e)}, status=400)


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
            address=data.get('address', ''),
            description=data.get('description', ''),
            rc_number=data.get('rc_number', ''),
        )
        return JsonResponse({'message': 'Agence créée avec succès', 'id': agency.id}, status=201)
    except Exception as e:
        return JsonResponse({'erreur': str(e)}, status=400)


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


def require_admin_token(request):
    token = get_token_from_request(request)
    if not token:
        return None, JsonResponse({'erreur': 'Non authentifié'}, status=401)
    try:
        payload = decode_token(token)
        if payload.get('role') != 'admin':
            return None, JsonResponse({'erreur': 'Accès refusé'}, status=403)
        return payload, None
    except Exception:
        return None, JsonResponse({'erreur': 'Token invalide'}, status=401)


def admin_list_agencies(request):
    _, err = require_admin_token(request)
    if err:
        return err
    agencies = list(Agency.objects.order_by('-created_at').values(
        'id', 'agency_name', 'owner_name', 'email', 'phone', 'wilaya', 'rc_number', 'status', 'created_at'
    ))
    return JsonResponse(agencies, safe=False)


@csrf_exempt
def admin_verify_agency(request, agency_id):
    _, err = require_admin_token(request)
    if err:
        return err
    try:
        agency = Agency.objects.get(id=agency_id)
        agency.status = 'VERIFIED'
        agency.save(update_fields=['status'])
        return JsonResponse({'message': 'Agence vérifiée'})
    except Agency.DoesNotExist:
        return JsonResponse({'erreur': 'Agence introuvable'}, status=404)


@csrf_exempt
def admin_ban_agency(request, agency_id):
    _, err = require_admin_token(request)
    if err:
        return err
    try:
        agency = Agency.objects.get(id=agency_id)
        agency.status = 'BANNED'
        agency.save(update_fields=['status'])
        return JsonResponse({'message': 'Agence bannie'})
    except Agency.DoesNotExist:
        return JsonResponse({'erreur': 'Agence introuvable'}, status=404)


@csrf_exempt
def admin_unban_agency(request, agency_id):
    _, err = require_admin_token(request)
    if err:
        return err
    try:
        agency = Agency.objects.get(id=agency_id)
        agency.status = 'VERIFIED'
        agency.save(update_fields=['status'])
        return JsonResponse({'message': 'Agence réactivée'})
    except Agency.DoesNotExist:
        return JsonResponse({'erreur': 'Agence introuvable'}, status=404)


def admin_list_clients(request):
    _, err = require_admin_token(request)
    if err:
        return err
    clients = list(Client.objects.order_by('-created_at').values(
        'id', 'full_name', 'email', 'phone', 'wilaya', 'status', 'created_at'
    ))
    return JsonResponse(clients, safe=False)


@csrf_exempt
def admin_ban_client(request, client_id):
    _, err = require_admin_token(request)
    if err:
        return err
    try:
        client = Client.objects.get(id=client_id)
        client.status = 'BANNED'
        client.save(update_fields=['status'])
        return JsonResponse({'message': 'Client banni'})
    except Client.DoesNotExist:
        return JsonResponse({'erreur': 'Client introuvable'}, status=404)


@csrf_exempt
def admin_unban_client(request, client_id):
    _, err = require_admin_token(request)
    if err:
        return err
    try:
        client = Client.objects.get(id=client_id)
        client.status = 'VERIFIED'
        client.save(update_fields=['status'])
        return JsonResponse({'message': 'Client réactivé'})
    except Client.DoesNotExist:
        return JsonResponse({'erreur': 'Client introuvable'}, status=404)


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
                'phone': user.phone, 'wilaya': user.wilaya,
                'driver_license': user.driver_license,
                'age': user.age,
                'gender': user.gender,
                'marital_status': user.marital_status,
                'family_size': user.family_size,
                'status': user.status,
                'member_since': user.created_at.strftime('%d/%m/%Y'),
            })
        elif role == 'agency':
            user = Agency.objects.get(id=user_id)
            return JsonResponse({
                'id': user.id, 'role': role,
                'agency_name': user.agency_name, 'owner_name': user.owner_name,
                'email': user.email, 'phone': user.phone,
                'wilaya': user.wilaya, 'address': user.address,
                'description': user.description, 'rc_number': user.rc_number,
                'status': user.status,
                'member_since': user.created_at.strftime('%d/%m/%Y'),
            })
        elif role == 'admin':
            user = Admin.objects.get(id=user_id)
            return JsonResponse({'id': user.id, 'role': role, 'email': user.email})

    except Exception as e:
        return JsonResponse({'erreur': str(e)}, status=401)


@csrf_exempt
def update_me(request):
    if request.method != 'PATCH':
        return JsonResponse({'erreur': 'Méthode non autorisée'}, status=405)
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
        data = json.loads(request.body)
        if role == 'client':
            user = Client.objects.get(id=user_id)
            for field in ['full_name', 'phone', 'wilaya', 'driver_license', 'gender', 'marital_status']:
                if field in data:
                    setattr(user, field, data[field])
            if 'age' in data:
                user.age = int(data['age']) if data['age'] else None
            if 'family_size' in data:
                user.family_size = int(data['family_size']) if data['family_size'] else None
            user.save()
            return JsonResponse({'success': True})
        elif role == 'agency':
            user = Agency.objects.get(id=user_id)
            for field in ['owner_name', 'phone', 'wilaya', 'address', 'description']:
                if field in data:
                    setattr(user, field, data[field])
            user.save()
            return JsonResponse({'success': True})
        return JsonResponse({'erreur': 'Rôle non supporté'}, status=400)
    except Exception as e:
        return JsonResponse({'erreur': str(e)}, status=400)


@csrf_exempt
def agency_public_info(request, agency_id):
    try:
        agency = Agency.objects.get(id=agency_id)
        return JsonResponse({
            'agency_name': agency.agency_name,
            'phone': agency.phone or '',
            'wilaya': agency.wilaya or '',
            'address': agency.address or '',
        })
    except Agency.DoesNotExist:
        return JsonResponse({'erreur': 'Agence introuvable'}, status=404)


def delete_me(request):
    if request.method != 'DELETE':
        return JsonResponse({'erreur': 'Méthode non autorisée'}, status=405)
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
            Client.objects.get(id=user_id).delete()
        elif role == 'agency':
            Agency.objects.get(id=user_id).delete()
        else:
            return JsonResponse({'erreur': 'Suppression non autorisée'}, status=403)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'erreur': str(e)}, status=400)
