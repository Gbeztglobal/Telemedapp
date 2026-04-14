from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_router, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_router, name='dashboard_router'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient/<int:patient_id>/', views.patient_medical_record, name='patient_medical_record'),
    path('logout/', views.logout_view, name='logout'),
]
