from django.urls import path
from . import views

urlpatterns = [
    path('checker/', views.symptom_checker, name='symptom_checker'),
    path('result/<int:pk>/', views.diagnosis_result, name='diagnosis_result'),
]
