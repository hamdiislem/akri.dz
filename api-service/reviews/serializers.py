from rest_framework import serializers
from .models import Review, ClientReview


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['client_id', 'car', 'booking', 'created_at']


class ClientReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientReview
        fields = '__all__'
        read_only_fields = ['agency_id', 'client_id', 'booking', 'created_at']
