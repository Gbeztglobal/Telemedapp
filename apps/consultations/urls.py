from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_appointment, name='book_appointment'),
    path('call/<str:room_name>/', views.video_call_room, name='video_call_room'),
    path('update/<int:pk>/<str:status>/', views.update_appointment_status, name='update_appointment_status'),
    path('record/create/<int:appt_id>/', views.create_medical_record, name='create_medical_record'),
]
