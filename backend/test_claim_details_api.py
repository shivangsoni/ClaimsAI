import requests
import json

# Test claim details API
claim_id = "DOC_20251103_200313"
url = f"http://localhost:5000/api/claims/details/{claim_id}"

print(f"Testing claim details for: {claim_id}")

try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        
        print("=== CLAIM DETAILS ===")
        claim = data.get('claim', {})
        print(f"Patient: {claim.get('patient_name')}")
        print(f"Amount: ${claim.get('amount_billed')}")
        print(f"Service Type: {claim.get('service_type')}")
        
        print("\n=== RECOMMENDATIONS ===")
        recommendations = data.get('recommendations', [])
        print(f"Found {len(recommendations)} recommendations")
        
        for i, rec in enumerate(recommendations):
            print(f"\nRecommendation {i+1}:")
            print(f"  Decision: {rec.get('recommendation')}")
            print(f"  Confidence: {rec.get('confidence')}%")
            print(f"  Overall Score: {rec.get('overall_score')}%")
            print(f"  Reasoning: {rec.get('reason', 'No reasoning')[:200]}...")
            
        print("\n=== VALIDATIONS ===")
        validations = data.get('validations', [])
        print(f"Found {len(validations)} validations")
        
        for i, val in enumerate(validations):
            print(f"\nValidation {i+1}:")
            print(f"  Valid: {val.get('is_valid')}")
            print(f"  Recommendation: {val.get('recommendation')}")
            print(f"  Issues: {val.get('total_issues')}")
            
        print("\n=== FULL JSON STRUCTURE ===")
        print(json.dumps(data, indent=2))
        
    else:
        print(f"Error: {response.status_code} - {response.text}")
        
except Exception as e:
    print(f"Error: {e}")