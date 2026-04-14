from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_index, name='chat_index'),
    path('room/<int:target_id>/', views.chat_room, name='chat_room'),
    path('upload/', views.upload_chat_attachment, name='upload_chat_attachment'),
]
