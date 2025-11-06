"""
Test script to verify timeout handling fixes
"""

import requests
import time

def test_timeout_handling():
    """Test that the API handles timeouts gracefully"""
    
    backend_url = "http://localhost:8000/api"
    
    # Test with the invalid claim example (should process quickly)
    test_text = """
INSURANCE CLAIM FORM

Policy Number: POL-2019-123456 (EXPIRED)
Claim Number: CLM-2024-999999
Date of Incident: March 10, 2024
Date of Claim: November 1, 2024 (LATE FILING - 8 MONTHS DELAY)

POLICYHOLDER INFORMATION:
Name: Robert Williams
Policy Holder ID: [MISSING]
Address: [INCOMPLETE ADDRESS]
Phone: 555-FAKE
Email: fake@notreal.com

INCIDENT DETAILS:
Type of Claim: Mysterious Vehicle Damage
Location: Somewhere in the city
Time of Incident: Some time at night
Weather Conditions: [NOT PROVIDED]

DESCRIPTION OF INCIDENT:
My car got damaged somehow. I think someone hit it but I'm not sure.
"""
    
    try:
        print("🧪 Testing API timeout handling...")
        print("📤 Sending request to analyze-text endpoint...")
        
        start_time = time.time()
        
        response = requests.post(
            f"{backend_url}/claims/analyze-text",
            json={
                "text": test_text,
                "claim_type": "medical_claim"
            },
            timeout=120  # 2 minute timeout
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Request successful!")
            print(f"📊 Analysis status: {result.get('document_analysis', {}).get('overall_status', 'Unknown')}")
            print(f"🎯 Confidence: {result.get('document_analysis', {}).get('confidence_level', 0)}%")
            print(f"📝 Processing notes: {result.get('document_analysis', {}).get('processing_notes', 'None')[:100]}...")
            
            # Check if it was a timeout
            if result.get('document_analysis', {}).get('overall_status') == 'TIMEOUT':
                print("⚠️  Request timed out but was handled gracefully")
            else:
                print("🚀 Request completed successfully within timeout")
                
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out at client level")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server")
        print("💡 Make sure the backend server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_timeout_handling()