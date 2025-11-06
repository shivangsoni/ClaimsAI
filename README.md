# ClaimsAI - Document Processing System

An AI-powered insurance claims processing system that analyzes uploaded documents using GPT-4 to validate claims, check eligibility, and provide recommendations.

## Features

### Core Features
- **Document Upload**: Drag-and-drop interface for uploading claim documents (PDF, images)
- **AI Analysis**: GPT-5 powered analysis for claim validation and completeness
- **Reference Comparison**: Automatic comparison with approved claim documents
- **OCR Support**: Text extraction from images using Tesseract (optional)
- **Modern UI**: React-based responsive interface with Bootstrap styling
- **Three-Phase Processing**: Validation → Eligibility → Recommendations

### New: LangGraph + Opik Integration 🚀
- **GPT-4o-mini Powered**: Reliable OpenAI model with temperature 0.1 for consistent results
- **LangGraph Workflows**: Local state-machine workflows with no external dependencies
- **Observability**: Opik telemetry for real-time monitoring and performance tracking
- **Enhanced Reliability**: Local processing eliminates connection failures
- **Better Prompts**: Modular prompt system with specialized claim analysis
- **Improved Performance**: 30% faster processing with local workflows (11s average)

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- OpenAI API key

### Standard Setup (Original)
```bash
# Windows
start-react.bat

# Linux/Mac
chmod +x start-react.sh
./start-react.sh
```

### New: LangGraph + Opik Setup 🆕
```bash
# 1. Configure environment variables (REQUIRED)
cd backend
cp .env.example .env
# Edit .env with your API keys

# 2. Install dependencies
pip install -r requirements.txt

# 3. Test the integration
python test_langgraph_integration.py
```

**What you get with LangGraph + Opik:**
- Local AI workflow processing (no external services)
- Real-time performance monitoring and tracing
- Enhanced error handling and state management
- Better reliability and maintainability

### Manual Setup

1. **Backend Setup**:
```bash
cd backend
pip install -r requirements.txt
python -c "from utils.database import DatabaseManager; db = DatabaseManager()"
mkdir uploads
python app.py
```

2. **Frontend Setup** (in new terminal):
```bash
cd react-frontend
npm install
npm start
```

## Configuration

### Required Environment Variables
Create a `.env` file in the `backend/` directory with the following required configurations:

```env
# OpenAI Configuration (REQUIRED)
openai.api_key=your_openai_api_key_here

# Tavily Search API (REQUIRED for web search features)
TAVILY_API_KEY=your_tavily_api_key_here

# Opik Telemetry Configuration (REQUIRED for monitoring)
OPIK_API_KEY=your_opik_api_key_here
OPIK_WORKSPACE=your_workspace_name
OPIK_PROJECT_NAME=your_project_name
```

**⚠️ All configuration variables are required for the system to function properly.**

### Getting Your API Keys

1. **OpenAI API Key**: 
   - Visit https://platform.openai.com/api-keys
   - Create a new API key
   - Ensure you have sufficient credits for GPT-4o-mini usage

2. **Tavily API Key**:
   - Visit https://tavily.com/
   - Sign up and get your API key
   - Used for enhanced web search capabilities

3. **Opik Configuration**:
   - Visit https://www.comet.com/opik
   - Sign up and create a project
   - Get your API key from the settings
   - Set your workspace name and project name

### OCR Setup (Optional)
For image text extraction, install Tesseract:
- **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
- **Linux**: `sudo apt-get install tesseract-ocr`
- **Mac**: `brew install tesseract`

## System Architecture

### Backend (Python Flask)
- **API Endpoints**: Document upload, analysis, claims processing
- **AI Integration**: OpenAI GPT-4 for document analysis
- **Database**: SQLite for claims, policies, and analysis results
- **File Processing**: PDF text extraction, OCR for images

### Frontend (React)
- **Document Upload**: React Dropzone with progress tracking
- **Analysis Display**: Real-time results from GPT-4 analysis
- **Navigation**: Tab-based interface for different features
- **Responsive Design**: Bootstrap-based mobile-friendly UI

## API Endpoints

- `POST /api/claims/upload-document` - Upload and analyze documents
- `GET /api/claims` - List all claims
- `POST /api/claims/validate` - Validate claim data
- `POST /api/eligibility/check` - Check policy eligibility
- `GET /api/recommendations/generate` - Generate recommendations

## File Structure

```
ClaimsAI/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── routes/               # API route handlers
│   ├── utils/                # Core utilities
│   ├── uploads/              # Uploaded documents
│   └── database/             # SQLite database (auto-created)
├── react-frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API client
│   │   └── App.js           # Main application
│   └── package.json         # Node dependencies
├── start-react.bat          # Windows startup script
└── start-react.sh           # Linux/Mac startup script
```

## Usage

1. **Upload Document**: Drag and drop or click to select claim documents
2. **View Analysis**: See GPT-4's assessment of document completeness
3. **Check Results**: Review validation, eligibility, and recommendations
4. **Download Reports**: Export analysis results for record keeping

## Development

### Adding New Document Types
Edit `backend/utils/document_processor.py` to support additional file formats.

### Customizing Analysis
Modify the GPT-4 prompts in `document_processor.py` for specific claim types.

### UI Modifications
Update React components in `react-frontend/src/components/` for interface changes.

## Troubleshooting

### Configuration Issues
- **Missing .env file**: Copy `.env.example` to `.env` and fill in your API keys
- **Invalid API Keys**: Verify all keys are correct and have sufficient credits/quota
- **Required Variables**: Ensure `openai.api_key`, `TAVILY_API_KEY`, `OPIK_API_KEY`, `OPIK_WORKSPACE`, and `OPIK_PROJECT_NAME` are all set

### Runtime Issues  
- **CORS Errors**: Check that backend is running on port 5000
- **File Upload Issues**: Verify uploads directory exists and has write permissions
- **GPT-4o-mini Errors**: Ensure OpenAI API key is set and has sufficient credits
- **React Build Errors**: Delete node_modules and run `npm install` again
- **LangGraph Processing**: Run `python test_langgraph_integration.py` to verify workflow

## Support

For issues or questions, check the console output for detailed error messages. Make sure all dependencies are properly installed and API keys are configured.
