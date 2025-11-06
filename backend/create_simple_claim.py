import requests
import json

def create_simple_claim():
    url = 'http://localhost:8000/api/claims/submit'
    
    # Create a simple claim data
    claim_data = {
        "patient_name": "John Michael Smith",
        "patient_id": "PH-456789", 
        "policy_number": "POL-2024-789456",
        "date_of_birth": "1985-03-15",
        "service_date": "2024-10-15",
        "provider_name": "Springfield Medical Center",
        "provider_id": "DOC-789",
        "procedure_code": "99213",
        "diagnosis_code": "M25.511",
        "amount_billed": 2850.00,
        "service_type": "medical_claim"
    }
    
    try:
        print("Creating a simple claim...")
        response = requests.post(url, json=claim_data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Claim created successfully!")
            print(f"- Claim ID: {result.get('claim_id', 'N/A')}")
            print(f"- Status: {result.get('status', 'N/A')}")
            return result.get('claim_id')
        else:
            print(f"Error Response: {response.text}")
    
    except Exception as e:
        print(f"Error creating claim: {e}")
    
    return None

if __name__ == "__main__":
    claim_id = create_simple_claim()
    if claim_id:
        print(f"\n✅ Successfully created claim: {claim_id}")
        print("Now you can view it in the frontend dashboard!")
    else:
        print("\n❌ Failed to create claim")