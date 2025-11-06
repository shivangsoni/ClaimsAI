import requests
import json

def test_claim_details(claim_id):
    url = f'http://localhost:8000/api/claims/details/{claim_id}'
    
    try:
        print(f"Getting details for claim: {claim_id}")
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n=== CLAIM DETAILS ===")
            if 'claim' in result:
                claim = result['claim']
                print(f"Patient: {claim.get('patient_name', 'N/A')}")
                print(f"Claim ID: {claim.get('claim_id', 'N/A')}")
                print(f"Status: {claim.get('status', 'N/A')}")
            
            print(f"\n=== RECOMMENDATIONS ===")
            if 'recommendations' in result and result['recommendations']:
                for i, rec in enumerate(result['recommendations']):
                    print(f"Recommendation {i+1}:")
                    print(f"  Decision: {rec.get('recommendation', 'N/A')}")
                    print(f"  Confidence: {rec.get('confidence', 'N/A')}%")
                    print(f"  Overall Score: {rec.get('overall_score', 'N/A')}%")
                    print(f"  Reasoning: {rec.get('reason', 'N/A')[:100]}...")
            else:
                print("No recommendations found")
            
            print(f"\n=== VALIDATIONS ===")
            if 'validations' in result and result['validations']:
                for i, val in enumerate(result['validations']):
                    print(f"Validation {i+1}:")
                    print(f"  Valid: {val.get('is_valid', 'N/A')}")
                    print(f"  Recommendation: {val.get('recommendation', 'N/A')}")
                    print(f"  Issues: {val.get('total_issues', 'N/A')}")
            else:
                print("No validations found")
                
            return True
        else:
            print(f"Error Response: {response.text}")
    
    except Exception as e:
        print(f"Error getting claim details: {e}")
    
    return False

if __name__ == "__main__":
    # Test the claim that we know has GPT-4 analysis
    test_claim_details("DOC_20251103_200313")