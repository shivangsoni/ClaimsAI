import os
import json
import time
import uuid
from typing import Dict, List, Any, Optional
import base64
from PIL import Image
import pytesseract
import PyPDF2
import io
from dotenv import load_dotenv

# LangFlow and LangChain imports
import requests
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough

# Opik telemetry imports
try:
    import opik
    from opik import track, Opik
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    print("Opik not available. Install with: pip install opik")

# Load prompts
from .prompt import (
    CLAIMS_ANALYST_SYSTEM_PROMPT,
    CLAIMS_ANALYSIS_PROMPT_TEMPLATE,
    IMPROVEMENT_SUGGESTIONS_PROMPT,
    DOCUMENT_COMPARISON_PROMPT,
    OCR_NOT_AVAILABLE_MESSAGE,
    ERROR_RESPONSE_TEMPLATES,
    LANGFLOW_CONFIG,
    OPIK_TRACE_CONFIG
)

# Load environment variables from .env file
load_dotenv()

class DocumentProcessor:
    """
    Process claim documents using LangFlow and OpenAI GPT-4 with Opik telemetry
    """
    
    def __init__(self):
        # Load configuration from environment
        self.api_key = os.getenv('openai.api_key') or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set 'openai.api_key' in your .env file")
        
        # LangFlow configuration
        self.langflow_url = os.getenv('LANGFLOW_URL', 'http://localhost:7860')
        self.langflow_flow_id = os.getenv('LANGFLOW_FLOW_ID', 'claims-analysis-flow')
        
        # Initialize Opik client if available
        if OPIK_AVAILABLE:
            try:
                self.opik_client = Opik(project_name=OPIK_TRACE_CONFIG["project_name"])
            except Exception as e:
                print(f"Opik initialization failed: {e}")
                self.opik_client = None
        else:
            self.opik_client = None
        
        # Initialize LangChain components for fallback
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=2000,
            timeout=60
        )
        
        # Setup JSON output parser
        self.output_parser = JsonOutputParser()
        
        # Create prompt template
        self.prompt_template = PromptTemplate(
            template=CLAIMS_ANALYSIS_PROMPT_TEMPLATE,
            input_variables=["document_text", "claim_type", "reference_document"]
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
            elif file_type.lower() == 'txt':
                return self._extract_from_text(file_path)
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
                return OCR_NOT_AVAILABLE_MESSAGE.format(
                    file_path=file_path,
                    error_message=str(e)
                )
            else:
                raise Exception(f"Image processing failed: {str(e)}")
    
    def _extract_from_text(self, file_path: str) -> str:
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Text file reading failed: {str(e)}")
    
    @track(name="analyze_claim_document") if OPIK_AVAILABLE else lambda func: func
    def analyze_claim_document(self, document_text: str, claim_type: str = "medical_claim") -> Dict[str, Any]:
        """
        Analyze claim document using LangFlow with Opik telemetry
        """
        trace_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Log to Opik if available
            if self.opik_client:
                self._log_opik_start(trace_id, document_text, claim_type)
            
            # Check if this is an OCR unavailable message
            if "[IMAGE UPLOAD DETECTED - OCR NOT AVAILABLE]" in document_text:
                result = ERROR_RESPONSE_TEMPLATES["ocr_required"].copy()
                result["processing_notes"] = document_text.strip()
                result["ocr_required"] = True
                return result
            
            # Truncate very large documents to prevent timeout
            max_length = 4000  # Limit document length
            if len(document_text) > max_length:
                document_text = document_text[:max_length] + "\n[DOCUMENT TRUNCATED - SHOWING FIRST 4000 CHARACTERS]"
            
            reference_doc = self.reference_documents.get(claim_type, self.reference_documents["medical_claim"])
            
            # Try LangFlow first, fallback to direct LangChain
            result = self._analyze_with_langflow(document_text, claim_type, reference_doc, trace_id)
            
            if not result or result.get("overall_status") == "ERROR":
                print("LangFlow failed, using fallback LangChain approach...")
                result = self._analyze_with_langchain(document_text, claim_type, reference_doc, trace_id)
            
            # Log completion to Opik
            if self.opik_client:
                self._log_opik_completion(trace_id, result, time.time() - start_time)
            
            return result
                
        except Exception as e:
            error_msg = str(e).lower()
            if "timeout" in error_msg or "timed out" in error_msg:
                result = ERROR_RESPONSE_TEMPLATES["timeout"].copy()
            else:
                result = ERROR_RESPONSE_TEMPLATES["system_error"].copy()
                result["validation_errors"][0]["error"] = str(e)
                result["processing_notes"] = f"System error: {str(e)}"
            
            # Log error to Opik
            if self.opik_client:
                self._log_opik_error(trace_id, str(e), time.time() - start_time)
            
            return result
    
    def _analyze_with_langflow(self, document_text: str, claim_type: str, reference_doc: str, trace_id: str) -> Dict[str, Any]:
        """
        Analyze document using LangFlow API
        """
        try:
            # LangFlow API endpoint
            url = f"{self.langflow_url}/api/v1/run/{self.langflow_flow_id}"
            
            # Prepare the payload
            payload = {
                "input_value": document_text,
                "input_type": "chat",
                "output_type": "chat",
                "tweaks": {
                    "ChatOpenAI-1": {
                        "model": "gpt-4o-mini",
                        "temperature": 0.1,
                        "max_tokens": 2000,
                        "api_key": self.api_key
                    },
                    "PromptTemplate-1": {
                        "template": CLAIMS_ANALYSIS_PROMPT_TEMPLATE,
                        "document_text": document_text,
                        "claim_type": claim_type,
                        "reference_document": reference_doc
                    }
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "x-trace-id": trace_id
            }
            
            # Make the API call
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                langflow_result = response.json()
                
                # Extract the result from LangFlow response
                if "outputs" in langflow_result:
                    output_text = langflow_result["outputs"][0]["outputs"][0]["results"]["message"]["text"]
                    return self._parse_analysis_result(output_text)
                else:
                    raise Exception("Invalid LangFlow response format")
            else:
                raise Exception(f"LangFlow API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"LangFlow analysis failed: {e}")
            return None
    
    def _analyze_with_langchain(self, document_text: str, claim_type: str, reference_doc: str, trace_id: str) -> Dict[str, Any]:
        """
        Fallback analysis using direct LangChain
        """
        try:
            # Create the analysis chain
            chain = (
                {
                    "document_text": RunnablePassthrough(),
                    "claim_type": lambda x: claim_type,
                    "reference_document": lambda x: reference_doc
                }
                | self.prompt_template
                | self.llm
                | self.output_parser
            )
            
            # Run the chain
            result = chain.invoke(document_text)
            
            # Ensure result is a dictionary
            if isinstance(result, str):
                result = self._parse_analysis_result(result)
            
            result["processing_method"] = "langchain_fallback"
            result["trace_id"] = trace_id
            
            return result
            
        except Exception as e:
            print(f"LangChain fallback failed: {e}")
            result = ERROR_RESPONSE_TEMPLATES["system_error"].copy()
            result["validation_errors"][0]["error"] = f"LangChain error: {str(e)}"
            result["processing_notes"] = f"Both LangFlow and LangChain failed: {str(e)}"
            return result
    
    def _parse_analysis_result(self, content: str) -> Dict[str, Any]:
        """
        Parse and clean the analysis result from LLM response
        """
        try:
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
            analysis_result["raw_llm_response"] = content
            return analysis_result
            
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return structured error response
            result = ERROR_RESPONSE_TEMPLATES["system_error"].copy()
            result["validation_errors"][0]["error"] = f"JSON parsing failed: {str(e)}"
            result["processing_notes"] = f"Raw LLM response: {content[:500]}..."
            result["raw_llm_response"] = content
            return result
    
    def _log_opik_start(self, trace_id: str, document_text: str, claim_type: str):
        """Log analysis start to Opik"""
        try:
            self.opik_client.log_traces([{
                "id": trace_id,
                "name": OPIK_TRACE_CONFIG["trace_name"],
                "input": {
                    "document_length": len(document_text),
                    "claim_type": claim_type,
                    "document_preview": document_text[:200] + "..." if len(document_text) > 200 else document_text
                },
                "tags": OPIK_TRACE_CONFIG["tags"],
                "start_time": time.time()
            }])
        except Exception as e:
            print(f"Opik logging failed: {e}")
    
    def _log_opik_completion(self, trace_id: str, result: Dict[str, Any], duration: float):
        """Log successful completion to Opik"""
        try:
            self.opik_client.log_traces([{
                "id": trace_id,
                "output": {
                    "overall_status": result.get("overall_status"),
                    "confidence_level": result.get("confidence_level"),
                    "completeness_score": result.get("completeness_score")
                },
                "end_time": time.time(),
                "duration": duration,
                "feedback_scores": [
                    {"name": "confidence", "value": result.get("confidence_level", 0) / 100.0},
                    {"name": "completeness", "value": result.get("completeness_score", 0) / 100.0}
                ]
            }])
        except Exception as e:
            print(f"Opik completion logging failed: {e}")
    
    def _log_opik_error(self, trace_id: str, error_message: str, duration: float):
        """Log error to Opik"""
        try:
            self.opik_client.log_traces([{
                "id": trace_id,
                "end_time": time.time(),
                "duration": duration,
                "metadata": {"error": error_message, "status": "failed"}
            }])
        except Exception as e:
            print(f"Opik error logging failed: {e}")
    
    @track(name="get_improvement_suggestions") if OPIK_AVAILABLE else lambda func: func
    def get_improvement_suggestions(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed improvement suggestions based on analysis using LangFlow/LangChain
        """
        try:
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
            
            # Generate AI-powered suggestions if possible
            if self.llm and analysis_result.get("overall_status") != "ERROR":
                try:
                    ai_suggestions = self._generate_ai_suggestions(analysis_result)
                    if ai_suggestions:
                        suggestions["ai_powered_suggestions"] = ai_suggestions
                except Exception as e:
                    print(f"AI suggestion generation failed: {e}")
            
            return suggestions
            
        except Exception as e:
            print(f"Error generating improvement suggestions: {e}")
            return {
                "priority_fixes": [],
                "optional_improvements": [],
                "template_recommendations": [],
                "error": f"Failed to generate suggestions: {str(e)}"
            }
    
    def _generate_ai_suggestions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate AI-powered improvement suggestions"""
        try:
            suggestion_prompt = PromptTemplate(
                template=IMPROVEMENT_SUGGESTIONS_PROMPT,
                input_variables=["analysis_results"]
            )
            
            chain = suggestion_prompt | self.llm | JsonOutputParser()
            ai_suggestions = chain.invoke({"analysis_results": json.dumps(analysis_result, indent=2)})
            
            return ai_suggestions.get("suggestions", [])
            
        except Exception as e:
            print(f"AI suggestion generation error: {e}")
            return []

    @track(name="compare_with_approved_claims") if OPIK_AVAILABLE else lambda func: func
    def compare_with_approved_claims(self, document_text: str) -> Dict[str, Any]:
        """
        Compare document with multiple approved claim examples using LangFlow/LangChain
        """
        try:
            comparison_results = {}
            
            for claim_type, reference in self.reference_documents.items():
                result = self.analyze_claim_document(document_text, claim_type)
                comparison_results[claim_type] = {
                    "match_score": result.get("completeness_score", 0),
                    "recommended": result.get("completeness_score", 0) > 70,
                    "status": result.get("overall_status", "UNKNOWN")
                }
            
            # Find best matching claim type
            best_match = max(comparison_results.items(), key=lambda x: x[1]["match_score"])
            
            # Generate detailed comparison using AI if available
            detailed_comparison = None
            if self.llm:
                try:
                    detailed_comparison = self._generate_detailed_comparison(document_text, comparison_results)
                except Exception as e:
                    print(f"Detailed comparison generation failed: {e}")
            
            result = {
                "best_match_type": best_match[0],
                "best_match_score": best_match[1]["match_score"],
                "all_comparisons": comparison_results,
                "detailed_analysis": self.analyze_claim_document(document_text, best_match[0])
            }
            
            if detailed_comparison:
                result["ai_detailed_comparison"] = detailed_comparison
                
            return result
            
        except Exception as e:
            print(f"Error in claim comparison: {e}")
            return {
                "best_match_type": "unknown",
                "best_match_score": 0,
                "all_comparisons": {},
                "detailed_analysis": ERROR_RESPONSE_TEMPLATES["system_error"],
                "error": f"Comparison failed: {str(e)}"
            }
    
    def _generate_detailed_comparison(self, document_text: str, comparison_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed AI-powered comparison analysis"""
        try:
            comparison_prompt = PromptTemplate(
                template=DOCUMENT_COMPARISON_PROMPT,
                input_variables=["document_text", "reference_claims"]
            )
            
            reference_claims_str = json.dumps(self.reference_documents, indent=2)
            
            chain = comparison_prompt | self.llm | JsonOutputParser()
            comparison_analysis = chain.invoke({
                "document_text": document_text,
                "reference_claims": reference_claims_str
            })
            
            return comparison_analysis
            
        except Exception as e:
            print(f"Detailed comparison error: {e}")
            return {"error": f"Failed to generate detailed comparison: {str(e)}"}
    
    def get_langflow_health(self) -> Dict[str, Any]:
        """Check LangFlow service health"""
        try:
            response = requests.get(f"{self.langflow_url}/health", timeout=5)
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "url": self.langflow_url,
                "response_code": response.status_code
            }
        except Exception as e:
            return {
                "status": "unreachable",
                "url": self.langflow_url,
                "error": str(e)
            }
    
    def get_opik_status(self) -> Dict[str, Any]:
        """Get Opik telemetry status"""
        return {
            "available": OPIK_AVAILABLE,
            "client_initialized": self.opik_client is not None,
            "project_name": OPIK_TRACE_CONFIG["project_name"] if OPIK_AVAILABLE else None
        }