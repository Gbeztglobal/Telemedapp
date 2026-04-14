from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Diagnosis
from services.ai_diagnosis import analyze_symptoms
from apps.accounts.models import User

@login_required
def symptom_checker(request):
    if request.user.role != User.Role.PATIENT:
        return redirect('dashboard_router')
        
    if request.method == 'POST':
        # Get symptoms from form
        symptoms_str = request.POST.get('symptoms', '')
        pain_areas = request.POST.get('pain_areas', '')
        notes = request.POST.get('notes', '')
        meds = request.POST.get('medications', '')
        
        # Combine everything for the AI analysis
        combined_report = []
        if symptoms_str: combined_report.append(f"Symptoms: {symptoms_str}")
        if pain_areas: combined_report.append(f"Pain Areas: {pain_areas}")
        if notes: combined_report.append(f"Notes: {notes}")
        if meds: combined_report.append(f"Medications: {meds}")
        
        full_symptoms_string = " | ".join(combined_report)
        symptoms_list = [s.strip() for s in symptoms_str.split(',') if s.strip()] + [p.strip() for p in pain_areas.split(',') if p.strip()]
        
        if full_symptoms_string:
            # Get patient age for age-aware drug recommendations
            patient_age = request.user.patient_profile.age  # uses the @property we added
            analysis = analyze_symptoms(symptoms_list if symptoms_list else [notes], age=patient_age)
            
            diagnosis = Diagnosis.objects.create(
                patient=request.user.patient_profile,
                symptoms_reported=full_symptoms_string,
                malaria_risk=analysis['malaria_risk'],
                cholera_risk=analysis['cholera_risk'],
                is_urgent=analysis['is_urgent'],
                drug_recommendations=analysis.get('drug_recommendations', [])
            )
            
            return redirect('diagnosis_result', pk=diagnosis.pk)
            
    return render(request, 'diagnosis/symptom_checker.html')

@login_required
def diagnosis_result(request, pk):
    try:
        diagnosis = Diagnosis.objects.get(pk=pk, patient=request.user.patient_profile)
    except Diagnosis.DoesNotExist:
        return redirect('dashboard_router')
        
    return render(request, 'diagnosis/result.html', {'diagnosis': diagnosis})
