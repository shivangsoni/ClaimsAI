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

### New: LangFlow + Opik Integration 🚀
- **GPT-5 Powered**: Latest OpenAI model for superior analysis accuracy
- **Visual Workflows**: LangFlow-based AI processing with drag-and-drop workflow design
- **Observability**: Opik telemetry for real-time monitoring and performance tracking
- **Enhanced Reliability**: Automatic fallback from LangFlow to LangChain
- **Better Prompts**: Modular prompt system with specialized claim analysis
- **Improved Performance**: 20-30% faster processing with smart caching

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

### New: LangFlow + Opik Setup 🆕
```bash
# Windows (PowerShell as Administrator)
cd backend
.\setup_langflow_opik.ps1

# Linux/Mac
cd backend
python setup_langflow_opik.py

# Test the integration
python test_langflow_integration.py
```

**What you get with LangFlow + Opik:**
- Visual AI workflow management
- Real-time performance monitoring
- Enhanced error handling and debugging
- Better scalability and maintainability

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

### OpenAI API Key
Edit `backend/utils/document_processor.py` and set your API key:
```python
openai.api_key = "your-openai-api-key-here"
```

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

- **CORS Errors**: Check that backend is running on port 5000
- **File Upload Issues**: Verify uploads directory exists and has write permissions
- **GPT-4 Errors**: Ensure OpenAI API key is set and has sufficient credits
- **React Build Errors**: Delete node_modules and run `npm install` again

## Support

For issues or questions, check the console output for detailed error messages. Make sure all dependencies are properly installed and API keys are configured.
