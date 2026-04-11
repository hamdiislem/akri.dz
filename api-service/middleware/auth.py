import requests as http_requests
from django.conf import settings


def get_auth_service_url():
    """Ask Consul for auth-service address. Falls back to env var."""
    consul_host = settings.CONSUL_HOST
    try:
        import consul
        c = consul.Consul(host=consul_host, port=settings.CONSUL_PORT)
        _, services = c.health.service('auth-service', passing=True)
        if services:
            svc = services[0]['Service']
            return f"http://{svc['Address']}:{svc['Port']}"
    except Exception:
        pass
    return settings.AUTH_SERVICE_URL


class AuthMiddleware:
    """
    For every request, if a JWT token is present (cookie or Authorization header),
    call auth-service /api/auth/verify/ and attach user info to request.
    """

    OPEN_PATHS = [
        '/api/cars/',
        '/api/reviews/',
        '/admin/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user_info = None

        token = request.COOKIES.get('token')
        if not token:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ', 1)[1]

        if token:
            try:
                auth_url = get_auth_service_url()
                resp = http_requests.get(
                    f"{auth_url}/api/auth/verify/",
                    cookies={'token': token},
                    timeout=30,
                )
                if resp.status_code == 200:
                    request.user_info = resp.json()
                    request.user_info['token'] = token
            except Exception:
                pass

        return self.get_response(request)
