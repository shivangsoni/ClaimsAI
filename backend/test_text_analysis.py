import requests
import json
import os

def test_text_analysis():
    url = 'http://localhost:8000/api/claims/analyze-text'
    
    # Read the test claim text
    test_file_path = r'c:\Users\shison\source\repos\ClaimsAI\ClaimsAI\test-claims\valid_claim_example.txt'
    
    if not os.path.exists(test_file_path):
        print(f"Test file not found: {test_file_path}")
        return
    
    # Read the text content
    with open(test_file_path, 'r', encoding='utf-8') as f:
        claim_text = f.read()
    
    # Prepare the request data
    data = {
        'text': claim_text,
        'claim_type': 'medical_claim'
    }
    
    try:
        print("Sending claim text for GPT-4 analysis...")
        response = requests.post(url, json=data, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("GPT-4 Analysis Results:")
            print(f"- Status: {result.get('status', 'N/A')}")
            
            # Check if analysis_result exists
            if 'analysis_result' in result:
                analysis = result['analysis_result']
                print(f"- Overall Status: {analysis.get('overall_status', 'N/A')}")
                print(f"- Completeness Score: {analysis.get('completeness_score', 'N/A')}%")
                print(f"- Confidence Level: {analysis.get('confidence_level', 'N/A')}%")
                print(f"- Decision: {analysis.get('decision_reasoning', 'N/A')}")
            
            # Check if a claim was created
            if 'claim_id' in result:
                print(f"- Claim ID Created: {result['claim_id']}")
                return result['claim_id']
        else:
            print(f"Error Response: {response.text}")
    
    except Exception as e:
        print(f"Error in text analysis: {e}")
    
    return None

if __name__ == "__main__":
    claim_id = test_text_analysis()
    if claim_id:
        print(f"\n✅ Successfully analyzed text and created claim: {claim_id}")
    else:
        print("\n❌ Failed to analyze text")