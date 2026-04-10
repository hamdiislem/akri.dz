import json
import pika
import decimal
from django.http import JsonResponse
from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Booking
from .serializers import BookingSerializer
from cars.models import Car


def require_auth(request, *roles):
    if not request.user_info:
        return JsonResponse({'erreur': 'Non authentifié'}, status=401)
    if roles and request.user_info.get('role') not in roles:
        return JsonResponse({'erreur': 'Accès interdit'}, status=403)
    return None


def publish_to_rabbitmq(queue, message):
    """Publish a message to a RabbitMQ queue (asynchronous communication)."""
    try:
        credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS)
        params = pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=credentials,
        )
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        connection.close()
        print(f'[RabbitMQ] Message publié dans "{queue}": {message}')
    except Exception as e:
        print(f'[RabbitMQ] Erreur: {e}')


class BookingViewSet(viewsets.ModelViewSet):
    """
    TP4 pattern: ModelViewSet + actions personnalisées
    POST   /api/bookings/              — créer une réservation (client)
    GET    /api/bookings/              — liste (admin)
    GET    /api/bookings/mes-reservations/ — mes réservations (client)
    GET    /api/bookings/agence/       — réservations de l'agence
    POST   /api/bookings/<id>/confirmer/ — confirmer (agency) → RabbitMQ
    POST   /api/bookings/<id>/annuler/  — annuler → RabbitMQ
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        err = require_auth(request, 'client')
        if err:
            return err
        try:
            data = request.data
            car = Car.objects.get(id=data.get('car'))
            if not car.available:
                return JsonResponse({'erreur': 'Voiture non disponible'}, status=400)

            from datetime import date
            start = date.fromisoformat(str(data.get('start_date')))
            end = date.fromisoformat(str(data.get('end_date')))
            if end <= start:
                return JsonResponse({'erreur': 'Dates invalides'}, status=400)

            # Check for conflicting bookings
            conflict = Booking.objects.filter(
                car=car,
                status__in=['PENDING', 'CONFIRMED'],
                start_date__lt=end,
                end_date__gt=start,
            ).exists()
            if conflict:
                return JsonResponse({'erreur': 'Voiture déjà réservée pour ces dates'}, status=409)

            days = (end - start).days
            total = decimal.Decimal(str(car.price_per_day)) * days

            booking = Booking.objects.create(
                car=car,
                client_id=request.user_info['id'],
                agency_id=car.agency_id,
                start_date=start,
                end_date=end,
                total_price=total,
                message=data.get('message', ''),
            )
            serializer = self.get_serializer(booking)
            return Response(serializer.data, status=201)
        except Car.DoesNotExist:
            return JsonResponse({'erreur': 'Voiture introuvable'}, status=404)
        except Exception as e:
            return JsonResponse({'erreur': str(e)}, status=400)

    @action(detail=False, methods=['get'], url_path='mes-reservations')
    def mes_reservations(self, request):
        """GET /api/bookings/mes-reservations/ — réservations du client connecté"""
        err = require_auth(request, 'client')
        if err:
            return err
        bookings = Booking.objects.filter(client_id=request.user_info['id']).order_by('-created_at')
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='agence')
    def agence(self, request):
        """GET /api/bookings/agence/ — réservations de l'agence connectée"""
        err = require_auth(request, 'agency')
        if err:
            return err
        bookings = Booking.objects.filter(agency_id=request.user_info['id']).order_by('-created_at')
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='confirmer')
    def confirmer(self, request, pk=None):
        """POST /api/bookings/<id>/confirmer/ — agence confirme → RabbitMQ"""
        err = require_auth(request, 'agency')
        if err:
            return err
        booking = self.get_object()
        if booking.agency_id != request.user_info['id']:
            return JsonResponse({'erreur': 'Accès interdit'}, status=403)
        if booking.status != 'PENDING':
            return JsonResponse({'erreur': 'Réservation non en attente'}, status=400)

        booking.status = 'CONFIRMED'
        booking.save()

        # Asynchronous notification via RabbitMQ
        publish_to_rabbitmq('booking.confirmed', {
            'booking_id': booking.id,
            'car': str(booking.car),
            'client_id': booking.client_id,
            'agency_id': booking.agency_id,
            'start_date': str(booking.start_date),
            'end_date': str(booking.end_date),
            'total_price': str(booking.total_price),
        })

        return JsonResponse({'message': 'Réservation confirmée', 'status': 'CONFIRMED'})

    @action(detail=True, methods=['post'], url_path='annuler')
    def annuler(self, request, pk=None):
        """POST /api/bookings/<id>/annuler/ — annuler une réservation → RabbitMQ"""
        err = require_auth(request, 'client', 'agency', 'admin')
        if err:
            return err
        booking = self.get_object()

        role = request.user_info['role']
        user_id = request.user_info['id']
        if role == 'client' and booking.client_id != user_id:
            return JsonResponse({'erreur': 'Accès interdit'}, status=403)
        if role == 'agency' and booking.agency_id != user_id:
            return JsonResponse({'erreur': 'Accès interdit'}, status=403)
        if booking.status in ['COMPLETED', 'CANCELLED']:
            return JsonResponse({'erreur': 'Impossible d\'annuler'}, status=400)

        booking.status = 'CANCELLED'
        booking.save()

        publish_to_rabbitmq('booking.cancelled', {
            'booking_id': booking.id,
            'car': str(booking.car),
            'client_id': booking.client_id,
        })

        return JsonResponse({'message': 'Réservation annulée', 'status': 'CANCELLED'})
