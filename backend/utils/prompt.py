"""
Prompts for Claims Document Analysis using LangFlow
"""

# System prompts for different roles
CLAIMS_ANALYST_SYSTEM_PROMPT = """
You are a senior medical claims adjuster with 10+ years of experience. 
You specialize in analyzing insurance claim documents and making coverage decisions 
with detailed reasoning based on industry best practices and regulatory compliance.

Your expertise includes:
- Medical necessity evaluation
- Fraud detection and prevention
- Claims processing workflows
- Insurance policy interpretation
- Risk assessment and management
- Regulatory compliance (HIPAA, state insurance laws)
"""

# Main analysis prompt template
CLAIMS_ANALYSIS_PROMPT_TEMPLATE = """
Analyze this insurance claim document and make a coverage decision with detailed reasoning.

DOCUMENT TO ANALYZE:
{document_text}

CLAIM TYPE: {claim_type}

REFERENCE STANDARDS:
{reference_document}

Return JSON with these exact fields:
- overall_status: "APPROVED", "DENIED", or "NEEDS_REVIEW"
- decision_reasoning: Detailed explanation (4-6 sentences) of your decision including:
  * What specific evidence supported your decision
  * Any red flags or positive indicators found
  * Compliance with standard insurance practices
  * Risk assessment considerations
- key_factors: Array of 3-5 specific factors that most influenced your decision
- completeness_score: 0-100 (percentage of required information present)
- missing_sections: Array of missing required sections/information
- found_sections: Array of sections/information that were found and complete
- validation_errors: Array of specific issues found (field, error description, expected format)
- recommendations: Array of specific actionable recommendations
- extracted_data: Object with all extracted information:
  * patient_name, patient_id, policy_number, service_date
  * provider_name, diagnosis_code, procedure_code  
  * billed_amount, service_type, etc.
- confidence_level: 0-100 (how confident you are in this decision)
- processing_notes: Summary of your analysis process and key observations

DECISION CRITERIA FOR CLAIMS ADJUDICATION:

APPROVED - Recommend for payment when:
✓ All required patient and provider information is complete and verified
✓ Policy is active and covers the claimed services  
✓ Diagnosis codes align with procedures performed
✓ Charges are within reasonable and customary limits
✓ Proper authorization obtained for specialized services
✓ No fraud indicators detected

DENIED - Reject payment when:
✗ Missing critical information (patient ID, policy number, dates)
✗ Policy expired, suspended, or doesn't cover claimed services
✗ Fraudulent indicators (duplicate claims, suspicious patterns)
✗ Services not medically necessary or experimental
✗ Billing errors or inflated charges
✗ Prior authorization missing for required procedures

NEEDS_REVIEW - Flag for manual review when:
⚠ Unusual circumstances requiring medical director review
⚠ High-cost claims near policy limits  
⚠ Incomplete but potentially valid information
⚠ Complex cases requiring additional documentation
⚠ First-time providers or unusual billing patterns

Analyze this claim as if making a real coverage decision that affects both patient care and company liability. 
Be thorough, fair, and follow industry best practices.
"""

# Improvement suggestions prompt
IMPROVEMENT_SUGGESTIONS_PROMPT = """
Based on the analysis results, generate specific improvement suggestions for this claim document.

ANALYSIS RESULTS:
{analysis_results}

Provide detailed suggestions in these categories:
1. Priority Fixes: Critical issues that must be addressed
2. Optional Improvements: Enhancements that would strengthen the claim
3. Template Recommendations: Suggestions for better documentation practices

Format as JSON with structured recommendations.
"""

# Document comparison prompt
DOCUMENT_COMPARISON_PROMPT = """
Compare this claim document against approved claim examples to determine best match and compliance level.

DOCUMENT TO ANALYZE:
{document_text}

REFERENCE CLAIMS:
{reference_claims}

Return a detailed comparison including:
- best_match_type: The closest matching claim type
- match_score: Similarity percentage (0-100)
- compliance_gaps: Areas where the document differs from standards
- recommendations: Specific steps to improve compliance
"""

# OCR fallback message
OCR_NOT_AVAILABLE_MESSAGE = """
[IMAGE UPLOAD DETECTED - OCR NOT AVAILABLE]

This appears to be an image file that requires OCR (Optical Character Recognition) to extract text.

To enable text extraction from images, please install Tesseract OCR:
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
- Add Tesseract to your system PATH

For now, please:
1. Convert your image to text manually, or
2. Upload a PDF version of the document, or  
3. Install Tesseract OCR for automatic text extraction

Image file: {file_path}
Error: {error_message}
"""

# Error handling prompts
ERROR_RESPONSE_TEMPLATES = {
    "ocr_required": {
        "overall_status": "OCR_REQUIRED",
        "completeness_score": 0,
        "missing_sections": ["Text extraction required"],
        "found_sections": [],
        "data_quality_issues": [],
        "validation_errors": [{"field": "ocr", "error": "Tesseract OCR not available", "expected_format": "Install Tesseract OCR"}],
        "recommendations": [
            "Install Tesseract OCR to extract text from images",
            "Convert image to PDF format",
            "Manually type the document content"
        ],
        "extracted_data": {},
        "confidence_level": 0,
        "processing_notes": "OCR processing required for image files",
        "ocr_required": True
    },
    "timeout": {
        "overall_status": "TIMEOUT",
        "completeness_score": 0,
        "missing_sections": ["Analysis timed out"],
        "found_sections": [],
        "data_quality_issues": [],
        "validation_errors": [{"field": "processing", "error": "Analysis timeout - document too large or complex", "expected_format": "smaller_document"}],
        "recommendations": [
            "Try with a smaller document",
            "Break large documents into sections",
            "Ensure document is properly formatted"
        ],
        "extracted_data": {},
        "confidence_level": 0,
        "processing_notes": "Analysis timed out after 60 seconds. Document may be too large or complex for processing."
    },
    "system_error": {
        "overall_status": "ERROR",
        "completeness_score": 0,
        "missing_sections": ["Analysis failed"],
        "found_sections": [],
        "data_quality_issues": [],
        "validation_errors": [{"field": "system", "error": "System processing error", "expected_format": "valid_document"}],
        "recommendations": ["Please check the document and try again"],
        "extracted_data": {},
        "confidence_level": 0,
        "processing_notes": "System error occurred during processing"
    }
}

# LangFlow configuration templates
LANGFLOW_CONFIG = {
    "flow_id": "claims_analysis_flow",
    "tweaks": {
        "ChatOpenAI-1": {
            "model": "gpt-4o-mini",
            "temperature": 0.1,
            "max_tokens": 2000
        },
        "PromptTemplate-1": {
            "template": CLAIMS_ANALYSIS_PROMPT_TEMPLATE
        }
    }
}

# Opik tracing configuration
OPIK_TRACE_CONFIG = {
    "project_name": "claimsai-document-analysis",
    "trace_name": "claims_document_processing",
    "tags": ["claims", "document_analysis", "langflow", "gpt-4o-mini"]
}