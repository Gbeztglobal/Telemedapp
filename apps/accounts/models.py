from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = 'PATIENT', 'Patient'
        DOCTOR = 'DOCTOR', 'Doctor'
        
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)
    
class PatientProfile(models.Model):
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'))
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    allergies = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def get_avatar_url(self):
        style = 'lorelei' if self.gender == 'F' else 'personas'
        return f"https://api.dicebear.com/7.x/{style}/svg?seed={self.user.username}&backgroundColor=b6e3f4"

    @property
    def age(self):
        import datetime
        if self.date_of_birth:
            today = datetime.date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

    def __str__(self):
        return f"Patient: {self.user.username}"

class DoctorProfile(models.Model):
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'))
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialty = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    license_number = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def get_avatar_url(self):
        style = 'lorelei' if self.gender == 'F' else 'personas'
        return f"https://api.dicebear.com/7.x/{style}/svg?seed={self.user.username}&backgroundColor=c0aede"

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} ({self.specialty})"

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action = models.CharField(max_length=255)
    module = models.CharField(max_length=100) # e.g. 'Prescription', 'MedicalRecord'
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"[{self.timestamp}] {self.user} - {self.action} on {self.module}"
