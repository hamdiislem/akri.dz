import json
import pika
import decimal
from django.http import JsonResponse
from django.conf import settings
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Booking
from .serializers import BookingSerializer
from cars.models import Car
from utils import require_auth


def publish_to_rabbitmq(queue, message):
    try:
        if settings.RABBITMQ_URL:
            params = pika.URLParameters(settings.RABBITMQ_URL)
        else:
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


class BookingViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
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
        err = require_auth(request, 'client')
        if err:
            return err
        bookings = Booking.objects.filter(client_id=request.user_info['id']).order_by('-created_at')
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='agence')
    def agence(self, request):
        err = require_auth(request, 'agency')
        if err:
            return err
        bookings = Booking.objects.filter(agency_id=request.user_info['id']).order_by('-created_at')
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='confirmer')
    def confirmer(self, request, pk=None):
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

    @action(detail=True, methods=['post'], url_path='completer')
    def completer(self, request, pk=None):
        err = require_auth(request, 'agency')
        if err:
            return err
        booking = self.get_object()
        if booking.agency_id != request.user_info['id']:
            return JsonResponse({'erreur': 'Accès interdit'}, status=403)
        if booking.status != 'CONFIRMED':
            return JsonResponse({'erreur': 'Seules les réservations confirmées peuvent être terminées'}, status=400)
        booking.status = 'COMPLETED'
        booking.save()
        return JsonResponse({'message': 'Réservation terminée', 'status': 'COMPLETED'})

    @action(detail=False, methods=['get'], url_path='disponibilite')
    def disponibilite(self, request):
        car_id = request.query_params.get('car')
        if not car_id:
            return Response([])
        bookings = Booking.objects.filter(
            car_id=car_id,
            status__in=['PENDING', 'CONFIRMED']
        ).values('start_date', 'end_date')
        return Response([
            {'start': str(b['start_date']), 'end': str(b['end_date'])}
            for b in bookings
        ])
