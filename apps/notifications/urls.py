from django.urls import path
from . import views

urlpatterns = [
    path('api/list/', views.list_notifications, name='list_notifications'),
    path('api/mark-read/', views.mark_read, name='mark_notifications_read'),
]
