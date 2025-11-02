from utils.document_processor import DocumentProcessor
import json

print("🔍 Testing ClaimsAI GPT-4 Integration...")
print("=" * 50)

try:
    # Initialize processor
    processor = DocumentProcessor()
    print("✅ DocumentProcessor initialized with OpenAI API key!")
    
    # Sample claim text
    sample_claim = """
    MEDICAL CLAIM
    Patient: John Smith
    Policy Number: POL123456  
    Date of Service: 2024-11-01
    Provider: Health Clinic
    Diagnosis: Annual checkup
    Amount Billed: $150.00
    """
    
    print("\n🤖 Analyzing sample claim with GPT-4...")
    result = processor.analyze_claim_document(sample_claim)
    
    print("\n📊 ANALYSIS RESULTS:")
    print(f"Status: {result.get('overall_status', 'Unknown')}")
    print(f"Completeness: {result.get('completeness_score', 0)}%")
    print(f"Confidence: {result.get('confidence_level', 0)}%")
    
    missing = result.get('missing_sections', [])
    if missing:
        print(f"Missing: {', '.join(missing[:3])}")
    
    print("\n🎉 SUCCESS: GPT-4 integration is working!")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("Check your OpenAI API key and credits.")