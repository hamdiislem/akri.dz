from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.StatsView.as_view(), name='admin_stats'),
    path('bookings/', views.AllBookingsView.as_view(), name='admin_bookings'),
]
