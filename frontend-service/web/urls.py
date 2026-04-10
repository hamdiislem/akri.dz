from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/client/', views.register_client, name='register_client'),
    path('register/agency/', views.register_agency, name='register_agency'),
    path('cars/', views.cars_list, name='cars'),
    path('cars/<int:car_id>/', views.car_detail, name='car_detail'),
    path('dashboard/client/', views.dashboard_client, name='dashboard_client'),
    path('dashboard/agency/', views.dashboard_agency, name='dashboard_agency'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('bookings/<int:booking_id>/confirmer/', views.confirmer_booking, name='confirmer_booking'),
    path('bookings/<int:booking_id>/annuler/', views.annuler_booking, name='annuler_booking'),
]
