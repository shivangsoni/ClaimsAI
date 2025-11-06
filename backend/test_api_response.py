import requests
import json

def test_api_response():
    claim_id = "DOC_20251103_203114"
    url = f'http://localhost:8000/api/claims/details/{claim_id}'
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("=== API RESPONSE STRUCTURE ===")
            print(f"Has claim: {'claim' in result}")
            print(f"Has recommendations: {'recommendations' in result and len(result.get('recommendations', [])) > 0}")
            print(f"Has validations: {'validations' in result and len(result.get('validations', [])) > 0}")
            print(f"Has documents: {'documents' in result and len(result.get('documents', [])) > 0}")
            
            if 'recommendations' in result and result['recommendations']:
                rec = result['recommendations'][0]
                print(f"\n=== FIRST RECOMMENDATION ===")
                print(f"Decision: {rec.get('recommendation', 'N/A')}")
                print(f"Confidence: {rec.get('confidence', 'N/A')}")
                print(f"Overall Score: {rec.get('overall_score', 'N/A')}")
                print(f"Reason: {rec.get('reason', 'N/A')[:100]}...")
            
            if 'documents' in result and result['documents']:
                doc = result['documents'][0]
                print(f"\n=== FIRST DOCUMENT ===")
                print(f"Original: {doc.get('original_filename', 'N/A')}")
                print(f"Type: {doc.get('file_type', 'N/A')}")
                print(f"Size: {doc.get('file_size', 'N/A')}")
                print(f"Has extracted text: {'extracted_text' in doc and len(doc.get('extracted_text', '')) > 0}")
            
            return True
        else:
            print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    return False

if __name__ == "__main__":
    test_api_response()