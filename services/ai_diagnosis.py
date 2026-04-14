def recommend_drugs(malaria_risk, cholera_risk, age):
    """
    Returns age-appropriate drug recommendations based on risk levels.
    WHO/clinical guidelines adapted for malaria & cholera treatment.
    """
    drugs = []

    # ---------- MALARIA ----------
    if malaria_risk in ['High', 'Critical']:
        if age is None or age >= 14:
            drugs.append({
                'condition': 'Malaria (High Risk)',
                'drug': 'Artemether-Lumefantrine (Coartem)',
                'dose': '4 tablets twice daily for 3 days',
                'notes': 'Take with food or milk to enhance absorption. Complete full course.'
            })
            drugs.append({
                'condition': 'Malaria – Supportive',
                'drug': 'Paracetamol 500mg',
                'dose': '2 tablets every 6 hours as needed',
                'notes': 'For fever and headache relief. Do not exceed 8 tablets per day.'
            })
        elif age >= 5:
            drugs.append({
                'condition': 'Malaria (High Risk – Child)',
                'drug': 'Artemether-Lumefantrine Pediatric Suspension',
                'dose': 'Based on weight: 5–14 kg → 1 tablet; 15–24 kg → 2 tablets twice daily for 3 days',
                'notes': 'Must be taken with food. Consult doctor for exact weight-based dosing.'
            })
            drugs.append({
                'condition': 'Malaria – Supportive',
                'drug': 'Paracetamol Syrup (120mg/5ml)',
                'dose': '15 mg/kg per dose, every 6 hours as needed',
                'notes': 'For fever management. Do not use adult tablets for children.'
            })
        else:
            # Infants < 5 years
            drugs.append({
                'condition': 'Malaria (High Risk – Infant)',
                'drug': 'Quinine Syrup + Clindamycin',
                'dose': 'Quinine 10mg/kg every 8 hours for 7 days',
                'notes': '⚠ URGENT: Infants must be seen by a doctor immediately. This is a provisional recommendation only.'
            })

    elif malaria_risk == 'Medium':
        drugs.append({
            'condition': 'Malaria (Moderate Risk – Prevention)',
            'drug': 'Chloroquine Phosphate',
            'dose': '500mg weekly (Adults) / 8.3mg/kg weekly (Children)',
            'notes': 'Preventive/prophylactic course. Confirm with a physician if symptoms worsen.'
        })

    # ---------- CHOLERA ----------
    if cholera_risk in ['High', 'Critical']:
        drugs.append({
            'condition': 'Cholera (High Risk)',
            'drug': 'Oral Rehydration Salts (ORS)',
            'dose': '200–400ml after every loose stool (Adults) / 50–100ml/kg over 4hrs (Children)',
            'notes': 'FIRST-LINE treatment. Begin IMMEDIATELY. Do not wait for lab confirmation.'
        })
        if age is None or age >= 8:
            drugs.append({
                'condition': 'Cholera – Antibiotic',
                'drug': 'Doxycycline 300mg',
                'dose': 'Single oral dose (Adults only, 8+ years)',
                'notes': 'Reduces duration of illness. Not recommended for pregnant women or children under 8.'
            })
        else:
            drugs.append({
                'condition': 'Cholera – Antibiotic (Child)',
                'drug': 'Azithromycin 20mg/kg',
                'dose': 'Single oral dose (max 1g)',
                'notes': 'Preferred antibiotic for children and pregnant women. Consult a doctor.'
            })
        drugs.append({
            'condition': 'Cholera – Zinc Supplementation',
            'drug': 'Zinc Sulfate',
            'dose': '20mg/day for 10–14 days (Adults) / 10mg/day < 6 months',
            'notes': 'Reduces duration and severity of diarrhea. Especially critical for children.'
        })

    elif cholera_risk == 'Medium':
        drugs.append({
            'condition': 'Cholera (Moderate – Rehydration)',
            'drug': 'ORS + Zinc',
            'dose': 'ORS as directed on packet, Zinc 20mg/day for 10 days',
            'notes': 'Monitor fluid intake. Increase ORS if symptoms worsen.'
        })

    # ---------- GENERAL ----------
    if not drugs:
        drugs.append({
            'condition': 'Low Risk – General Wellness',
            'drug': 'No prescription drugs required at this time.',
            'dose': 'Stay hydrated. Monitor symptoms.',
            'notes': 'If symptoms persist for more than 48 hours, consult a healthcare provider.'
        })

    return drugs


def analyze_symptoms(symptoms_list, age=None):
    """
    Evaluates a list of string symptoms and returns a risk profile
    for Malaria and Cholera, plus age-aware drug recommendations.
    """
    symptoms = [s.lower() for s in symptoms_list]

    malaria_indicators = ['fever', 'chills', 'sweats', 'headache', 'nausea', 'vomiting', 'body ache', 'fatigue']
    cholera_indicators = ['severe diarrhea', 'watery diarrhea', 'vomiting', 'leg cramps', 'dehydration', 'rapid heart rate']

    malaria_score = sum(1 for ind in malaria_indicators if any(ind in sym for sym in symptoms))
    cholera_score = sum(1 for ind in cholera_indicators if any(ind in sym for sym in symptoms))

    def calculate_risk(score, total):
        pct = (score / total) * 100 if total > 0 else 0
        if pct >= 75: return "Critical"
        elif pct >= 50: return "High"
        elif pct >= 25: return "Medium"
        return "Low"

    malaria_risk = calculate_risk(malaria_score, len(malaria_indicators))
    cholera_risk = calculate_risk(cholera_score, len(cholera_indicators))
    is_urgent = malaria_risk in ["High", "Critical"] or cholera_risk in ["High", "Critical"]

    drugs = recommend_drugs(malaria_risk, cholera_risk, age)

    return {
        "malaria_risk": malaria_risk,
        "cholera_risk": cholera_risk,
        "is_urgent": is_urgent,
        "drug_recommendations": drugs
    }
