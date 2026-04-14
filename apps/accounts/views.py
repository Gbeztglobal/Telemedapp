from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import User, PatientProfile, DoctorProfile
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

@csrf_exempt
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_router')
        
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('dashboard_router')
        else:
            messages.error(request, 'Invalid credentials.')
            
    return render(request, 'accounts/login.html')

@csrf_exempt
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_router')
        
    if request.method == 'POST':
        r = request.POST.get('role', User.Role.PATIENT)
        u = request.POST.get('username')
        p = request.POST.get('password')
        fn = request.POST.get('first_name', '')
        ln = request.POST.get('last_name', '')
        e = request.POST.get('email', '')
        phone = request.POST.get('phone_number', '')
        g = request.POST.get('gender', '')
        dob = request.POST.get('date_of_birth') or None
        
        if User.objects.filter(username=u).exists():
            messages.error(request, 'Username already taken.')
        else:
            user = User.objects.create_user(username=u, password=p, role=r, first_name=fn, last_name=ln, email=e)
            if r == User.Role.PATIENT:
                PatientProfile.objects.create(user=user, phone_number=phone, gender=g, date_of_birth=dob)
            elif r == User.Role.DOCTOR:
                DoctorProfile.objects.create(user=user, phone_number=phone, gender=g)
                
            login(request, user)
            return redirect('dashboard_router')
            
    return render(request, 'accounts/register.html')

@login_required
def dashboard_router(request):
    """
    Routes the user to their respective dashboard based on their role.
    """
    if request.user.role == User.Role.DOCTOR:
        return redirect('doctor_dashboard')
    
    # Default fallback to patient
    return redirect('patient_dashboard')

from apps.consultations.models import Appointment, MedicalRecord
from apps.diagnosis.models import Diagnosis

@login_required
def patient_dashboard(request):
    if request.user.role != User.Role.PATIENT:
        return redirect('dashboard_router')
        
    profile = request.user.patient_profile
    upcoming_visits = Appointment.objects.filter(patient=profile, status='APPROVED').order_by('appointment_date')
    diagnosis_logs = Diagnosis.objects.filter(patient=profile).order_by('-created_at')
    medical_records = MedicalRecord.objects.filter(patient=profile).order_by('-created_at')
    
    context = {
        'upcoming_visits': upcoming_visits,
        'upcoming_visits_count': upcoming_visits.count(),
        'diagnosis_logs': diagnosis_logs,
        'diagnosis_logs_count': diagnosis_logs.count(),
        'medical_records': medical_records,
        'medical_records_count': medical_records.count(),
    }
    return render(request, 'accounts/patient_dashboard.html', context)

@login_required
def doctor_dashboard(request):
    if request.user.role != User.Role.DOCTOR:
        return redirect('dashboard_router')
        
    profile = request.user.doctor_profile
    pending_requests = Appointment.objects.filter(doctor=profile, status='PENDING').order_by('-created_at')
    upcoming_visits = Appointment.objects.filter(doctor=profile, status='APPROVED').order_by('appointment_date')
    
    # Fetch distinct patient profiles that have an appointment with this doctor
    active_patients = PatientProfile.objects.filter(appointments__doctor=profile).distinct()
    
    context = {
        'pending_requests': pending_requests,
        'pending_requests_count': pending_requests.count(),
        'upcoming_visits': upcoming_visits,
        'active_patients': active_patients,
        'active_patients_count': active_patients.count(),
    }
    return render(request, 'accounts/doctor_dashboard.html', context)

@login_required
def edit_profile(request):
    user = request.user
    
    if request.method == 'POST':
        # Update Base User Data
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        if request.POST.get('email'):
            user.email = request.POST.get('email')
        user.save()
        
        # Update Profile Data
        if user.role == User.Role.PATIENT:
            p = user.patient_profile
            p.phone_number = request.POST.get('phone_number', p.phone_number)
            p.allergies = request.POST.get('allergies', p.allergies)
            p.bio = request.POST.get('bio', p.bio)
            if request.POST.get('date_of_birth'):
                p.date_of_birth = request.POST.get('date_of_birth')
            p.save()
        else:
            d = user.doctor_profile
            d.phone_number = request.POST.get('phone_number', d.phone_number)
            d.specialty = request.POST.get('specialty', d.specialty)
            d.license_number = request.POST.get('license_number', d.license_number)
            d.bio = request.POST.get('bio', d.bio)
            d.save()
            
        messages.success(request, 'Profile updated successfully!')
        return redirect('dashboard_router')
        
    return render(request, 'accounts/edit_profile.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def patient_medical_record(request, patient_id):
    if request.user.role != User.Role.DOCTOR:
        return redirect('dashboard_router')
        
    patient = get_object_or_404(PatientProfile, id=patient_id)
    
    # Get AI assessments
    try:
        from apps.diagnosis.models import Diagnosis
        assessments = Diagnosis.objects.filter(patient=patient).order_by('-created_at')
    except Exception:
        assessments = []
        
    # Get past consultations
    try:
        past_appointments = Appointment.objects.filter(patient=patient, status='APPROVED').count()
        medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-created_at')
    except Exception:
        past_appointments = 0
        medical_records = []
        
    context = {
        'pat': patient,
        'assessments': assessments,
        'consultation_count': past_appointments,
        'medical_records': medical_records
    }
    return render(request, 'accounts/patient_medical_record.html', context)
