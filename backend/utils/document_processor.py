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

# LangGraph and LangChain imports
try:
    from langgraph.graph import StateGraph, END
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.runnables import RunnablePassthrough
    from typing_extensions import TypedDict
    import functools
    LANGGRAPH_AVAILABLE = True
    print("✅ LangGraph is available")
except ImportError as e:
    LANGGRAPH_AVAILABLE = False
    print(f"⚠️  LangGraph not available: {e}")
    # Fallback imports for basic LangChain
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import JsonOutputParser
        from langchain_core.runnables import RunnablePassthrough
        print("✅ LangChain fallback available")
    except ImportError:
        print("❌ No LangChain available")

# Opik telemetry imports
try:
    import opik
    from opik import track, Opik
    from opik.integrations.langchain import OpikTracer
    OPIK_AVAILABLE = True
    OPIK_CALLBACK_AVAILABLE = True
    print("✅ Opik is available with OpikTracer callback support")
except ImportError:
    try:
        import opik
        from opik import track, Opik
        OPIK_AVAILABLE = True
        OPIK_CALLBACK_AVAILABLE = False
        print("✅ Opik is available but no callback handler")
    except ImportError:
        OPIK_AVAILABLE = False
        OPIK_CALLBACK_AVAILABLE = False
        print("Opik not available. Install with: pip install opik")

# Create safe decorator for Opik tracing
def safe_opik_track(name):
    """Decorator that safely applies Opik tracking when available"""
    def decorator(func):
        if OPIK_AVAILABLE:
            try:
                return track(name=name)(func)
            except Exception as e:
                print(f"⚠️  Opik decorator failed for {name}: {e}")
                return func
        else:
            return func
    return decorator

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

# LangGraph State Definition
if LANGGRAPH_AVAILABLE:
    class ClaimsAnalysisState(TypedDict):
        """State for the claims analysis workflow"""
        document_text: str
        claim_type: str
        reference_document: str
        analysis_result: Optional[Dict[str, Any]]
        error_message: Optional[str]
        processing_method: str

# Load environment variables from .env file
load_dotenv()

class DocumentProcessor:
    """
    Process claim documents using LangGraph workflows and OpenAI GPT-4o-mini with Opik telemetry
    
    Features:
    - LangGraph state-machine workflows for reliable processing
    - Opik telemetry for observability and tracing
    - Graceful fallback to direct LangChain when needed
    - GPT-4o-mini with temperature 0.1 for consistent results
    """
    
    def __init__(self):
        # Load configuration from environment
        self.api_key = os.getenv('openai.api_key') or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set 'openai.api_key' in your .env file")
        
        # LangGraph configuration
        self.use_langgraph = LANGGRAPH_AVAILABLE
        
        # Initialize Opik client if available
        if OPIK_AVAILABLE:
            try:
                # Get Opik configuration from environment
                opik_api_key = os.getenv('OPIK_API_KEY')
                opik_workspace = os.getenv('OPIK_WORKSPACE', 'default')
                opik_project = os.getenv('OPIK_PROJECT_NAME', OPIK_TRACE_CONFIG["project_name"])
                
                # Configure Opik with environment variables
                if opik_api_key:
                    self.opik_client = Opik(
                        api_key=opik_api_key,
                        project_name=opik_project,
                        workspace=opik_workspace
                    )
                    print(f"✅ Opik client initialized with API key")
                    print(f"   Project: {opik_project}")
                    print(f"   Workspace: {opik_workspace}")
                    if OPIK_CALLBACK_AVAILABLE:
                        print(f"   Callback support: ✅ Available for invoke() tracing")
                    else:
                        print(f"   Callback support: ⚠️  Not available")
                else:
                    # Try without API key for local development
                    self.opik_client = Opik(project_name=opik_project)
                    print(f"✅ Opik client initialized without API key (local mode)")
                    print(f"   Project: {opik_project}")
                    if OPIK_CALLBACK_AVAILABLE:
                        print(f"   Callback support: ✅ Available for invoke() tracing")
                    else:
                        print(f"   Callback support: ⚠️  Not available")
                    
            except Exception as e:
                print(f"⚠️  Opik initialization issue: {e}")
                print(f"   This is normal if no API key is configured")
                print(f"   Opik telemetry will be disabled for this session")
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
        
        # Initialize LangGraph workflow
        if self.use_langgraph:
            self.analysis_workflow = self._create_langgraph_workflow()
        else:
            self.analysis_workflow = None
        
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
    
    def _create_langgraph_workflow(self):
        """Create LangGraph workflow for claims analysis"""
        if not LANGGRAPH_AVAILABLE:
            return None
            
        def analyze_document(state: ClaimsAnalysisState) -> ClaimsAnalysisState:
            """LangGraph node: Analyze the document using LLM"""
            try:
                # Create the analysis chain
                chain = (
                    {
                        "document_text": lambda x: state["document_text"],
                        "claim_type": lambda x: state["claim_type"],
                        "reference_document": lambda x: state["reference_document"]
                    }
                    | self.prompt_template
                    | self.llm
                    | self.output_parser
                )
                
                # Run the analysis
                result = chain.invoke({})
                
                # Ensure result is a dictionary
                if isinstance(result, str):
                    result = self._parse_analysis_result(result)
                
                result["processing_method"] = "langgraph"
                
                # Update state
                state["analysis_result"] = result
                state["processing_method"] = "langgraph"
                
                return state
                
            except Exception as e:
                state["error_message"] = str(e)
                state["processing_method"] = "langgraph_error"
                return state
        
        def handle_error(state: ClaimsAnalysisState) -> ClaimsAnalysisState:
            """LangGraph node: Handle errors and create fallback response"""
            error_result = ERROR_RESPONSE_TEMPLATES["system_error"].copy()
            error_result["validation_errors"][0]["error"] = state.get("error_message", "Unknown error")
            error_result["processing_notes"] = f"LangGraph error: {state.get('error_message', 'Unknown error')}"
            error_result["processing_method"] = "error_fallback"
            
            state["analysis_result"] = error_result
            return state
        
        def should_handle_error(state: ClaimsAnalysisState) -> str:
            """Conditional edge: Check if we need error handling"""
            if state.get("error_message"):
                return "error"
            return "success"
        
        # Build the workflow
        workflow = StateGraph(ClaimsAnalysisState)
        
        # Add nodes
        workflow.add_node("analyze", analyze_document)
        workflow.add_node("handle_error", handle_error)
        
        # Set entry point
        workflow.set_entry_point("analyze")
        
        # Add conditional edge
        workflow.add_conditional_edges(
            "analyze",
            should_handle_error,
            {
                "success": END,
                "error": "handle_error"
            }
        )
        
        # Add edge from error handler to end
        workflow.add_edge("handle_error", END)
        
        # Compile the workflow
        return workflow.compile()
    
    def analyze_claim_document(self, document_text: str, claim_type: str = "medical_claim") -> Dict[str, Any]:
        """
        Analyze claim document using LangFlow
        """
        trace_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
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
            
            # Use LangGraph workflow if available, otherwise fallback to LangChain
            if self.use_langgraph and self.analysis_workflow:
                result = self._analyze_with_langgraph(document_text, claim_type, reference_doc, trace_id)
            else:
                print("Using direct LangChain approach...")
                result = self._analyze_with_langchain(document_text, claim_type, reference_doc, trace_id)
            
            return result
                
        except Exception as e:
            error_msg = str(e).lower()
            if "timeout" in error_msg or "timed out" in error_msg:
                result = ERROR_RESPONSE_TEMPLATES["timeout"].copy()
            else:
                result = ERROR_RESPONSE_TEMPLATES["system_error"].copy()
                result["validation_errors"][0]["error"] = str(e)
                result["processing_notes"] = f"System error: {str(e)}"
            
            return result
    
    def _analyze_with_langgraph(self, document_text: str, claim_type: str, reference_doc: str, trace_id: str) -> Dict[str, Any]:
        """
        Analyze document using LangGraph workflow
        """
        try:
            if not self.analysis_workflow:
                raise Exception("LangGraph workflow not available")
            
            # Create initial state
            initial_state = {
                "document_text": document_text,
                "claim_type": claim_type,
                "reference_document": reference_doc,
                "analysis_result": None,
                "error_message": None,
                "processing_method": "langgraph"
            }
            
            # Run the workflow
            final_state = self.analysis_workflow.invoke(initial_state)
            
            # Extract result
            result = final_state.get("analysis_result")
            if result:
                result["trace_id"] = trace_id
                return result
            else:
                raise Exception("No result from LangGraph workflow")
                
        except Exception as e:
            print(f"LangGraph analysis failed: {e}")
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
        if not self.opik_client:
            return
            
        try:
            # Create a trace using the modern Opik API
            self.current_trace = self.opik_client.trace(
                name=OPIK_TRACE_CONFIG["trace_name"],
                input={
                    "document_length": len(document_text),
                    "claim_type": claim_type,
                    "document_preview": document_text[:200] + "..." if len(document_text) > 200 else document_text
                },
                tags=OPIK_TRACE_CONFIG["tags"]
            )
            print(f"📊 Opik trace started: {trace_id}")
        except Exception as e:
            print(f"⚠️  Opik start logging failed: {e}")
            self.current_trace = None
    
    def _log_opik_completion(self, trace_id: str, result: Dict[str, Any], duration: float):
        """Log successful completion to Opik"""
        if not self.opik_client or not hasattr(self, 'current_trace') or not self.current_trace:
            return
            
        try:
            # Update the trace with output and metrics
            self.current_trace.update(
                output={
                    "overall_status": result.get("overall_status"),
                    "confidence_level": result.get("confidence_level"),
                    "completeness_score": result.get("completeness_score"),
                    "processing_method": result.get("processing_method", "unknown")
                },
                metadata={
                    "duration_seconds": duration,
                    "model": "gpt-4o-mini",
                    "temperature": 0.1
                }
            )
            
            # Log feedback scores
            try:
                if result.get("confidence_level"):
                    self.current_trace.log_feedback_score(
                        name="confidence",
                        value=result.get("confidence_level", 0) / 100.0
                    )
                if result.get("completeness_score"):
                    self.current_trace.log_feedback_score(
                        name="completeness", 
                        value=result.get("completeness_score", 0) / 100.0
                    )
            except Exception as score_err:
                print(f"⚠️  Opik score logging failed: {score_err}")
                
            print(f"📊 Opik trace completed: {trace_id} ({duration:.2f}s)")
            
        except Exception as e:
            print(f"⚠️  Opik completion logging failed: {e}")
    
    def _log_opik_error(self, trace_id: str, error_message: str, duration: float):
        """Log error to Opik"""
        if not self.opik_client or not hasattr(self, 'current_trace') or not self.current_trace:
            return
            
        try:
            # Update trace with error information
            self.current_trace.update(
                output={
                    "error": error_message,
                    "status": "failed"
                },
                metadata={
                    "duration_seconds": duration,
                    "error_type": "processing_error"
                }
            )
            
            # Log error as negative feedback score
            try:
                self.current_trace.log_feedback_score(name="success", value=0.0)
            except Exception as score_err:
                print(f"⚠️  Opik error score logging failed: {score_err}")
                
            print(f"📊 Opik error logged: {trace_id} - {error_message}")
            
        except Exception as e:
            print(f"⚠️  Opik error logging failed: {e}")
    
    def _get_opik_callbacks(self):
        """Get Opik callback handlers for LangChain/LangGraph invoke calls"""
        if not OPIK_CALLBACK_AVAILABLE or not self.opik_client:
            return []
        
        try:
            # Create OpikTracer for this session
            tracer = OpikTracer()
            return [tracer]
        except Exception as e:
            print(f"⚠️  Opik tracer creation failed: {e}")
            return []
    
    @safe_opik_track("get_improvement_suggestions")
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
            
            # Get Opik callbacks for chain tracing
            opik_callbacks = self._get_opik_callbacks()
            
            # Run the chain with Opik callbacks
            if opik_callbacks:
                ai_suggestions = chain.invoke(
                    {"analysis_results": json.dumps(analysis_result, indent=2)},
                    config={"callbacks": opik_callbacks}
                )
            else:
                ai_suggestions = chain.invoke({"analysis_results": json.dumps(analysis_result, indent=2)})
            
            return ai_suggestions.get("suggestions", [])
            
        except Exception as e:
            print(f"AI suggestion generation error: {e}")
            return []

    @safe_opik_track("compare_with_approved_claims")
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
            
            # Get Opik callbacks for chain tracing
            opik_callbacks = self._get_opik_callbacks()
            
            # Run the chain with Opik callbacks
            if opik_callbacks:
                comparison_analysis = chain.invoke({
                    "document_text": document_text,
                    "reference_claims": reference_claims_str
                }, config={"callbacks": opik_callbacks})
            else:
                comparison_analysis = chain.invoke({
                    "document_text": document_text,
                    "reference_claims": reference_claims_str
                })
            
            return comparison_analysis
            
        except Exception as e:
            print(f"Detailed comparison error: {e}")
            return {"error": f"Failed to generate detailed comparison: {str(e)}"}
    
    def get_langgraph_status(self) -> Dict[str, Any]:
        """Check LangGraph workflow status"""
        return {
            "available": LANGGRAPH_AVAILABLE,
            "workflow_initialized": self.analysis_workflow is not None,
            "processing_method": "langgraph" if self.use_langgraph else "langchain_direct"
        }
    
    def get_opik_status(self) -> Dict[str, Any]:
        """Get Opik telemetry status"""
        return {
            "available": OPIK_AVAILABLE,
            "callback_available": OPIK_CALLBACK_AVAILABLE,
            "client_initialized": self.opik_client is not None,
            "project_name": OPIK_TRACE_CONFIG["project_name"] if OPIK_AVAILABLE else None
        }