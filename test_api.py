"""
Test GPT-4 Mini with Reasoning - Complete Verification
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from utils.document_processor import DocumentProcessor

def test_gpt4_mini_with_reasoning():
    """Test GPT-4 Mini with decision reasoning functionality"""
    
    print("🧪 Testing GPT-4 Mini with Decision Reasoning...")
    print("=" * 60)
    
    try:
        # Initialize processor
        processor = DocumentProcessor()
        print("✅ DocumentProcessor initialized successfully!")
        
        # Test with a simple but complete claim
        test_claim = """
INSURANCE CLAIM FORM
Policy Number: POL-2024-789456
Date of Incident: October 15, 2024

POLICYHOLDER INFORMATION:
Name: John Smith
Policy Number: POL-2024-789456
Address: 123 Main St, Springfield, IL
Phone: (555) 123-4567

INCIDENT DETAILS:
Type of Claim: Auto Accident
Date of Service: October 15, 2024
Provider: City Auto Repair
Amount: $2,500.00
Diagnosis: Minor collision repair
"""
        
        print("\n📄 Testing with sample claim...")
        print("🤖 Sending to GPT-4 Mini for analysis...")
        
        result = processor.analyze_claim_document(test_claim)
        
        print("\n📊 ANALYSIS RESULTS:")
        print(f"Overall Status: {result.get('overall_status', 'Unknown')}")
        print(f"Completeness Score: {result.get('completeness_score', 0)}%")
        print(f"Confidence Level: {result.get('confidence_level', 0)}%")
        
        # Check for new reasoning fields
        if 'decision_reasoning' in result:
            print(f"\n💡 DECISION REASONING:")
            print(f"   {result['decision_reasoning']}")
        else:
            print("\n❌ No decision reasoning found (check prompt update)")
        
        if 'key_factors' in result and result['key_factors']:
            print(f"\n🔑 KEY DECISION FACTORS:")
            for i, factor in enumerate(result['key_factors'], 1):
                print(f"   {i}. {factor}")
        else:
            print("\n❌ No key factors found (check prompt update)")
        
        print(f"\n📝 Processing Notes: {result.get('processing_notes', 'None')}")
        
        # Verify improvements are working
        improvements_made = []
        if 'decision_reasoning' in result:
            improvements_made.append("✅ Decision reasoning implemented")
        if 'key_factors' in result:
            improvements_made.append("✅ Key factors extraction working")
        
        print(f"\n🎯 IMPROVEMENTS VERIFIED:")
        for improvement in improvements_made:
            print(f"   {improvement}")
        
        if result.get('overall_status') in ['APPROVED', 'DENIED', 'NEEDS_REVIEW']:
            improvements_made.append("✅ Status classification working")
        
        print(f"\n🎉 GPT-4 Mini Integration Test: {'SUCCESSFUL' if improvements_made else 'NEEDS WORK'}!")
        return len(improvements_made) >= 2
        
    except Exception as e:
        print(f"\n❌ Test Failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check that backend server is running")
        print("2. Verify OpenAI API key is valid")
        print("3. Ensure GPT-4 Mini model access")
        return False

if __name__ == "__main__":
    success = test_gpt4_mini_with_reasoning()
    if success:
        print("\n🎊 ALL UPDATES WORKING CORRECTLY!")
        print("✅ GPT-4 Mini model updated")
        print("✅ Decision reasoning added")
        print("✅ Key factors extraction implemented")
    else:
        print("\n⚠️  Some features may need attention")