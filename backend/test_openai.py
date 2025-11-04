import os
from dotenv import load_dotenv
from utils.document_processor import DocumentProcessor

# Load environment variables
load_dotenv()

def test_openai_connection():
    """Test if OpenAI API is working"""
    try:
        # Check if API key is loaded
        api_key = os.getenv('OPENAI_API_KEY') or os.getenv('openai.api_key')
        print(f"API Key loaded: {'Yes' if api_key else 'No'}")
        if api_key:
            print(f"API Key starts with: {api_key[:8]}...")
        
        # Test DocumentProcessor
        processor = DocumentProcessor()
        
        # Simple test text
        test_text = """
        INSURANCE CLAIM FORM
        Policy Number: POL-2024-789456
        Patient Name: John Smith
        Service Date: 2024-10-15
        Amount: $150.00
        """
        
        print("\nTesting GPT-4 analysis...")
        result = processor.analyze_claim_document(test_text, "medical_claim")
        
        print("✅ GPT-4 analysis successful!")
        print(f"Overall Status: {result.get('overall_status', 'N/A')}")
        print(f"Confidence: {result.get('confidence_level', 'N/A')}%")
        print(f"Decision: {result.get('decision_reasoning', 'N/A')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ GPT-4 analysis failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_openai_connection()