from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.accounts.models import User
from .models import Message
from django.db.models import Q

@login_required
def chat_room(request, target_id):
    target_user = get_object_or_404(User, id=target_id)
    
    # Sort IDs so the room name is always consistent between these two users
    ids = sorted([request.user.id, target_user.id])
    room_name = f"{ids[0]}_{ids[1]}"
    
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=target_user) | 
        Q(sender=target_user, receiver=request.user)
    ).order_by('timestamp')
    
    return render(request, 'messaging/room.html', {
        'target_user': target_user,
        'room_name': room_name,
        'chat_messages': messages
    })

@login_required
def chat_index(request):
    from apps.accounts.models import DoctorProfile, PatientProfile
    
    contacts = []
    if request.user.role == User.Role.PATIENT:
        # Get doctors they have booked with
        doctors = DoctorProfile.objects.filter(appointments__patient__user=request.user).distinct()
        if not doctors.exists():
            doctors = DoctorProfile.objects.all()[:10]
        
        for d in doctors:
            contacts.append({
                'user_id': d.user.id,
                'name': f"Dr. {d.user.get_full_name() or d.user.username}",
                'subtitle': d.specialty,
                'avatar': d.get_avatar_url()
            })
    else:
        patients = PatientProfile.objects.filter(appointments__doctor__user=request.user).distinct()
        if not patients.exists():
            patients = PatientProfile.objects.all()[:10]
            
        for p in patients:
            contacts.append({
                'user_id': p.user.id,
                'name': p.user.get_full_name() or p.user.username,
                'subtitle': "Patient",
                'avatar': p.get_avatar_url()
            })
            
    return render(request, 'messaging/index.html', {'contacts': contacts})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def upload_chat_attachment(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        receiver = User.objects.get(id=receiver_id)
        
        msg = Message.objects.create(sender=request.user, receiver=receiver)
        
        if 'attachment' in request.FILES:
            msg.attachment = request.FILES['attachment']
        if 'audio_note' in request.FILES:
            msg.audio_note = request.FILES['audio_note']
            
        msg.save()
        
        # In a real app we'd trigger a channel group send here or the JS will trigger it
        return JsonResponse({'status': 'success', 'msg_id': msg.id, 'attachment_url': msg.attachment.url if msg.attachment else None, 'audio_url': msg.audio_note.url if msg.audio_note else None})
    return JsonResponse({'status': 'error'})
