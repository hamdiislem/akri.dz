from django.urls import path
from . import views

urlpatterns = [
    path('register/client/', views.register_client, name='register_client'),
    path('register/agency/', views.register_agency, name='register_agency'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('verify/', views.verify, name='verify'),
    path('me/', views.me, name='me'),
]
