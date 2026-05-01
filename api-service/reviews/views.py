from django.http import JsonResponse
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from .models import Review
from .serializers import ReviewSerializer
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
