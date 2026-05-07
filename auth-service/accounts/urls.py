from django.urls import path
from . import views

urlpatterns = [
    path('register/client/', views.register_client, name='register_client'),
    path('register/agency/', views.register_agency, name='register_agency'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('verify/', views.verify, name='verify'),
    path('me/', views.me, name='me'),
    path('me/update/', views.update_me, name='update_me'),
    path('me/delete/', views.delete_me, name='delete_me'),
    # Admin
    path('admin/agencies/', views.admin_list_agencies, name='admin_list_agencies'),
    path('admin/agencies/<int:agency_id>/verify/', views.admin_verify_agency, name='admin_verify_agency'),
    path('admin/agencies/<int:agency_id>/ban/', views.admin_ban_agency, name='admin_ban_agency'),
    path('admin/agencies/<int:agency_id>/unban/', views.admin_unban_agency, name='admin_unban_agency'),
    path('admin/clients/', views.admin_list_clients, name='admin_list_clients'),
    path('admin/clients/<int:client_id>/ban/', views.admin_ban_client, name='admin_ban_client'),
    path('admin/clients/<int:client_id>/unban/', views.admin_unban_client, name='admin_unban_client'),
    path('admin/clients/<int:client_id>/delete/', views.admin_delete_client, name='admin_delete_client'),
    path('admin/agencies/<int:agency_id>/delete/', views.admin_delete_agency, name='admin_delete_agency'),
    path('admin/clients/<int:client_id>/', views.admin_get_client, name='admin_get_client'),
    path('admin/agencies/<int:agency_id>/', views.admin_get_agency, name='admin_get_agency'),
    path('agencies/<int:agency_id>/info/', views.agency_public_info, name='agency_public_info'),
    path('setup-admin/', views.setup_admin, name='setup_admin'),
    path('clients/<int:client_id>/info/', views.client_public_info, name='client_public_info'),
]
