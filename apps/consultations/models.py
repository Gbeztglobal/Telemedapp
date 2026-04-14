from django.db import models
from apps.accounts.models import PatientProfile, DoctorProfile

class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.user.username} with {self.doctor.user.username} on {self.appointment_date}"

class MedicalRecord(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, related_name='record')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='medical_records')
    diagnosis = models.TextField()
    prescription = models.TextField()
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Record for {self.patient.user.username} by {self.doctor.user.username}"

class Prescription(models.Model):
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions')
    drug_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100) # e.g., 500mg
    frequency = models.CharField(max_length=100) # e.g., Twice daily
    duration = models.CharField(max_length=100) # e.g., 5 days
    instructions = models.TextField(blank=True)
    digital_signature = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.drug_name} - {self.medical_record.patient.user.username}"

class VitalSign(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='vitals')
    recorded_by = models.ForeignKey(DoctorProfile, on_delete=models.SET_NULL, null=True, blank=True)
    blood_pressure = models.CharField(max_length=20, blank=True) # e.g., 120/80
    heart_rate = models.IntegerField(null=True, blank=True) # bpm
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True) # Celsius
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # kg
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vitals for {self.patient.user.username} on {self.recorded_at.date()}"

class LabResult(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='lab_results')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.SET_NULL, null=True, related_name='ordered_labs')
    test_type = models.CharField(max_length=100)
    result_file = models.FileField(upload_to='lab_results/')
    summary = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.test_type} Lab for {self.patient.user.username}"
