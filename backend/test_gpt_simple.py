import requests
import json

# Test GPT-4 with simple text
url = 'http://localhost:8000/api/claims/analyze-text'
sample_text = '''
MEDICAL CLAIM FORM

Patient Information:
Name: John Smith  
DOB: 1985-05-15
Patient ID: P123456
Policy Number: POL-12345

Provider Information:
Provider: City Medical Center
Service Date: 2025-11-03
Diagnosis: Routine checkup (Z00.00)
Procedure: Office visit (99213)  
Amount: $250.00

This claim is for a routine annual physical examination.
'''

data = {'text': sample_text, 'claim_type': 'medical_claim'}
print('Testing GPT-4 analysis...')

try:
    response = requests.post(url, json=data, timeout=60)
    print(f'Status Code: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        analysis = result.get('document_analysis', {})
        print(f'Decision: {analysis.get("overall_status")}')
        print(f'Confidence: {analysis.get("confidence_level")}%')
        
        reasoning = analysis.get('decision_reasoning')
        if reasoning:
            print(f'Reasoning: {reasoning}')
        
        if analysis.get('processing_notes'):
            print(f'Notes: {analysis.get("processing_notes")}')
            
        # Print full response for debugging
        print('\\nFull Analysis:')
        print(json.dumps(analysis, indent=2))
    else:
        print(f'Error Response: {response.text}')
        
except Exception as e:
    print(f'Exception: {e}')