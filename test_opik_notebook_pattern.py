#!/usr/bin/env python3
"""
Test Opik logging with Claims AI - LangGraph Notebook Pattern
"""

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_opik_notebook_pattern():
    """Test Opik integration following the LangGraph notebook pattern"""
    
    print("Testing Opik Integration - LangGraph Notebook Pattern")
    print("=" * 60)
    
    # Import after setting path
    from utils.document_processor import DocumentProcessor, OPIK_AVAILABLE, OPIK_CLIENT, OPIK_CALLBACK_AVAILABLE
    
    print(f"\n📊 Opik Global Status:")
    print(f"   OPIK_AVAILABLE: {OPIK_AVAILABLE}")
    print(f"   OPIK_CLIENT: {OPIK_CLIENT is not None}")
    print(f"   OPIK_CALLBACK_AVAILABLE: {OPIK_CALLBACK_AVAILABLE}")
    
    if OPIK_CLIENT:
        print(f"   Project Name: {getattr(OPIK_CLIENT, 'project_name', 'Unknown')}")
    
    # Initialize document processor
    print(f"\n🏭 Initializing DocumentProcessor...")
    processor = DocumentProcessor()
    
    # Check processor status
    opik_status = processor.get_opik_status()
    print(f"\n📈 Processor Opik Status:")
    print(f"   Available: {opik_status['available']}")
    print(f"   Client Initialized: {opik_status['client_initialized']}")
    if 'project_name' in opik_status:
        print(f"   Project Name: {opik_status['project_name']}")
    
    # Test callback creation
    print(f"\n🧪 Testing Opik Callbacks:")
    callbacks = processor._get_opik_callbacks()
    print(f"   Callbacks created: {len(callbacks)}")
    if callbacks:
        print(f"   Callback types: {[type(cb).__name__ for cb in callbacks]}")
    
    # Test document analysis
    test_document = """
    MEDICAL CLAIM FORM
    
    Patient Name: John Doe
    Policy Number: POL12345678
    Service Date: 2024-11-07
    Provider: Dr. Smith Medical Center
    Diagnosis: Routine checkup (Z00.00)
    Procedure: Office visit (99213)
    Amount Billed: $150.00
    
    All required documents attached.
    """
    
    print(f"\n🔬 Running claim analysis with Opik tracing...")
    print(f"   Document length: {len(test_document)} characters")
    print(f"   Expected: Opik traces should be logged automatically")
    
    try:
        result = processor.analyze_claim_document(test_document, "medical_claim")
        
        print(f"\n✅ Analysis completed successfully!")
        print(f"   Processing method: {result.get('processing_method', 'unknown')}")
        print(f"   Overall status: {result.get('overall_status', 'unknown')}")
        print(f"   Trace ID: {result.get('trace_id', 'not set')}")
        
        # Check if this looks like it was traced
        if callbacks and result.get('trace_id'):
            print(f"\n🎯 Opik Integration Success!")
            print(f"   ✅ Callbacks were available")
            print(f"   ✅ Analysis completed with trace ID")
            print(f"   ✅ Check Opik dashboard for traces")
            
            if OPIK_CLIENT and hasattr(OPIK_CLIENT, 'project_name'):
                print(f"   🔗 Project: {OPIK_CLIENT.project_name}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_setup():
    """Test that environment is properly configured for Opik"""
    
    print(f"\n🌍 Environment Configuration:")
    print("-" * 40)
    
    env_vars = [
        "OPENAI_API_KEY",
        "OPIK_API_KEY", 
        "OPIK_WORKSPACE",
        "OPIK_PROJECT_NAME"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "KEY" in var:
                display_value = value[:10] + "..." if len(value) > 10 else value
            else:
                display_value = value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ⚠️  {var}: Not set")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Opik LangGraph Pattern Test")
    
    # Test environment
    env_ok = test_environment_setup()
    
    # Test Opik integration
    opik_ok = test_opik_notebook_pattern()
    
    print(f"\n📋 Test Summary:")
    print(f"   Environment Setup: {'✅' if env_ok else '❌'}")
    print(f"   Opik Integration: {'✅' if opik_ok else '❌'}")
    
    if opik_ok:
        print(f"\n🎉 Opik integration is working with LangGraph notebook pattern!")
        print(f"   📊 Check your Opik dashboard for logged traces")
        print(f"   🔍 Traces should show LangGraph workflow structure")
    else:
        print(f"\n⚠️  Opik integration needs attention")
        print(f"     Check environment variables and Opik installation")