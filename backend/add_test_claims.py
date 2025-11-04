#!/usr/bin/env python3
"""
Add sample claims from test-claims folder to the database
"""
import sys
import os
from datetime import datetime
import json

# Add the backend directory to the path
sys.path.append(os.path.dirname(__file__))

from utils.database import DatabaseManager

def add_test_claims():
    """Add the actual test claims from the test-claims folder to database"""
    db = DatabaseManager()
    
    # Sample claims based on the test-claims folder examples
    test_claims = [
        {
            'claim_id': 'CLM-2024-001234',
            'patient_id': 'PH-456789',
            'patient_name': 'John Michael Smith',
            'date_of_birth': '1985-06-15',  # Estimated DOB
            'policy_number': 'POL12345678',  # Using one of our sample policies
            'provider_name': 'Springfield Auto Repair',
            'provider_id': 'PROV001',
            'service_date': '2024-10-15',
            'service_type': 'Auto Accident',
            'diagnosis_code': 'V43.52XA',  # ICD-10 for car accident
            'procedure_code': 'P2850',
            'amount_billed': 2850.00
        },
        {
            'claim_id': 'CLM-2024-999999',
            'patient_id': 'PH-INVALID',
            'patient_name': 'Robert Williams',
            'date_of_birth': '1975-01-01',  # Estimated DOB
            'policy_number': 'POL87654321',  # Using expired policy for testing
            'provider_name': 'Suspicious Auto Shop',
            'provider_id': 'PROV999',
            'service_date': '2024-03-10',
            'service_type': 'Mysterious Vehicle Damage',
            'diagnosis_code': 'INVALID',
            'procedure_code': 'P45000',
            'amount_billed': 45000.00
        },
        # Additional realistic claims for better testing
        {
            'claim_id': 'CLM-2024-001235',
            'patient_id': 'PH-789123',
            'patient_name': 'Sarah Johnson',
            'date_of_birth': '1990-03-22',
            'policy_number': 'POL11111111',
            'provider_name': 'City General Hospital',
            'provider_id': 'PROV001',
            'service_date': '2024-10-25',
            'service_type': 'Emergency',
            'diagnosis_code': 'S72.001A',
            'procedure_code': 'P1234',
            'amount_billed': 1250.75
        },
        {
            'claim_id': 'CLM-2024-001236',
            'patient_id': 'PH-321654',
            'patient_name': 'Maria Garcia',
            'date_of_birth': '1988-09-14',
            'policy_number': 'POL12345678',
            'provider_name': 'Downtown Medical Center',
            'provider_id': 'PROV002',
            'service_date': '2024-10-28',
            'service_type': 'Surgery',
            'diagnosis_code': 'K80.20',
            'procedure_code': 'P5678',
            'amount_billed': 8750.00
        },
        {
            'claim_id': 'CLM-2024-001237',
            'patient_id': 'PH-654987',
            'patient_name': 'David Chen',
            'date_of_birth': '1982-12-05',
            'policy_number': 'POL87654321',
            'provider_name': 'Westside Clinic',
            'provider_id': 'PROV003',
            'service_date': '2024-10-30',
            'service_type': 'Diagnostics',
            'diagnosis_code': 'Z51.11',
            'procedure_code': 'P9876',
            'amount_billed': 485.50
        }
    ]
    
    # Add validation results for these claims
    validation_results = [
        {
            'claim_id': 'CLM-2024-001234',
            'is_valid': True,
            'issues': [],
            'recommendation': 'Approved - All documentation complete and valid',
            'total_issues': 0
        },
        {
            'claim_id': 'CLM-2024-999999',
            'is_valid': False,
            'issues': [
                {'field': 'policy_number', 'error': 'Policy expired in 2019'},
                {'field': 'filing_date', 'error': 'Filed 8 months after incident - exceeds deadline'},
                {'field': 'documentation', 'error': 'Missing police report and supporting evidence'},
                {'field': 'vin_number', 'error': 'Invalid VIN format'},
                {'field': 'amount_billed', 'error': 'Repair estimate exceeds vehicle value'}
            ],
            'recommendation': 'DENIED - Multiple critical violations: expired policy, late filing, insufficient evidence',
            'total_issues': 5
        },
        {
            'claim_id': 'CLM-2024-001235',
            'is_valid': True,
            'issues': [],
            'recommendation': 'Approved - Emergency treatment properly documented',
            'total_issues': 0
        },
        {
            'claim_id': 'CLM-2024-001236',
            'is_valid': True,
            'issues': [
                {'field': 'pre_authorization', 'error': 'Surgery requires pre-authorization verification'}
            ],
            'recommendation': 'Pending - Verify pre-authorization before final approval',
            'total_issues': 1
        },
        {
            'claim_id': 'CLM-2024-001237',
            'is_valid': True,
            'issues': [],
            'recommendation': 'Approved - Routine diagnostic procedure',
            'total_issues': 0
        }
    ]
    
    # Add AI recommendations for some claims
    recommendations = [
        {
            'claim_id': 'CLM-2024-001234',
            'recommendation': 'APPROVE',
            'confidence': 95,
            'reason': 'Complete documentation, valid policy, timely filing',
            'priority': 'low',
            'suggested_actions': ['Process payment', 'Close claim'],
            'overall_score': 9.5
        },
        {
            'claim_id': 'CLM-2024-999999',
            'recommendation': 'DENY',
            'confidence': 98,
            'reason': 'Multiple red flags: expired policy, late filing, suspicious circumstances',
            'priority': 'high',
            'suggested_actions': ['Deny claim', 'Flag for fraud investigation', 'Notify regulatory body'],
            'overall_score': 1.2
        },
        {
            'claim_id': 'CLM-2024-001236',
            'recommendation': 'REVIEW',
            'confidence': 75,
            'reason': 'Valid claim but requires pre-authorization verification',
            'priority': 'medium',
            'suggested_actions': ['Verify pre-authorization', 'Contact provider', 'Manual review'],
            'overall_score': 7.5
        }
    ]
    
    # Insert claims
    for claim in test_claims:
        try:
            db.save_claim(claim)
            print(f"✓ Added claim: {claim['claim_id']} for {claim['patient_name']}")
        except Exception as e:
            print(f"✗ Error adding claim {claim['claim_id']}: {e}")
    
    # Insert validation results
    for validation in validation_results:
        try:
            db.save_validation_result(validation['claim_id'], validation)
            print(f"✓ Added validation for: {validation['claim_id']}")
        except Exception as e:
            print(f"✗ Error adding validation {validation['claim_id']}: {e}")
    
    # Insert AI recommendations
    for rec in recommendations:
        try:
            db.save_recommendation(rec['claim_id'], rec)
            print(f"✓ Added AI recommendation for: {rec['claim_id']}")
        except Exception as e:
            print(f"✗ Error adding recommendation {rec['claim_id']}: {e}")
    
    print("\n" + "="*50)
    print("✅ Test claims data added successfully!")
    print("="*50)
    print("\nSample claims include:")
    print("• Valid auto accident claim (John Michael Smith)")
    print("• Invalid suspicious claim (Robert Williams)")  
    print("• Emergency medical claim (Sarah Johnson)")
    print("• Surgery claim needing review (Maria Garcia)")
    print("• Approved diagnostic claim (David Chen)")
    print("\nYou can now test the dashboard with realistic sample data!")

if __name__ == '__main__':
    add_test_claims()