from django.http import JsonResponse
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Review, ClientReview
from .serializers import ReviewSerializer, ClientReviewSerializer
from bookings.models import Booking
from utils import require_auth


class ReviewViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        queryset = Review.objects.all()
        car_id = self.request.query_params.get('car')
        if car_id:
            queryset = queryset.filter(car_id=car_id)
        return queryset

    def create(self, request, *args, **kwargs):
        err = require_auth(request, 'client')
        if err:
            return err
        try:
            data = request.data
            booking = Booking.objects.get(id=data.get('booking'))
            if booking.client_id != request.user_info['id']:
                return JsonResponse({'erreur': 'Ce n\'est pas votre réservation'}, status=403)
            if booking.status != 'COMPLETED':
                return JsonResponse({'erreur': 'Réservation non complétée'}, status=400)
            if hasattr(booking, 'review'):
                return JsonResponse({'erreur': 'Avis déjà soumis'}, status=409)

            rating = int(data.get('rating', 0))
            if not (1 <= rating <= 5):
                return JsonResponse({'erreur': 'Note entre 1 et 5'}, status=400)

            review = Review.objects.create(
                car=booking.car,
                booking=booking,
                client_id=request.user_info['id'],
                rating=rating,
                comment=data.get('comment', ''),
            )
            serializer = self.get_serializer(review)
            return Response(serializer.data, status=201)
        except Booking.DoesNotExist:
            return JsonResponse({'erreur': 'Réservation introuvable'}, status=404)
        except Exception as e:
            return JsonResponse({'erreur': str(e)}, status=400)


class ClientReviewViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = ClientReview.objects.all()
    serializer_class = ClientReviewSerializer

    def get_queryset(self):
        queryset = ClientReview.objects.all()
        client_id = self.request.query_params.get('client_id')
        booking_id = self.request.query_params.get('booking')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        if booking_id:
            queryset = queryset.filter(booking_id=booking_id)
        return queryset

    @action(detail=False, methods=['get'], url_path='mine')
    def mine(self, request):
        err = require_auth(request, 'agency')
        if err:
            return err
        reviews = ClientReview.objects.filter(agency_id=request.user_info['id'])
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        err = require_auth(request, 'agency')
        if err:
            return err
        try:
            data = request.data
            booking = Booking.objects.get(id=data.get('booking'))
            if booking.agency_id != request.user_info['id']:
                return JsonResponse({'erreur': 'Ce n\'est pas votre réservation'}, status=403)
            if booking.status != 'COMPLETED':
                return JsonResponse({'erreur': 'Réservation non complétée'}, status=400)
            if hasattr(booking, 'client_review'):
                return JsonResponse({'erreur': 'Évaluation déjà soumise'}, status=409)

            rating = int(data.get('rating', 0))
            if not (1 <= rating <= 5):
                return JsonResponse({'erreur': 'Note entre 1 et 5'}, status=400)

            cr = ClientReview.objects.create(
                booking=booking,
                agency_id=request.user_info['id'],
                client_id=booking.client_id,
                rating=rating,
                comment=data.get('comment', ''),
            )
            serializer = self.get_serializer(cr)
            return Response(serializer.data, status=201)
        except Booking.DoesNotExist:
            return JsonResponse({'erreur': 'Réservation introuvable'}, status=404)
        except Exception as e:
            return JsonResponse({'erreur': str(e)}, status=400)
