from django.db import models
from cars.models import Car


BOOKING_STATUS = [
    ('PENDING', 'PENDING'),
    ('CONFIRMED', 'CONFIRMED'),
    ('COMPLETED', 'COMPLETED'),
    ('CANCELLED', 'CANCELLED'),
]


class Booking(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='bookings')
    client_id = models.IntegerField()    # references Client in auth-service DB
    agency_id = models.IntegerField()    # references Agency in auth-service DB
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='PENDING')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking #{self.id} — {self.car} (client {self.client_id})"
