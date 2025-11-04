import requests
import os

# Test document upload to trigger GPT-4 analysis
def test_document_upload():
    url = 'http://localhost:5000/api/claims/upload'
    
    # Check if test file exists
    test_file_path = r'c:\Users\shison\source\repos\ClaimsAI\ClaimsAI\test-claims\valid_claim_example.txt'
    
    if not os.path.exists(test_file_path):
        print(f"Test file not found: {test_file_path}")
        return
    
    # Upload the file
    try:
        with open(test_file_path, 'rb') as f:
            files = {'document': f}
            data = {'claim_type': 'medical_claim'}
            response = requests.post(url, files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            if 'claim_id' in result:
                print(f"Claim created with ID: {result['claim_id']}")
                return result['claim_id']
    
    except Exception as e:
        print(f"Error uploading document: {e}")
    
    return None

if __name__ == "__main__":
    claim_id = test_document_upload()
    if claim_id:
        print(f"Successfully uploaded document and created claim: {claim_id}")
    else:
        print("Failed to upload document")