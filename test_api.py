#!/usr/bin/env python3
"""
Quick test script to verify OpenAI integration is working
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from utils.document_processor import DocumentProcessor

def test_document_analysis():
    """Test the document analysis with a sample claim text"""
    
    print("🔍 Testing ClaimsAI Document Processing...")
    print("=" * 50)
    
    try:
        # Initialize processor
        processor = DocumentProcessor()
        print("✅ DocumentProcessor initialized successfully!")
        
        # Sample claim text for testing
        sample_claim = """
        MEDICAL CLAIM SUBMISSION
        
        Patient: John Doe
        Date of Birth: 1980-05-15
        Policy Number: POL98765
        
        Service Date: 2024-11-01
        Provider: City Medical Center
        Diagnosis: Routine checkup
        Amount: $250.00
        """
        
        print("\n📄 Testing with sample claim text...")
        print(f"Sample text: {sample_claim[:100]}...")
        
        # Analyze the document
        print("\n🤖 Sending to GPT-4 for analysis...")
        result = processor.analyze_claim_document(sample_claim)
        
        print("\n📊 ANALYSIS RESULTS:")
        print(f"Overall Status: {result.get('overall_status', 'Unknown')}")
        print(f"Completeness Score: {result.get('completeness_score', 0)}%")
        print(f"Confidence Level: {result.get('confidence_level', 0)}%")
        
        missing = result.get('missing_sections', [])
        if missing:
            print(f"\n❌ Missing Sections: {', '.join(missing)}")
        
        found = result.get('found_sections', [])
        if found:
            print(f"\n✅ Found Sections: {', '.join(found)}")
        
        recommendations = result.get('recommendations', [])
        if recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"   {i}. {rec}")
        
        print("\n🎉 GPT-4 Integration Test: SUCCESSFUL!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test Failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check that your OpenAI API key is valid")
        print("2. Ensure you have sufficient OpenAI credits")
        print("3. Verify internet connection")
        return False

if __name__ == "__main__":
    test_document_analysis()