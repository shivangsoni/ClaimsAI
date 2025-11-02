from flask import Blueprint, request, jsonify
import re
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from utils.claim_validator import ClaimValidator
from utils.database import DatabaseManager
from utils.document_processor import DocumentProcessor

claims_bp = Blueprint('claims', __name__)

@claims_bp.route('/validate', methods=['POST'])
def validate_claim():
    """
    Iteration 1: Detect inconsistencies or missing information in submitted claims
    """
    try:
        claim_data = request.get_json()
        
        if not claim_data:
            return jsonify({
                'error': 'No claim data provided'
            }), 400
        
        validator = ClaimValidator()
        validation_result = validator.validate_claim(claim_data)
        
        # Save validation result to database if claim_id is provided
        if 'claim_id' in claim_data:
            try:
                db = DatabaseManager()
                db.save_validation_result(claim_data['claim_id'], validation_result)
            except Exception as db_error:
                print(f"Database save error: {db_error}")
        
        return jsonify(validation_result), 200
    
    except Exception as e:
        return jsonify({
            'error': f'Validation failed: {str(e)}'
        }), 500

@claims_bp.route('/submit', methods=['POST'])
def submit_claim():
    """
    Submit a new claim for processing
    """
    try:
        claim_data = request.get_json()
        
        # Generate claim ID
        claim_id = f"CLM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        claim_data['claim_id'] = claim_id
        
        # Save to database
        db = DatabaseManager()
        db.save_claim(claim_data)
        
        response = {
            'claim_id': claim_id,
            'status': 'submitted',
            'message': 'Claim submitted successfully',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 201
    
    except Exception as e:
        return jsonify({
            'error': f'Submission failed: {str(e)}'
        }), 500

@claims_bp.route('/status/<claim_id>', methods=['GET'])
def get_claim_status(claim_id):
    """
    Get the status of a specific claim
    """
    # Mock response - in real app, query database
    return jsonify({
        'claim_id': claim_id,
        'status': 'under_review',
        'last_updated': datetime.now().isoformat()
    }), 200

@claims_bp.route('/upload', methods=['POST'])
def upload_claim_document():
    """
    Upload and analyze claim document using GPT-4
    """
    try:
        # Check if file is present
        if 'document' not in request.files:
            return jsonify({'error': 'No document file provided'}), 400
        
        file = request.files['document']
        claim_type = request.form.get('claim_type', 'medical_claim')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'File type {file_ext} not supported. Use: {", ".join(allowed_extensions)}'}), 400
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file securely
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Process document
        processor = DocumentProcessor()
        
        # Extract text from document
        document_text = processor.extract_text_from_file(file_path, file_ext)
        
        if not document_text.strip():
            return jsonify({'error': 'No text could be extracted from the document'}), 400
        
        # Analyze with GPT-4
        analysis_result = processor.analyze_claim_document(document_text, claim_type)
        
        # Get improvement suggestions
        suggestions = processor.get_improvement_suggestions(analysis_result)
        
        # Compare with approved claims
        comparison = processor.compare_with_approved_claims(document_text)
        
        # Generate claim ID
        claim_id = f"DOC_{timestamp}"
        
        # Save to database (you might want to extend the database schema)
        try:
            db = DatabaseManager()
            # For now, save as a regular claim with additional document info
            document_data = {
                'claim_id': claim_id,
                'patient_id': analysis_result.get('extracted_data', {}).get('patient_id', 'EXTRACTED'),
                'patient_name': analysis_result.get('extracted_data', {}).get('patient_name', 'From Document'),
                'date_of_birth': analysis_result.get('extracted_data', {}).get('date_of_birth', '1900-01-01'),
                'policy_number': analysis_result.get('extracted_data', {}).get('policy_number', 'UNKNOWN'),
                'provider_name': analysis_result.get('extracted_data', {}).get('provider_name', 'From Document'),
                'provider_id': 'DOC_UPLOAD',
                'service_date': analysis_result.get('extracted_data', {}).get('service_date', '2024-01-01'),
                'service_type': claim_type,
                'diagnosis_code': analysis_result.get('extracted_data', {}).get('diagnosis_code', 'EXTRACTED'),
                'procedure_code': analysis_result.get('extracted_data', {}).get('procedure_code', 'EXTRACTED'),
                'amount_billed': analysis_result.get('extracted_data', {}).get('billed_amount', 0)
            }
            db.save_claim(document_data)
        except Exception as db_error:
            print(f"Database save error: {db_error}")
        
        # Clean up uploaded file (optional, or keep for records)
        # os.remove(file_path)
        
        response = {
            'claim_id': claim_id,
            'status': 'analyzed',
            'document_analysis': analysis_result,
            'improvement_suggestions': suggestions,
            'comparison_with_approved': comparison,
            'extracted_text_preview': document_text[:500] + "..." if len(document_text) > 500 else document_text,
            'file_info': {
                'original_name': filename,
                'file_type': file_ext,
                'size_bytes': os.path.getsize(file_path),
                'processed_at': datetime.now().isoformat()
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Document processing failed: {str(e)}'
        }), 500

@claims_bp.route('/analyze-text', methods=['POST'])
def analyze_text_directly():
    """
    Analyze claim text directly without file upload (for testing)
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided for analysis'}), 400
        
        text = data['text']
        claim_type = data.get('claim_type', 'medical_claim')
        
        processor = DocumentProcessor()
        
        # Analyze with GPT-4
        analysis_result = processor.analyze_claim_document(text, claim_type)
        
        # Get improvement suggestions
        suggestions = processor.get_improvement_suggestions(analysis_result)
        
        # Compare with approved claims
        comparison = processor.compare_with_approved_claims(text)
        
        response = {
            'status': 'analyzed',
            'document_analysis': analysis_result,
            'improvement_suggestions': suggestions,
            'comparison_with_approved': comparison
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Text analysis failed: {str(e)}'
        }), 500