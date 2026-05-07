from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.StatsView.as_view(), name='admin_stats'),
    path('bookings/', views.AllBookingsView.as_view(), name='admin_bookings'),
    path('tickets/', views.AllTicketsView.as_view(), name='admin_tickets'),
    path('tickets/<int:ticket_id>/respond/', views.RespondTicketView.as_view(), name='admin_respond_ticket'),
]
