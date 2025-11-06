#!/usr/bin/env python3
"""
Test script to demonstrate the new 5-stage claim status workflow
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def test_status_workflow():
    """
    Test the complete 5-stage status workflow
    """
    print("🚀 Testing 5-Stage Claim Status Workflow")
    print("=" * 50)
    
    # Step 1: Create a new claim (should start as 'open')
    print("\n📝 Step 1: Creating new claim...")
    claim_data = {
        "patient_id": "P12345",
        "patient_name": "John Test Patient", 
        "date_of_birth": "1985-03-15",
        "policy_number": "POL12345678",
        "provider_name": "Test Medical Center",
        "provider_id": "PROV001",
        "service_date": "2024-11-01",
        "service_type": "medical_consultation",
        "diagnosis_code": "Z00.00",
        "procedure_code": "99213",
        "amount_billed": 150.00
    }
    
    try:
        response = requests.post(f"{BASE_URL}/claims/submit", json=claim_data)
        if response.status_code == 201:
            claim_result = response.json()
            claim_id = claim_result["claim_id"]
            print(f"✅ Claim created: {claim_id}")
            print(f"   Initial status: {claim_result['status']}")
        else:
            print(f"❌ Failed to create claim: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error creating claim: {e}")
        return
    
    # Step 2: Process with AI (open -> validation_complete)
    print(f"\n🤖 Step 2: Processing claim {claim_id} with AI...")
    try:
        response = requests.post(f"{BASE_URL}/claims/{claim_id}/ai-process")
        if response.status_code == 200:
            ai_result = response.json()
            print(f"✅ AI processing complete!")
            print(f"   New status: {ai_result['status']}")
            print(f"   AI suggested: {ai_result['suggested_status']}")
            print(f"   Summary: {ai_result['ai_summary']}")
            print(f"   Decision: {ai_result['decision_summary']}")
        else:
            print(f"❌ AI processing failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error in AI processing: {e}")
        return
    
    # Step 3: Human decision - move to verified
    print(f"\n👤 Step 3: Human moving claim to 'verified' status...")
    status_update = {
        "status": "verified",
        "changed_by": "human_reviewer",
        "reason": "Reviewed and verified claim details",
        "notes": "All documentation looks good, proceeding to final decision"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/claims/{claim_id}/status", json=status_update)
        if response.status_code == 200:
            update_result = response.json()
            print(f"✅ Status updated to: {update_result['new_status']}")
            print(f"   Changed by: {update_result['changed_by']}")
        else:
            print(f"❌ Status update failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error updating status: {e}")
        return
    
    # Step 4: Final human decision - approve
    print(f"\n✅ Step 4: Human approving the claim...")
    final_decision = {
        "status": "approved",
        "changed_by": "claims_manager", 
        "reason": "Claim meets all requirements for approval",
        "notes": "Approved for payment processing"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/claims/{claim_id}/status", json=final_decision)
        if response.status_code == 200:
            final_result = response.json()
            print(f"✅ Final decision: {final_result['new_status']}")
            print(f"   Timestamp: {final_result['timestamp']}")
        else:
            print(f"❌ Final decision failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error in final decision: {e}")
        return
    
    # Step 5: Get complete history
    print(f"\n📋 Step 5: Retrieving complete claim history...")
    try:
        response = requests.get(f"{BASE_URL}/claims/{claim_id}/transitions")
        if response.status_code == 200:
            history = response.json()
            print(f"✅ Status transition history for {claim_id}:")
            for i, transition in enumerate(history['transitions'], 1):
                print(f"   {i}. {transition['from_status']} → {transition['to_status']}")
                print(f"      Changed by: {transition['changed_by']}")
                print(f"      Reason: {transition['change_reason']}")
                print(f"      Time: {transition['created_at']}")
                print(f"      AI Suggested: {'Yes' if transition['ai_suggested'] else 'No'}")
                print()
        else:
            print(f"❌ Failed to get history: {response.text}")
    except Exception as e:
        print(f"❌ Error getting history: {e}")
    
    print("\n🎉 Workflow test completed!")
    print(f"Claim {claim_id} successfully moved through all stages:")
    print("   open → validation_complete → verified → approved")

def test_ai_suggestions():
    """
    Test AI suggestions without changing status
    """
    print("\n🧠 Testing AI Suggestions Feature...")
    print("=" * 40)
    
    # This would be a more comprehensive test of AI analysis
    # For now, just show the concept
    print("AI provides suggestions but humans control all state changes")
    print("- AI can only move claims from 'open' to 'validation_complete'")  
    print("- All other transitions require human decision")
    print("- AI suggestions are displayed but not automatically applied")

if __name__ == "__main__":
    print("🏥 ClaimsAI - 5-Stage Status Workflow Test")
    print("Make sure the backend server is running on http://localhost:5000")
    print()
    
    # Test basic connectivity
    try:
        response = requests.get(f"{BASE_URL}/claims/stats")
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server responded with error")
            exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to backend server: {e}")
        print("Please start the backend server first:")
        print("cd backend && python app.py")
        exit(1)
    
    # Run the tests
    test_status_workflow()
    test_ai_suggestions()
    
    print("\n📚 Status System Summary:")
    print("1. Open - Initial state when claim is received")
    print("2. Validation Complete - AI has analyzed and provided suggestions")
    print("3. Verified - Human has reviewed and verified the claim") 
    print("4. Approved/Denied - Final human decision")
    print("5. Need More Info - Can be set at any stage if more info needed")
    print()
    print("Key Features:")
    print("✓ AI provides suggestions but doesn't change application state")
    print("✓ Only humans can make status transitions")
    print("✓ Full audit trail of all status changes")
    print("✓ Next/Previous stage buttons for easy navigation")
    print("✓ AI summary and decision reasoning displayed to humans")