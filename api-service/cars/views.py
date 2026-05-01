from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Car
from .serializers import CarSerializer
from utils import require_auth


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer

    def get_queryset(self):
        queryset = Car.objects.all()
        wilaya = self.request.query_params.get('wilaya')
        available = self.request.query_params.get('available')
        fuel_type = self.request.query_params.get('fuel_type')
        transmission = self.request.query_params.get('transmission')
        if wilaya:
            queryset = queryset.filter(wilaya=wilaya)
        if available is not None:
            queryset = queryset.filter(available=available.lower() == 'true')
        if fuel_type:
            queryset = queryset.filter(fuel_type=fuel_type)
        if transmission:
            queryset = queryset.filter(transmission=transmission)
        return queryset

    def create(self, request, *args, **kwargs):
        err = require_auth(request, 'agency')
        if err:
            return err
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(agency_id=request.user_info['id'])
        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        err = require_auth(request, 'agency')
        if err:
            return err
        car = self.get_object()
        if car.agency_id != request.user_info['id']:
            return JsonResponse({'erreur': 'Accès interdit'}, status=403)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        from rest_framework.exceptions import MethodNotAllowed
        raise MethodNotAllowed('PATCH')

    def destroy(self, request, *args, **kwargs):
        err = require_auth(request, 'agency')
        if err:
            return err
        car = self.get_object()
        if car.agency_id != request.user_info['id']:
            return JsonResponse({'erreur': 'Accès interdit'}, status=403)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='mine')
    def mine(self, request):
        err = require_auth(request, 'agency')
        if err:
            return err
        cars = Car.objects.filter(agency_id=request.user_info['id'])
        serializer = self.get_serializer(cars, many=True)
        return Response(serializer.data)
