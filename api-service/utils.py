from django.http import JsonResponse


def require_auth(request, *roles):
    if not request.user_info:
        return JsonResponse({'erreur': 'Non authentifié'}, status=401)
    if roles and request.user_info.get('role') not in roles:
        return JsonResponse({'erreur': 'Accès interdit'}, status=403)
    return None
