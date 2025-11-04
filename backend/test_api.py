#!/usr/bin/env python3
"""
Test the Claims API endpoints
"""
import requests
import json

base_url = "http://localhost:5000/api"

def test_api():
    print("🧪 Testing ClaimsAI Backend API")
    print("=" * 40)
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/status", timeout=5)
        if response.status_code == 200:
            print("✅ Health check: PASSED")
        else:
            print(f"❌ Health check: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Health check: ERROR - {e}")
    
    # Test claims stats
    try:
        response = requests.get(f"{base_url}/claims/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Claims stats: PASSED")
            print(f"   Total claims: {data.get('total_claims', 0)}")
            print(f"   Status distribution: {data.get('status_distribution', {})}")
        else:
            print(f"❌ Claims stats: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Claims stats: ERROR - {e}")
    
    # Test claims list
    try:
        response = requests.get(f"{base_url}/claims/list?per_page=3", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Claims list: PASSED")
            print(f"   Claims returned: {len(data.get('claims', []))}")
            if data.get('claims'):
                first_claim = data['claims'][0]
                print(f"   Sample claim: {first_claim.get('patient_name')} - {first_claim.get('claim_id')}")
        else:
            print(f"❌ Claims list: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Claims list: ERROR - {e}")
    
    # Test specific claim details
    try:
        response = requests.get(f"{base_url}/claims/details/CLM-2024-001234", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Claim details: PASSED")
            print(f"   Patient: {data.get('claim', {}).get('patient_name')}")
            print(f"   Validations: {len(data.get('validations', []))}")
            print(f"   Recommendations: {len(data.get('recommendations', []))}")
        else:
            print(f"❌ Claim details: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Claim details: ERROR - {e}")
    
    print("\n🎯 API Integration Test Complete!")

if __name__ == '__main__':
    test_api()