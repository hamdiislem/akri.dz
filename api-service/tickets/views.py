from django.http import JsonResponse
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Ticket
from .serializers import TicketSerializer
from utils import require_auth


class TicketViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def create(self, request, *args, **kwargs):
        err = require_auth(request, 'client', 'agency')
        if err:
            return err
        data = request.data
        subject = data.get('subject', '').strip()
        body = data.get('body', '').strip()
        if not subject or not body:
            return JsonResponse({'erreur': 'Sujet et message requis'}, status=400)

        ticket = Ticket.objects.create(
            sender_id=request.user_info['id'],
            sender_role=request.user_info['role'],
            subject=subject,
            body=body,
            reported_id=data.get('reported_id') or None,
            reported_role=data.get('reported_role', ''),
        )
        return Response(TicketSerializer(ticket).data, status=201)

    @action(detail=False, methods=['get'], url_path='mine')
    def mine(self, request):
        err = require_auth(request, 'client', 'agency')
        if err:
            return err
        tickets = Ticket.objects.filter(
            sender_id=request.user_info['id'],
            sender_role=request.user_info['role'],
        ).order_by('-created_at')
        return Response(TicketSerializer(tickets, many=True).data)
