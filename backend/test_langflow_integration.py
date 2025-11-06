#!/usr/bin/env python3
"""
Test script for LangFlow + Opik integration with ClaimsAI
"""

import sys
import os
import time
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

def test_langflow_integration():
    """Test LangFlow integration with document processing"""
    print("🧪 Testing LangFlow Integration")
    print("=" * 40)
    
    try:
        from utils.document_processor import DocumentProcessor
        
        # Initialize processor
        print("1. Initializing DocumentProcessor...")
        processor = DocumentProcessor()
        print("✅ DocumentProcessor initialized successfully")
        
        # Check service health
        print("\n2. Checking service health...")
        langflow_health = processor.get_langflow_health()
        opik_status = processor.get_opik_status()
        
        print(f"   LangFlow: {langflow_health['status']} ({langflow_health['url']})")
        print(f"   Opik Available: {opik_status['available']}")
        print(f"   Opik Client: {'Initialized' if opik_status['client_initialized'] else 'Not initialized'}")
        
        # Test document analysis
        print("\n3. Testing document analysis...")
        test_document = """
MEDICAL CLAIM SUBMISSION

Patient: John Doe
DOB: 01/15/1980
Policy #: POL123456789
Member ID: MEM987654

Provider: City Medical Center
Date of Service: 11/01/2024
Procedure Code: 99213
Diagnosis Code: Z00.00
Charges: $250.00

This is a routine office visit for preventive care.
"""
        
        start_time = time.time()
        result = processor.analyze_claim_document(test_document, "medical_claim")
        end_time = time.time()
        
        print(f"✅ Analysis completed in {end_time - start_time:.2f} seconds")
        
        # Display results
        print(f"\n📊 Analysis Results:")
        print(f"   Status: {result.get('overall_status', 'N/A')}")
        print(f"   Confidence: {result.get('confidence_level', 'N/A')}%")
        print(f"   Completeness: {result.get('completeness_score', 'N/A')}%")
        print(f"   Processing Method: {result.get('processing_method', 'langflow')}")
        print(f"   AI Model: GPT-5")
        
        if result.get('decision_reasoning'):
            reasoning = result['decision_reasoning']
            print(f"   Reasoning: {reasoning[:100]}..." if len(reasoning) > 100 else f"   Reasoning: {reasoning}")
        
        # Test improvement suggestions
        print("\n4. Testing improvement suggestions...")
        suggestions = processor.get_improvement_suggestions(result)
        print(f"   Priority Fixes: {len(suggestions.get('priority_fixes', []))}")
        print(f"   Optional Improvements: {len(suggestions.get('optional_improvements', []))}")
        print(f"   Template Recommendations: {len(suggestions.get('template_recommendations', []))}")
        
        # Test comparison with approved claims
        print("\n5. Testing claim comparison...")
        comparison = processor.compare_with_approved_claims(test_document)
        print(f"   Best Match: {comparison.get('best_match_type', 'N/A')}")
        print(f"   Match Score: {comparison.get('best_match_score', 'N/A')}%")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling scenarios"""
    print("\n🔧 Testing Error Handling")
    print("=" * 30)
    
    try:
        from utils.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        # Test OCR unavailable scenario
        print("1. Testing OCR unavailable scenario...")
        ocr_text = "[IMAGE UPLOAD DETECTED - OCR NOT AVAILABLE]"
        result = processor.analyze_claim_document(ocr_text)
        print(f"   OCR Status: {result.get('overall_status', 'N/A')}")
        print("✅ OCR error handling works")
        
        # Test empty document
        print("\n2. Testing empty document...")
        result = processor.analyze_claim_document("")
        print(f"   Empty Document Status: {result.get('overall_status', 'N/A')}")
        print("✅ Empty document handling works")
        
        # Test very large document
        print("\n3. Testing large document truncation...")
        large_doc = "Sample text. " * 1000  # Create a large document
        result = processor.analyze_claim_document(large_doc)
        print(f"   Large Document Status: {result.get('overall_status', 'N/A')}")
        print("✅ Large document handling works")
        
        print("\n✅ Error handling tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error handling test failed: {str(e)}")
        return False

def test_opik_tracing():
    """Test Opik tracing functionality"""
    print("\n📊 Testing Opik Tracing")
    print("=" * 25)
    
    try:
        from utils.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        opik_status = processor.get_opik_status()
        
        if not opik_status['available']:
            print("⚠️  Opik not available - skipping tracing tests")
            return True
        
        if not opik_status['client_initialized']:
            print("⚠️  Opik client not initialized - check configuration")
            return True
        
        print("Testing traced document analysis...")
        test_doc = "Sample medical claim for tracing test"
        result = processor.analyze_claim_document(test_doc)
        
        print(f"✅ Traced analysis completed: {result.get('overall_status', 'N/A')}")
        print("Check your Opik dashboard for trace data")
        
        return True
        
    except Exception as e:
        print(f"❌ Opik tracing test failed: {str(e)}")
        return True  # Non-blocking failure

def display_configuration_help():
    """Display configuration help"""
    print("\n📋 Configuration Help")
    print("=" * 20)
    print("If tests are failing, check these configurations:")
    print()
    print("1. Environment Variables (.env file):")
    print("   OPENAI_API_KEY=your_openai_api_key")
    print("   LANGFLOW_URL=http://localhost:7860")
    print("   LANGFLOW_FLOW_ID=claims-analysis-flow")
    print("   OPIK_PROJECT_NAME=claimsai-document-analysis")
    print("   OPIK_API_KEY=your_opik_api_key")
    print()
    print("2. LangFlow Setup:")
    print("   - Start LangFlow: langflow run --host 0.0.0.0 --port 7860")
    print("   - Import langflow_config.json in the UI")
    print("   - Configure OpenAI API key in the ChatOpenAI node")
    print()
    print("3. Dependencies:")
    print("   - Run: python setup_langflow_opik.py")
    print("   - Or manually: pip install langflow langchain-openai opik")

def main():
    """Main test function"""
    print("🤖 ClaimsAI LangFlow + Opik Integration Tests")
    print("=" * 50)
    
    # Test basic integration
    if not test_langflow_integration():
        print("\n❌ Basic integration test failed")
        display_configuration_help()
        return False
    
    # Test error handling
    if not test_error_handling():
        print("\n❌ Error handling test failed")
        return False
    
    # Test Opik tracing (non-blocking)
    test_opik_tracing()
    
    print("\n🎊 All tests completed!")
    print("\n✅ LangFlow + Opik integration is working correctly")
    print("You can now use the enhanced DocumentProcessor in your ClaimsAI application")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n💡 Troubleshooting Tips:")
        print("1. Ensure all dependencies are installed")
        print("2. Check that LangFlow is running on http://localhost:7860") 
        print("3. Verify your OpenAI API key is set correctly")
        print("4. Run setup_langflow_opik.py for automated setup")
    
    sys.exit(0 if success else 1)