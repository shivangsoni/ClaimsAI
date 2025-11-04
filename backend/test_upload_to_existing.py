import requests
import os

def test_upload_to_existing_claim():
    """Test uploading document to an existing claim"""
    
    claim_id = "CLM_20251103_203506"
    url = f'http://localhost:5000/api/claims/{claim_id}/upload'
    
    # Check if test file exists
    test_file_path = r'c:\Users\shison\source\repos\ClaimsAI\ClaimsAI\test-claims\valid_claim_example.txt'
    
    if not os.path.exists(test_file_path):
        print(f"Test file not found: {test_file_path}")
        return False
    
    try:
        print(f"Uploading document to existing claim: {claim_id}")
        
        with open(test_file_path, 'rb') as f:
            files = {'document': f}
            data = {'claim_type': 'medical_claim'}
            response = requests.post(url, files=files, data=data, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document uploaded and analyzed successfully!")
            print(f"- Claim ID: {result.get('claim_id', 'N/A')}")
            print(f"- Status: {result.get('status', 'N/A')}")
            
            # Check GPT-4 analysis
            if 'document_analysis' in result:
                analysis = result['document_analysis']
                print(f"- GPT-4 Decision: {analysis.get('overall_status', 'N/A')}")
                print(f"- Confidence: {analysis.get('confidence_level', 'N/A')}%")
                print(f"- Completeness: {analysis.get('completeness_score', 'N/A')}%")
            
            return True
        else:
            print(f"❌ Error Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error uploading document: {e}")
        return False

if __name__ == "__main__":
    success = test_upload_to_existing_claim()
    if success:
        print(f"\n🎉 Document uploaded successfully! Now check the claim in the frontend.")
    else:
        print(f"\n💥 Document upload failed.")