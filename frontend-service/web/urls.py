from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/client/', views.register_client, name='register_client'),
    path('register/agency/', views.register_agency, name='register_agency'),
    path('cars/', views.cars_list, name='cars'),
    path('cars/ajouter/', views.add_car, name='add_car'),
    path('cars/<int:car_id>/', views.car_detail, name='car_detail'),
    path('cars/<int:car_id>/supprimer/', views.supprimer_voiture, name='supprimer_voiture'),
    path('dashboard/client/', views.dashboard_client, name='dashboard_client'),
    path('dashboard/agency/', views.dashboard_agency, name='dashboard_agency'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('bookings/<int:booking_id>/confirmer/', views.confirmer_booking, name='confirmer_booking'),
    path('bookings/<int:booking_id>/annuler/', views.annuler_booking, name='annuler_booking'),
    path('admin/agences/<int:agency_id>/verifier/', views.admin_verifier_agence, name='admin_verifier_agence'),
    path('admin/agences/<int:agency_id>/bannir/', views.admin_bannir_agence, name='admin_bannir_agence'),
    path('admin/clients/<int:client_id>/bannir/', views.admin_bannir_client, name='admin_bannir_client'),
    path('bookings/<int:booking_id>/avis/', views.submit_review, name='submit_review'),
]
