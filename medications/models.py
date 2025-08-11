from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Medication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('taken', 'Taken'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medications')
    name = models.CharField(max_length=100)
    dosage = models.TextField()
    scheduled_datetime = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_datetime']
    
    def __str__(self):
        return f"{self.name} - {self.scheduled_datetime.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def is_overdue(self):
        return self.scheduled_datetime < timezone.now() and self.status == 'pending'
