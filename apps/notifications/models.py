from django.db import models
from apps.accounts.models import User

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        MESSAGE = 'MESSAGE', 'Message'
        APPOINTMENT = 'APPOINTMENT', 'Appointment'
        DIAGNOSIS = 'DIAGNOSIS', 'Diagnosis'
        SYSTEM = 'SYSTEM', 'System'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices, default=NotificationType.SYSTEM)
    action_link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"
