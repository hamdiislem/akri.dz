from django.db import models


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Ouvert'),
        ('IN_PROGRESS', 'En cours'),
        ('RESOLVED', 'Résolu'),
    ]

    sender_id = models.IntegerField()
    sender_role = models.CharField(max_length=10)   # 'client' | 'agency'
    subject = models.CharField(max_length=200)
    body = models.TextField()
    reported_phone = models.CharField(max_length=30, blank=True)
    reported_role = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    admin_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket #{self.id} — {self.sender_role} {self.sender_id} — {self.status}"
