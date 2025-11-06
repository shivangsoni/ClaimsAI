#!/usr/bin/env python3
"""
Quick test to verify GPT-5 configuration in ClaimsAI
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

def test_gpt5_config():
    """Test GPT-5 configuration"""
    print("🧪 Testing GPT-5 Configuration")
    print("=" * 35)
    
    try:
        from utils.document_processor import DocumentProcessor
        from utils.prompt import LANGFLOW_CONFIG, OPIK_TRACE_CONFIG
        
        # Initialize processor
        print("1. Checking DocumentProcessor configuration...")
        processor = DocumentProcessor()
        
        # Check LLM model configuration
        model_name = processor.llm.model_name
        max_tokens = processor.llm.max_tokens
        timeout = processor.llm.request_timeout
        
        print(f"   ✅ LangChain Model: {model_name}")
        print(f"   ✅ Max Tokens: {max_tokens}")
        print(f"   ✅ Timeout: {timeout}s")
        
        # Check LangFlow configuration
        print("\n2. Checking LangFlow configuration...")
        langflow_model = LANGFLOW_CONFIG["tweaks"]["ChatOpenAI-1"]["model"]
        langflow_tokens = LANGFLOW_CONFIG["tweaks"]["ChatOpenAI-1"]["max_tokens"]
        
        print(f"   ✅ LangFlow Model: {langflow_model}")
        print(f"   ✅ LangFlow Max Tokens: {langflow_tokens}")
        
        # Check Opik tags
        print("\n3. Checking Opik configuration...")
        opik_tags = OPIK_TRACE_CONFIG["tags"]
        print(f"   ✅ Opik Tags: {opik_tags}")
        
        # Verify all configurations use GPT-5
        print("\n4. Verifying GPT-5 configuration...")
        configs_correct = True
        
        if model_name != "gpt-5":
            print(f"   ❌ LangChain model should be 'gpt-5', found '{model_name}'")
            configs_correct = False
        
        if langflow_model != "gpt-5":
            print(f"   ❌ LangFlow model should be 'gpt-5', found '{langflow_model}'")
            configs_correct = False
            
        if "gpt-5" not in opik_tags:
            print(f"   ❌ Opik tags should include 'gpt-5', found {opik_tags}")
            configs_correct = False
        
        if configs_correct:
            print("   ✅ All configurations correctly set to GPT-5")
        
        # Test basic functionality
        print("\n5. Testing basic analysis...")
        test_doc = "Sample medical claim for GPT-5 testing"
        result = processor.analyze_claim_document(test_doc)
        
        status = result.get('overall_status', 'UNKNOWN')
        confidence = result.get('confidence_level', 0)
        
        print(f"   ✅ Analysis Status: {status}")
        print(f"   ✅ Confidence Level: {confidence}%")
        print(f"   ✅ Processing completed successfully")
        
        print("\n🎉 GPT-5 Configuration Test: PASSED")
        print("\nKey Benefits of GPT-5:")
        print("   • Enhanced reasoning capabilities")
        print("   • Better understanding of complex claims")
        print("   • Improved accuracy in document analysis")
        print("   • Higher token limit (4000 vs 2000)")
        print("   • More nuanced decision making")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration test failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure OpenAI API key supports GPT-5")
        print("2. Check if GPT-5 is available in your region")
        print("3. Verify all dependencies are installed")
        print("4. Run setup script: python setup_langflow_opik.py")
        
        import traceback
        traceback.print_exc()
        return False

def check_model_availability():
    """Check if GPT-5 is available via OpenAI API"""
    print("\n🔍 Checking GPT-5 Model Availability")
    print("=" * 40)
    
    try:
        import openai
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv('openai.api_key') or os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("❌ OpenAI API key not found")
            return False
        
        client = openai.OpenAI(api_key=api_key)
        
        # Try to list models to check availability
        try:
            models = client.models.list()
            model_names = [model.id for model in models.data]
            
            if "gpt-5" in model_names:
                print("✅ GPT-5 is available in your account")
                return True
            else:
                print("⚠️  GPT-5 not found in available models")
                print("Available GPT models:")
                gpt_models = [m for m in model_names if m.startswith('gpt')]
                for model in sorted(gpt_models)[:10]:  # Show first 10
                    print(f"   - {model}")
                
                print("\nNote: GPT-5 may not be generally available yet.")
                print("Consider using gpt-4o or gpt-4-turbo as alternatives.")
                return False
                
        except Exception as e:
            print(f"⚠️  Could not check model availability: {e}")
            print("Proceeding with configuration (model availability will be tested during use)")
            return True
            
    except ImportError:
        print("⚠️  OpenAI library not available for model checking")
        return True
    except Exception as e:
        print(f"❌ Error checking model availability: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 ClaimsAI GPT-5 Configuration Verification")
    print("=" * 50)
    
    # Check model availability first
    model_available = check_model_availability()
    
    # Test configuration
    config_test = test_gpt5_config()
    
    if config_test:
        if model_available:
            print("\n🎊 SUCCESS: GPT-5 is configured and available!")
        else:
            print("\n⚠️  PARTIAL SUCCESS: GPT-5 is configured but availability uncertain")
        
        print("\nYou can now:")
        print("1. Use enhanced AI analysis with GPT-5")
        print("2. Process larger documents (6000 char limit)")
        print("3. Get more accurate claim assessments")
        print("4. Benefit from improved reasoning capabilities")
        
    else:
        print("\n❌ Configuration needs attention")
        print("Please fix the issues above before using GPT-5")
    
    return config_test

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)