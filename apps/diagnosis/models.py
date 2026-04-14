from django.db import models
from apps.accounts.models import PatientProfile

class Diagnosis(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='diagnoses')
    symptoms_reported = models.TextField()
    malaria_risk = models.CharField(max_length=20)
    cholera_risk = models.CharField(max_length=20)
    is_urgent = models.BooleanField(default=False)
    drug_recommendations = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Diagnosis for {self.patient.user.username} on {self.created_at.strftime('%Y-%m-%d')}"
