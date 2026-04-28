from django.http import JsonResponse
from django.views import View
from cars.models import Car
from bookings.models import Booking
from reviews.models import Review
from utils import require_auth


class StatsView(View):
    """GET /api/admin/stats/ — statistiques globales"""
    def get(self, request):
        err = require_auth(request, 'admin')
        if err:
            return err
        return JsonResponse({
            'total_cars': Car.objects.count(),
            'total_bookings': Booking.objects.count(),
            'total_reviews': Review.objects.count(),
            'pending_bookings': Booking.objects.filter(status='PENDING').count(),
            'confirmed_bookings': Booking.objects.filter(status='CONFIRMED').count(),
        })


class AllBookingsView(View):
    """GET /api/admin/bookings/ — toutes les réservations"""
    def get(self, request):
        err = require_auth(request, 'admin')
        if err:
            return err
        bookings = Booking.objects.all().order_by('-created_at').values(
            'id', 'car_id', 'client_id', 'agency_id',
            'start_date', 'end_date', 'total_price', 'status', 'created_at'
        )
        return JsonResponse(list(bookings), safe=False)
