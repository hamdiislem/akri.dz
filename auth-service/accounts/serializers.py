from rest_framework import serializers
from .models import Client, Agency, Admin


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}


class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}
