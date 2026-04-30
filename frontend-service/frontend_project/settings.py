import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-frontend-change-me')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'web',
]

STATIC_URL = '/static/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'frontend_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'frontend_project.wsgi.application'

# Backend service URLs
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:8001')
API_SERVICE_URL = os.getenv('API_SERVICE_URL', 'http://localhost:8002')
# Render provides host without protocol — add https:// if needed
if AUTH_SERVICE_URL and not AUTH_SERVICE_URL.startswith('http'):
    AUTH_SERVICE_URL = f'https://{AUTH_SERVICE_URL}'
if API_SERVICE_URL and not API_SERVICE_URL.startswith('http'):
    API_SERVICE_URL = f'https://{API_SERVICE_URL}'

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
