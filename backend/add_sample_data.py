#!/usr/bin/env python3
"""
Add sample claims data to the database for testing
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add the backend directory to the path
sys.path.append(os.path.dirname(__file__))

from utils.database import DatabaseManager

def add_sample_claims():
    """Add sample claims to the database"""
    db = DatabaseManager()
    
    # Sample data
    patients = [
        ("John Doe", "1985-03-15", "JOHN001"),
        ("Jane Smith", "1990-07-22", "JANE002"), 
        ("Bob Johnson", "1978-11-05", "BOB003"),
        ("Alice Brown", "1992-01-30", "ALICE004"),
        ("Charlie Wilson", "1983-09-12", "CHARLIE005"),
        ("Diana Davis", "1995-06-08", "DIANA006"),
        ("Edward Miller", "1987-12-03", "EDWARD007"),
        ("Fiona Garcia", "1991-04-18", "FIONA008")
    ]
    
    providers = [
        ("City General Hospital", "PROV001"),
        ("Downtown Medical Center", "PROV002"),
        ("Westside Clinic", "PROV003"),
        ("Emergency Care Associates", "PROV004"),
        ("Family Health Practice", "PROV005")
    ]
    
    service_types = ["Emergency", "Surgery", "Diagnostics", "Pharmacy", "Mental Health"]
    statuses = ["submitted", "pending", "approved", "rejected", "under-review"]
    
    # Generate 20 sample claims
    for i in range(20):
        patient_name, dob, patient_id = random.choice(patients)
        provider_name, provider_id = random.choice(providers)
        
        # Generate dates within the last 90 days
        days_ago = random.randint(1, 90)
        service_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        claim_data = {
            'claim_id': f"CLM_{datetime.now().strftime('%Y%m%d')}_{i+1:03d}",
            'patient_id': patient_id,
            'patient_name': patient_name,
            'date_of_birth': dob,
            'policy_number': random.choice(['POL12345678', 'POL87654321', 'POL11111111']),
            'provider_name': provider_name,
            'provider_id': provider_id,
            'service_date': service_date,
            'service_type': random.choice(service_types),
            'diagnosis_code': f"D{random.randint(100, 999)}.{random.randint(0, 9)}",
            'procedure_code': f"P{random.randint(1000, 9999)}",
            'amount_billed': round(random.uniform(100, 5000), 2)
        }
        
        try:
            db.save_claim(claim_data)
            print(f"Added claim: {claim_data['claim_id']} for {patient_name}")
            
            # Add some validation results for variety
            if random.random() < 0.7:  # 70% chance of having validation results
                validation_result = {
                    'is_valid': random.choice([True, False]),
                    'issues': [
                        {'field': 'diagnosis_code', 'error': 'Code verification needed'},
                        {'field': 'amount', 'error': 'Amount exceeds typical range'}
                    ] if random.random() < 0.3 else [],
                    'recommendation': 'Approved for processing' if random.random() > 0.3 else 'Requires manual review',
                    'total_issues': random.randint(0, 3)
                }
                db.save_validation_result(claim_data['claim_id'], validation_result)
                print(f"  Added validation result for {claim_data['claim_id']}")
                
        except Exception as e:
            print(f"Error adding claim {claim_data['claim_id']}: {e}")
    
    print("\nSample data added successfully!")
    print("You can now test the dashboard with real data from the SQLite database.")

if __name__ == '__main__':
    add_sample_claims()