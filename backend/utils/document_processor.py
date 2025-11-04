import openai
import os
from typing import Dict, List, Any, Optional
import base64
from PIL import Image
import pytesseract
import PyPDF2
import io
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DocumentProcessor:
    """
    Process claim documents using OpenAI GPT-4 for analysis
    """
    
    def __init__(self):
        # Load OpenAI API key from .env file
        api_key = os.getenv('openai.api_key') or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set 'openai.api_key' in your .env file")
        
        self.client = openai.OpenAI(
            api_key=api_key,
            timeout=60.0  # Default 60 second timeout for all requests
        )
        
        # Reference claim document examples for comparison
        self.reference_documents = {
            "medical_claim": """
APPROVED MEDICAL CLAIM EXAMPLE:

Claim ID: MC-2024-001234
Date: 2024-03-15

PATIENT INFORMATION:
- Full Name: John Smith
- Date of Birth: 1985-05-20
- Patient ID: PAT123456
- Policy Number: POL12345678
- Address: 123 Main St, City, State 12345

PROVIDER INFORMATION:
- Provider Name: City General Hospital
- Provider ID: PROV987654
- Tax ID: 12-3456789
- Address: 456 Hospital Ave, City, State 12345
- Phone: (555) 123-4567

SERVICE DETAILS:
- Date of Service: 2024-03-10
- Place of Service: Inpatient Hospital (21)
- Diagnosis Code: Z51.11 (Encounter for antineoplastic chemotherapy)
- Procedure Code: 96413 (Chemotherapy administration)
- Service Description: Chemotherapy treatment session
- Units: 1
- Charges: $2,500.00

SUPPORTING DOCUMENTATION:
- Prior authorization number: PA20240301
- Physician notes included: Yes
- Lab results attached: Yes
- Treatment plan documented: Yes

BILLING INFORMATION:
- Billed Amount: $2,500.00
- Allowed Amount: $2,200.00
- Patient Deductible: $500.00
- Copay: $50.00
- Insurance Payment: $1,650.00
- Patient Responsibility: $550.00

AUTHORIZATION:
Provider Signature: Dr. Jane Doe, MD
Date: 2024-03-10
""",
            "pharmacy_claim": """
APPROVED PHARMACY CLAIM EXAMPLE:

Claim ID: RX-2024-567890
Date: 2024-03-20

PATIENT INFORMATION:
- Full Name: Mary Johnson
- Date of Birth: 1978-12-15
- Patient ID: PAT654321
- Policy Number: POL87654321
- Member ID: MEM789012

PHARMACY INFORMATION:
- Pharmacy Name: HealthCare Pharmacy
- Pharmacy ID: PHARM12345
- DEA Number: BB1234567
- Address: 789 Pharmacy St, City, State 12345
- Phone: (555) 987-6543

PRESCRIPTION DETAILS:
- Prescription Number: RX987654
- Date Filled: 2024-03-20
- Prescriber: Dr. Robert Wilson, MD
- NPI: 1234567890
- Drug Name: Lipitor (Atorvastatin)
- NDC Number: 12345-678-90
- Strength: 20mg
- Quantity: 30 tablets
- Days Supply: 30
- Generic Substitution: No
- DAW Code: 0

BILLING INFORMATION:
- Ingredient Cost: $180.00
- Dispensing Fee: $15.00
- Total Billed: $195.00
- Insurance Payment: $175.50
- Patient Copay: $19.50

CLINICAL INFORMATION:
- Diagnosis: Hyperlipidemia (E78.5)
- Prior Authorization: Not Required
- Step Therapy Met: N/A
- Quantity Limits: Within limits
"""
        }
    
    def extract_text_from_file(self, file_path: str, file_type: str) -> str:
        """
        Extract text from uploaded document (PDF, image, etc.)
        """
        try:
            if file_type.lower() in ['pdf']:
                return self._extract_from_pdf(file_path)
            elif file_type.lower() in ['png', 'jpg', 'jpeg', 'tiff', 'bmp']:
                extracted_text = self._extract_from_image(file_path)
                # Check if this is an OCR unavailable message
                if "[IMAGE UPLOAD DETECTED - OCR NOT AVAILABLE]" in extracted_text:
                    return extracted_text  # Return the helpful message as-is
                return extracted_text
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            raise Exception(f"Text extraction failed: {str(e)}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
        return text
    
    def _extract_from_image(self, file_path: str) -> str:
        """Extract text from image using OCR (with fallback if Tesseract not available)"""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            # If Tesseract is not installed, return a helpful message instead of failing
            if "tesseract" in str(e).lower() or "not installed" in str(e).lower():
                return f"""
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
Error: {str(e)}
"""
            else:
                raise Exception(f"Image processing failed: {str(e)}")
    
    def analyze_claim_document(self, document_text: str, claim_type: str = "medical_claim") -> Dict[str, Any]:
        """
        Analyze claim document using GPT-4 against reference documents
        """
        try:
            # Check if this is an OCR unavailable message
            if "[IMAGE UPLOAD DETECTED - OCR NOT AVAILABLE]" in document_text:
                return {
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
                    "processing_notes": document_text.strip(),
                    "ocr_required": True
                }
            
            # Truncate very large documents to prevent timeout
            max_length = 4000  # Limit document length
            if len(document_text) > max_length:
                document_text = document_text[:max_length] + "\n[DOCUMENT TRUNCATED - SHOWING FIRST 4000 CHARACTERS]"
            
            reference_doc = self.reference_documents.get(claim_type, self.reference_documents["medical_claim"])
            
            prompt = f"""
Analyze this insurance claim document and return results in JSON format:

DOCUMENT TO ANALYZE:
{document_text}

Return JSON with these fields:
- overall_status: "APPROVED", "DENIED", or "NEEDS_REVIEW"
- decision_reasoning: detailed explanation of why the claim was approved, denied, or needs review (minimum 3 sentences)
- key_factors: array of 3-5 main factors that influenced the decision
- completeness_score: 0-100
- missing_sections: array of missing required sections
- found_sections: array of sections found
- validation_errors: array with field, error, expected_format
- recommendations: array of improvement suggestions
- extracted_data: object with patient_name, policy_number, service_date, billed_amount, etc.
- confidence_level: 0-100
- processing_notes: brief analysis summary

DECISION CRITERIA:
APPROVED: All required information present, valid policy, within coverage limits, proper documentation
DENIED: Missing critical information, expired/invalid policy, fraudulent indicators, outside coverage
NEEDS_REVIEW: Incomplete information but potentially valid, unusual circumstances, borderline cases

Provide clear, specific reasoning for your decision based on standard insurance industry practices.
"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert medical claims analyst with years of experience reviewing insurance claims for completeness and accuracy."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2000,
                timeout=60  # Set 60 second timeout
            )
            
            # Parse the JSON response
            import json
            try:
                content = response.choices[0].message.content
                
                # Handle markdown code blocks (remove ```json and ```)
                if content.strip().startswith('```json'):
                    content = content.strip()[7:]  # Remove ```json
                if content.strip().endswith('```'):
                    content = content.strip()[:-3]  # Remove ```
                elif content.strip().startswith('```'):
                    # Handle just ``` without json
                    content = content.strip()[3:]
                    if content.endswith('```'):
                        content = content[:-3]
                
                content = content.strip()
                analysis_result = json.loads(content)
                analysis_result["raw_gpt_response"] = response.choices[0].message.content
                return analysis_result
            except json.JSONDecodeError:
                # If JSON parsing fails, return structured response
                return {
                    "overall_status": "ERROR",
                    "completeness_score": 0,
                    "missing_sections": ["Analysis parsing failed"],
                    "found_sections": [],
                    "data_quality_issues": [],
                    "validation_errors": [{"field": "document", "error": "GPT-4 response parsing failed", "expected_format": "JSON"}],
                    "recommendations": ["Please resubmit the document"],
                    "extracted_data": {},
                    "confidence_level": 0,
                    "processing_notes": f"GPT-4 raw response: {response.choices[0].message.content}",
                    "raw_gpt_response": response.choices[0].message.content
                }
                
        except Exception as e:
            error_msg = str(e).lower()
            if "timeout" in error_msg or "timed out" in error_msg:
                return {
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
                    "processing_notes": f"Analysis timed out after 60 seconds. Document may be too large or complex for processing."
                }
            else:
                return {
                    "overall_status": "ERROR",
                    "completeness_score": 0,
                    "missing_sections": ["Analysis failed"],
                    "found_sections": [],
                    "data_quality_issues": [],
                    "validation_errors": [{"field": "system", "error": str(e), "expected_format": "valid_document"}],
                    "recommendations": ["Please check the document and try again"],
                    "extracted_data": {},
                    "confidence_level": 0,
                    "processing_notes": f"System error: {str(e)}"
                }
    
    def get_improvement_suggestions(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed improvement suggestions based on analysis
        """
        suggestions = {
            "priority_fixes": [],
            "optional_improvements": [],
            "template_recommendations": []
        }
        
        # High priority fixes
        for error in analysis_result.get("validation_errors", []):
            suggestions["priority_fixes"].append({
                "type": "validation_error",
                "description": f"Fix {error.get('field', 'unknown field')}: {error.get('error', 'unknown error')}",
                "expected": error.get('expected_format', 'correct format')
            })
        
        for section in analysis_result.get("missing_sections", []):
            suggestions["priority_fixes"].append({
                "type": "missing_section",
                "description": f"Add missing section: {section}",
                "expected": "Complete section with all required fields"
            })
        
        # Medium priority improvements
        for issue in analysis_result.get("data_quality_issues", []):
            if issue.get("severity") in ["HIGH", "MEDIUM"]:
                suggestions["optional_improvements"].append({
                    "section": issue.get("section", "unknown"),
                    "improvement": issue.get("issue", "unknown issue"),
                    "severity": issue.get("severity", "MEDIUM")
                })
        
        # Template recommendations
        if analysis_result.get("completeness_score", 0) < 70:
            suggestions["template_recommendations"].append(
                "Consider using a standardized claim form template to ensure all required sections are included."
            )
        
        return suggestions

    def compare_with_approved_claims(self, document_text: str) -> Dict[str, Any]:
        """
        Compare document with multiple approved claim examples
        """
        comparison_results = {}
        
        for claim_type, reference in self.reference_documents.items():
            result = self.analyze_claim_document(document_text, claim_type)
            comparison_results[claim_type] = {
                "match_score": result.get("completeness_score", 0),
                "recommended": result.get("completeness_score", 0) > 70
            }
        
        # Find best matching claim type
        best_match = max(comparison_results.items(), key=lambda x: x[1]["match_score"])
        
        return {
            "best_match_type": best_match[0],
            "best_match_score": best_match[1]["match_score"],
            "all_comparisons": comparison_results,
            "detailed_analysis": self.analyze_claim_document(document_text, best_match[0])
        }