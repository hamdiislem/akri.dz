from django.http import JsonResponse
from django.views import View
from cars.models import Car
from bookings.models import Booking
from reviews.models import Review
from tickets.models import Ticket
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


class AllTicketsView(View):
    """GET /api/admin/tickets/ — tous les tickets"""
    def get(self, request):
        err = require_auth(request, 'admin')
        if err:
            return err
        tickets = list(Ticket.objects.all().order_by('-created_at').values())
        return JsonResponse(tickets, safe=False)


class RespondTicketView(View):
    """POST /api/admin/tickets/<id>/respond/"""
    def post(self, request, ticket_id):
        err = require_auth(request, 'admin')
        if err:
            return err
        import json
        try:
            data = json.loads(request.body)
            ticket = Ticket.objects.get(id=ticket_id)
            ticket.admin_response = data.get('admin_response', '').strip()
            ticket.status = data.get('status', 'IN_PROGRESS')
            ticket.save(update_fields=['admin_response', 'status', 'updated_at'])
            return JsonResponse({'message': 'Réponse enregistrée', 'status': ticket.status})
        except Ticket.DoesNotExist:
            return JsonResponse({'erreur': 'Ticket introuvable'}, status=404)
        except Exception as e:
            return JsonResponse({'erreur': str(e)}, status=400)
