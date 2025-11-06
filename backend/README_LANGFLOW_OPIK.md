# LangGraph + Opik Integration for ClaimsAI

This document explains the new LangGraph and Opik integration for the ClaimsAI document processing system.

## Overview

The ClaimsAI system has been upgraded to use:

- **LangGraph**: Local state-machine workflow builder for reliable AI applications
- **Opik**: Telemetry and observability platform for AI applications  
- **GPT-4o-mini**: Consistent OpenAI model with temperature 0.1 for reliable analysis

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Document      │    │   LangFlow      │                           │   GPT-5         │
│   Upload        │───▶│   Workflow      │───▶│   Analysis      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Opik          │    │   Structured    │
                       │   Tracing       │    │   JSON Result   │
                       └─────────────────┘    └─────────────────┘
```

## New Features

### 1. LangFlow Integration
- Visual workflow design for claims processing
- Hot-swappable AI models and prompts
- Better error handling and retry mechanisms
- Automatic fallback to LangChain if LangFlow is unavailable

### 2. GPT-5 Model Support
- Latest OpenAI model with enhanced reasoning
- Increased token limit (4000 tokens vs 2000)
- Improved accuracy in complex document analysis
- Note: GPT-5 uses default temperature (1.0) only

### 3. Opik Telemetry
- Real-time performance monitoring
- Trace analysis for debugging
- Confidence and completeness scoring
- Error tracking and analysis

### 4. Enhanced Prompts
- Modular prompt system in `prompt.py`
- Specialized prompts for different claim types
- Improved decision reasoning
- Better structured JSON output

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
python setup_langflow_opik.py
```

Or manually:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Update your `.env` file:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# LangFlow Configuration
LANGFLOW_URL=http://localhost:7860
LANGFLOW_FLOW_ID=claims-analysis-flow

# Opik Configuration
OPIK_PROJECT_NAME=claimsai-document-analysis
OPIK_API_KEY=your_opik_api_key_here
```

### 3. Start LangFlow

In a separate terminal:
```bash
langflow run --host 0.0.0.0 --port 7860
```

### 4. Import Flow Configuration

1. Open http://localhost:7860 in your browser
2. Import `langflow_config.json`
3. Configure your OpenAI API key in the ChatOpenAI node
4. Deploy the flow

### 5. Test the Integration

```bash
python test_langflow_integration.py
```

## Usage

### Basic Document Analysis

```python
from utils.document_processor import DocumentProcessor

processor = DocumentProcessor()

# Analyze a claim document
result = processor.analyze_claim_document(document_text, "medical_claim")

print(f"Status: {result['overall_status']}")
print(f"Confidence: {result['confidence_level']}%")
print(f"Reasoning: {result['decision_reasoning']}")
```

### Check Integration Status

```python
# Check LangFlow health
langflow_health = processor.get_langflow_health()
print(f"LangFlow: {langflow_health['status']}")

# Check Opik status
opik_status = processor.get_opik_status()
print(f"Opik Available: {opik_status['available']}")
```

### Get Improvement Suggestions

```python
# Get AI-powered improvement suggestions
suggestions = processor.get_improvement_suggestions(analysis_result)

print("Priority Fixes:")
for fix in suggestions['priority_fixes']:
    print(f"  - {fix['description']}")
```

## API Endpoints

### Integration Status
```http
GET /api/integration/status
```

Response:
```json
{
  "langflow": {
    "status": "healthy",
    "url": "http://localhost:7860",
    "available": true
  },
  "opik": {
    "available": true,
    "client_initialized": true,
    "project_name": "claimsai-document-analysis"
  },
  "processing": {
    "method": "langflow_with_langchain_fallback",
    "ai_model": "gpt-5",
    "telemetry_enabled": true
  }
}
```

## Configuration Files

### `prompt.py`
Contains all AI prompts and templates:
- `CLAIMS_ANALYST_SYSTEM_PROMPT`: System role definition
- `CLAIMS_ANALYSIS_PROMPT_TEMPLATE`: Main analysis prompt
- `IMPROVEMENT_SUGGESTIONS_PROMPT`: Suggestions generation
- `ERROR_RESPONSE_TEMPLATES`: Standardized error responses

### `langflow_config.json`
LangFlow workflow definition with:
- ChatOpenAI node configuration
- PromptTemplate setup
- JsonOutputParser for structured output
- Node connections and data flow

## Monitoring and Observability

### Opik Dashboard
Access your Opik dashboard to monitor:
- Request traces and latency
- Model performance metrics
- Error rates and patterns
- Confidence score distributions

### LangFlow Monitoring
Monitor through LangFlow UI:
- Flow execution status
- Node-level performance
- Input/output inspection
- Real-time debugging

## Troubleshooting

### Common Issues

1. **LangFlow Connection Failed**
   ```bash
   # Check if LangFlow is running
   curl http://localhost:7860/health
   
   # Start LangFlow if needed
   langflow run --host 0.0.0.0 --port 7860
   ```

2. **Opik Tracing Not Working**
   ```bash
   # Check Opik installation
   pip show opik
   
   # Verify API key
   echo $OPIK_API_KEY
   ```

3. **Model Timeout Issues**
   - Increase timeout in LangFlow ChatOpenAI node
   - Reduce document size (auto-truncation at 4000 chars)
   - Check OpenAI API status

### Error Handling

The system implements graceful degradation:
1. **Primary**: LangFlow workflow execution
2. **Fallback**: Direct LangChain processing
3. **Final**: Structured error response

### Performance Optimization

- Document truncation prevents timeouts
- Async processing where possible
- Caching for repeated requests
- Batch processing for multiple documents

## Migration from Direct OpenAI

The new system is backward compatible. Existing code will work with enhanced features:

```python
# Old way (still works)
result = processor.analyze_claim_document(text)

# New features available
trace_id = result.get('trace_id')
processing_method = result.get('processing_method')
ai_suggestions = suggestions.get('ai_powered_suggestions', [])
```

## Development

### Adding New Prompts

1. Add prompt template to `prompt.py`
2. Update LangFlow configuration if needed
3. Test with `test_langflow_integration.py`

### Customizing Workflows

1. Modify `langflow_config.json`
2. Re-import in LangFlow UI
3. Update `DocumentProcessor` if needed

### Adding Telemetry

Use Opik decorators for new functions:
```python
@track(name="my_function") if OPIK_AVAILABLE else lambda func: func
def my_function():
    # Your code here
    pass
```

## Support

For issues:
1. Check integration status: `/api/integration/status`
2. Run diagnostics: `python test_langflow_integration.py`
3. Review logs in Opik dashboard
4. Check LangFlow execution logs

## Performance Metrics

Expected performance improvements:
- **Latency**: 20-30% faster with LangFlow caching
- **Reliability**: 99%+ uptime with fallback system
- **Observability**: Full request tracing
- **Maintainability**: Visual workflow management