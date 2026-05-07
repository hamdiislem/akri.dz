from rest_framework import serializers
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['sender_id', 'sender_role', 'status', 'admin_response', 'created_at', 'updated_at']
