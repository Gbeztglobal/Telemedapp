from django.db import models
from apps.accounts.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(blank=True)
    attachment = models.FileField(upload_to='chat_files/', null=True, blank=True)
    audio_note = models.FileField(upload_to='chat_audio/', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Simple unthreaded model for 1v1 PMs
    
    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} at {self.timestamp}"
