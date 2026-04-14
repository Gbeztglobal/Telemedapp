from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment
from apps.accounts.models import DoctorProfile, User
from datetime import datetime

@login_required
def video_call_room(request, room_name):
    # Parse room_name (e.g., '2_12') to find the other user
    ids = room_name.split('_')
    patient_diagnoses = None
    target_user = None
    
    if len(ids) == 2:
        try:
            id1, id2 = int(ids[0]), int(ids[1])
            target_id = id2 if request.user.id == id1 else id1
            target_user = User.objects.get(id=target_id)
            
            # Trigger live ring
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'notify_{target_user.id}',
                {
                    'type': 'send_notification',
                    'message': 'Incoming Call',
                    'count': target_user.notifications.filter(is_read=False).count(),
                    'action': 'INCOMING_CALL',
                    'caller_name': request.user.get_full_name() or request.user.username,
                    'room_url': request.get_full_path()
                }
            )
        except Exception:
            pass
    elif room_name.isdigit():
        try:
            appt = Appointment.objects.get(id=int(room_name))
            if request.user.role == User.Role.DOCTOR:
                target_user = appt.patient.user
            elif request.user.role == User.Role.PATIENT:
                target_user = appt.doctor.user
        except Exception:
            pass
            
    if request.user.role == User.Role.DOCTOR and target_user and target_user.role == User.Role.PATIENT:
        try:
            from apps.diagnosis.models import Diagnosis
            patient_diagnoses = Diagnosis.objects.filter(patient=target_user.patient_profile).order_by('-created_at')[:4]
        except Exception:
            pass

    is_audio_only = request.GET.get('audio_only', '0') == '1'

    # Build return URL — go back to chat if came from chat, else dashboard
    return_url = request.META.get('HTTP_REFERER', '/dashboard/')
    if target_user and '/chat/' not in return_url and '/messaging/' not in return_url:
        return_url = f'/chat/room/{target_user.id}/'

    return render(request, 'consultations/video_call.html', {
        'room_name': room_name,
        'target_user': target_user,
        'diagnoses': patient_diagnoses,
        'is_audio_only': is_audio_only,
        'return_url': return_url
    })

@login_required
def book_appointment(request):
    if request.user.role != User.Role.PATIENT:
        return redirect('dashboard_router')
        
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        date_str = request.POST.get('appointment_date')
        
        try:
            appt_date = datetime.fromisoformat(date_str)
            doctor = DoctorProfile.objects.get(id=doctor_id)
            notes = request.POST.get('notes', '')
            is_urgent = request.POST.get('is_urgent') == 'on'
            
            if is_urgent:
                notes = f"[URGENT TRIAGE NEEDED] {notes}"
            
            if Appointment.objects.filter(doctor=doctor, appointment_date=appt_date, status__in=[Appointment.Status.PENDING, Appointment.Status.APPROVED]).exists():
                messages.error(request, 'This time slot is already booked.')
            else:
                Appointment.objects.create(
                    patient=request.user.patient_profile,
                    doctor=doctor,
                    appointment_date=appt_date,
                    notes=notes
                )
                messages.success(request, 'Appointment requested successfully.')
                return redirect('patient_dashboard')
        except ValueError:
            messages.error(request, 'Invalid date format provided.')
        except DoctorProfile.DoesNotExist:
            messages.error(request, 'Selected doctor does not exist.')
        except Exception as e:
            messages.error(request, 'Error booking appointment.')
            
    is_urgent_init = request.GET.get('urgent') == '1'
    doctors = DoctorProfile.objects.all()
    return render(request, 'consultations/book.html', {'doctors': doctors, 'is_urgent_init': is_urgent_init})

@login_required
def update_appointment_status(request, pk, status):
    if request.user.role != User.Role.DOCTOR:
        return redirect('dashboard_router')
    
    appointment = get_object_or_404(Appointment, id=pk)
    if appointment.doctor.user == request.user:
        if status in [s[0] for s in Appointment.Status.choices]:
            appointment.status = status
            appointment.save()
            messages.success(request, f'Appointment marked as {status}.')
            
            # Send Notification
            from apps.notifications.models import Notification
            msg = f"Your appointment with Dr. {appointment.doctor.user.get_full_name() or appointment.doctor.user.username} has been {status.lower()}."
            notif = Notification.objects.create(
                user=appointment.patient.user,
                message=msg,
                notification_type=Notification.NotificationType.APPOINTMENT,
                action_link='/patient-dashboard/'
            )
            
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'notify_{appointment.patient.user.id}',
                    {
                        'type': 'send_notification',
                        'message': msg,
                        'count': appointment.patient.user.notifications.filter(is_read=False).count(),
                        'action': 'STANDARD'
                    }
                )
            except Exception:
                pass
    return redirect('doctor_dashboard')

@login_required
def create_medical_record(request, appt_id):
    if request.user.role != User.Role.DOCTOR:
        return redirect('dashboard_router')
        
    appointment = get_object_or_404(Appointment, id=appt_id, doctor=request.user.doctor_profile)
    
    if request.method == 'POST':
        diagnosis_text = request.POST.get('diagnosis')
        notes = request.POST.get('notes')
        
        # Medical Record
        from .models import MedicalRecord, Prescription
        record, created = MedicalRecord.objects.get_or_create(
            appointment=appointment,
            patient=appointment.patient,
            doctor=appointment.doctor,
            defaults={'diagnosis': diagnosis_text, 'notes': notes}
        )
        if not created:
            record.diagnosis = diagnosis_text
            record.notes = notes
            record.save()
            
        # Prescription parsing
        drug_name = request.POST.get('drug_name')
        if drug_name:
            dosage = request.POST.get('dosage', '')
            frequency = request.POST.get('frequency', '')
            duration = request.POST.get('duration', '')
            instructions = request.POST.get('instructions', '')
            digital_signature = request.POST.get('digital_sig') == 'on'
            
            Prescription.objects.create(
                medical_record=record,
                drug_name=drug_name,
                dosage=dosage,
                frequency=frequency,
                duration=duration,
                instructions=instructions,
                digital_signature=digital_signature
            )
            
            # Audit Logging for HIPAA
            from services.audit_logger import log_medical_action
            log_medical_action(
                user=request.user, 
                action=f"Issued E-Prescription for {drug_name}", 
                module="Prescription", 
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
        messages.success(request, 'Medical Record & E-Prescription Saved Securely.')
        return redirect('doctor_dashboard')
        
    return render(request, 'consultations/create_record.html', {'appointment': appointment})
