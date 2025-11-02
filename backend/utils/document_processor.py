import openai
import os
from typing import Dict, List, Any, Optional
import base64
from PIL import Image
import pytesseract
import PyPDF2
import io

class DocumentProcessor:
    """
    Process claim documents using OpenAI GPT-4 for analysis
    """
    
    def __init__(self):
        # Set your OpenAI API key here or use environment variable
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')
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
                return self._extract_from_image(file_path)
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
        """Extract text from image using OCR"""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")
    
    def analyze_claim_document(self, document_text: str, claim_type: str = "medical_claim") -> Dict[str, Any]:
        """
        Analyze claim document using GPT-4 against reference documents
        """
        try:
            reference_doc = self.reference_documents.get(claim_type, self.reference_documents["medical_claim"])
            
            prompt = f"""
You are an expert medical claims analyst. Compare the submitted claim document against the reference approved claim to identify missing sections, errors, or inconsistencies.

REFERENCE APPROVED CLAIM:
{reference_doc}

SUBMITTED CLAIM DOCUMENT:
{document_text}

Please analyze the submitted claim and provide a detailed assessment in the following JSON format:

{{
    "overall_status": "COMPLETE|INCOMPLETE|INVALID",
    "completeness_score": 0-100,
    "missing_sections": [
        "List of missing required sections"
    ],
    "found_sections": [
        "List of sections that were found"
    ],
    "data_quality_issues": [
        {{
            "section": "section_name",
            "issue": "description of the issue",
            "severity": "HIGH|MEDIUM|LOW"
        }}
    ],
    "validation_errors": [
        {{
            "field": "field_name", 
            "error": "description of validation error",
            "expected_format": "expected format or value"
        }}
    ],
    "recommendations": [
        "List of specific recommendations to improve the claim"
    ],
    "extracted_data": {{
        "patient_name": "extracted or null",
        "patient_id": "extracted or null",
        "date_of_birth": "extracted or null",
        "policy_number": "extracted or null",
        "provider_name": "extracted or null",
        "service_date": "extracted or null",
        "diagnosis_code": "extracted or null",
        "procedure_code": "extracted or null",
        "billed_amount": "extracted or null"
    }},
    "confidence_level": 0-100,
    "processing_notes": "Any additional notes about the analysis"
}}

Focus on:
1. Required sections presence (patient info, provider info, service details, billing)
2. Data format validation (dates, codes, amounts)
3. Logical consistency (dates, amounts, codes matching)
4. Completeness of supporting documentation
5. Proper authorization and signatures

Be thorough and specific in your analysis.
"""

            response = self.client.chat.completions.create(
                model="gpt-4",
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
                max_tokens=2000
            )
            
            # Parse the JSON response
            import json
            try:
                analysis_result = json.loads(response.choices[0].message.content)
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