from django.db import models


TRANSMISSION_CHOICES = [
    ('MANUAL', 'MANUAL'),
    ('AUTOMATIC', 'AUTOMATIC'),
]

FUEL_CHOICES = [
    ('PETROL', 'PETROL'),
    ('DIESEL', 'DIESEL'),
    ('ELECTRIC', 'ELECTRIC'),
    ('HYBRID', 'HYBRID'),
]


class Car(models.Model):
    agency_id = models.IntegerField()  # references Agency in auth-service DB
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    seats = models.IntegerField()
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default='MANUAL')
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='PETROL')
    wilaya = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    images = models.JSONField(default=list)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"
