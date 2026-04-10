from django.db import models
from cars.models import Car
from bookings.models import Booking


class Review(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reviews')
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    client_id = models.IntegerField()
    rating = models.IntegerField()  # 1–5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avis #{self.id} — {self.car} ({self.rating}/5)"
