from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

@login_required
def list_notifications(request):
    # Fetch recent global notifications
    notifs = request.user.notifications.filter(is_read=False).order_by('-timestamp')[:10]
    unreads = request.user.notifications.filter(is_read=False).count()
    
    data = []
    for n in notifs:
        data.append({
            'id': n.id,
            'message': n.message,
            'type': n.get_notification_type_display(),
            'action_link': n.action_link
        })
        
    return JsonResponse({'unreads': unreads, 'notifications': data})

@login_required
@csrf_exempt
def mark_read(request):
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})
