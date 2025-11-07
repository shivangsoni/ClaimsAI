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

### New: LangGraph + Optimized Processing 🚀
- **GPT-4o-mini Powered**: Reliable OpenAI model with temperature 0.1 for consistent results
- **LangGraph Workflows**: Local state-machine workflows with no external dependencies
- **Optimized Core Processing**: Main claim document analysis runs without tracing overhead for maximum performance
- **Optional Opik Tracing**: Available for AI suggestions and comparison analysis when needed
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

**What you get with LangGraph + Optimized Processing:**
- Local AI workflow processing (no external services)
- **High-Performance Core**: Main claim processing without tracing overhead
- **Optional Observability**: Opik available for secondary analysis functions when needed
- Enhanced error handling and state management
- Better reliability and maintainability
- Comprehensive workflow visibility from start to finish

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
Create a `.env` file in the `backend/` directory with the following configurations:

```env
# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=your_openai_api_key_here

# Opik Telemetry Configuration (Optional - for monitoring)
OPIK_API_KEY=your_opik_api_key_here
OPIK_PROJECT_NAME=claimsai-document-analysis
OPIK_WORKSPACE=default
```

**⚠️ OPENAI_API_KEY is required for the system to function. Opik configuration is optional for telemetry.**

Copy the example file:
```bash
cd backend
cp .env.example .env
# Edit .env with your actual API keys
```

### Getting Your API Keys

1. **OpenAI API Key**: 
   - Visit https://platform.openai.com/api-keys
   - Create a new API key
   - Ensure you have sufficient credits for GPT-4o-mini usage

2. **Opik Configuration** (Optional):
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
- **Invalid API Keys**: Verify OpenAI API key is correct and has sufficient credits
- **Required Variables**: Ensure `OPENAI_API_KEY` is set (Opik variables are optional)

### Runtime Issues  
- **CORS Errors**: Check that backend is running on port 5000
- **File Upload Issues**: Verify uploads directory exists and has write permissions
- **GPT-4o-mini Errors**: Ensure OpenAI API key is set and has sufficient credits
- **React Build Errors**: Delete node_modules and run `npm install` again
- **LangGraph Processing**: Run `python test_langgraph_integration.py` to verify workflow

## Contributing

### Development Guidelines
1. **Code Style**: Follow PEP 8 for Python, ESLint for JavaScript
2. **Testing**: Test new features before committing
3. **Documentation**: Update README for any new features or configuration changes
4. **Environment**: Use virtual environments for Python dependencies

### Project Structure Details

#### Backend Components
- **`app.py`**: Main Flask application with CORS configuration
- **`routes/`**: Modular API endpoints
  - `claims_routes.py`: Document upload and analysis endpoints
  - `eligibility_routes.py`: Policy eligibility checking
  - `recommendations_routes.py`: AI-powered recommendations
- **`utils/`**: Core business logic
  - `document_processor.py`: LangGraph workflows and AI analysis
  - `database.py`: SQLite database management
  - `claim_validator.py`: Data validation logic
  - `eligibility_checker.py`: Policy eligibility rules
  - `recommendation_engine.py`: Recommendation algorithms
- **`models/`**: Database schema definitions
- **`database/`**: SQLite database files (auto-generated)

#### Frontend Components
- **`components/`**: React UI components
  - `ClaimsDashboard.jsx`: Main dashboard view
  - `ClaimDetailPage.jsx`: Individual claim analysis view
  - `NewClaimForm.jsx`: Claim creation form
  - `DocumentUpload.jsx`: File upload interface
- **`services/api.js`**: Centralized API client
- **`lib/utils.js`**: Utility functions and helpers

### Technology Stack
- **Backend**: Python 3.8+, Flask, SQLite, LangGraph
- **Frontend**: React 18, Tailwind CSS, Lucide React
- **AI/ML**: OpenAI GPT-4o-mini, LangGraph workflows
- **Observability**: Opik telemetry (optional)
- **File Processing**: PyPDF2, Pillow (PIL)

## Deployment

### Production Deployment
1. **Environment Setup**:
   ```bash
   # Set production environment variables
   export FLASK_ENV=production
   export OPENAI_API_KEY=your_production_key
   ```

2. **Database Setup**:
   ```bash
   # Initialize production database
   python -c "from utils.database import DatabaseManager; db = DatabaseManager()"
   ```

3. **Static Files**:
   ```bash
   # Build React frontend
   cd react-frontend
   npm run build
   ```

### Docker Deployment (Optional)
Create a `Dockerfile` in the root directory for containerized deployment.

## Security Considerations
- **API Keys**: Never commit API keys to version control
- **File Upload**: Validate file types and sizes to prevent abuse
- **Input Sanitization**: Sanitize all user inputs before processing
- **CORS**: Configure CORS settings appropriately for production

## Performance Optimization
- **AI Requests**: Implement request caching for repeated document analysis
- **Database**: Add indexes for frequently queried fields
- **File Storage**: Consider cloud storage for large file volumes
- **Frontend**: Implement lazy loading for large claim lists

## Monitoring and Observability
- **Opik Integration**: Optional telemetry for AI workflow monitoring
- **Logging**: Check Flask logs for backend issues
- **Performance**: Monitor response times and AI processing duration
- **Error Tracking**: Implement error logging for production use

## License
This project is for educational and development purposes. Review license requirements for production use.

## Support

### Getting Help
1. **Check Logs**: Review console output for detailed error messages
2. **Verify Setup**: Ensure all dependencies are installed and API keys configured
3. **Test Integration**: Run the test suite to verify system functionality
4. **Documentation**: Refer to this README for setup and troubleshooting

### Common Issues
- **Port Conflicts**: Change ports in configuration if 5000 (backend) or 3000 (frontend) are in use
- **Permission Errors**: Ensure write permissions for uploads/ directory
- **Memory Issues**: Monitor memory usage during large file processing
- **API Rate Limits**: Implement backoff strategies for OpenAI API calls

For detailed error diagnostics, enable debug mode in Flask and check browser developer tools for frontend issues.
