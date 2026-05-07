from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.StatsView.as_view(), name='admin_stats'),
    path('bookings/', views.AllBookingsView.as_view(), name='admin_bookings'),
    path('tickets/', views.AllTicketsView.as_view(), name='admin_tickets'),
    path('tickets/<int:ticket_id>/respond/', views.RespondTicketView.as_view(), name='admin_respond_ticket'),
    path('client-reviews/', views.AllClientReviewsView.as_view(), name='admin_client_reviews'),
    path('bookings/<int:booking_id>/annuler/', views.AdminCancelBookingView.as_view(), name='admin_cancel_booking'),
    path('notifications/', views.AdminNotificationsView.as_view(), name='admin_notifications'),
]
