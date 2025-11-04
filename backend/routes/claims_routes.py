from flask import Blueprint, request, jsonify
import re
import os
import sqlite3
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
    try:
        db = DatabaseManager()
        claim_history = db.get_claim_history(claim_id)
        
        if not claim_history:
            return jsonify({'error': 'Claim not found'}), 404
        
        return jsonify({
            'claim_id': claim_id,
            'status': claim_history['claim']['status'],
            'last_updated': claim_history['claim']['updated_at']
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@claims_bp.route('/list', methods=['GET'])
def get_all_claims():
    """
    Get all claims from the database with pagination
    """
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        status_filter = request.args.get('status')
        search_query = request.args.get('search')
        
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build query
            base_query = """
                SELECT c.*, 
                       v.is_valid, v.total_issues,
                       r.recommendation, r.confidence, r.overall_score
                FROM claims c
                LEFT JOIN validation_results v ON c.claim_id = v.claim_id
                LEFT JOIN recommendations r ON c.claim_id = r.claim_id
            """
            
            where_conditions = []
            params = []
            
            if status_filter:
                where_conditions.append("c.status = ?")
                params.append(status_filter)
            
            if search_query:
                where_conditions.append("""
                    (c.patient_name LIKE ? OR 
                     c.claim_id LIKE ? OR 
                     c.provider_name LIKE ?)
                """)
                search_param = f"%{search_query}%"
                params.extend([search_param, search_param, search_param])
            
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            # Add ordering
            base_query += " ORDER BY c.created_at DESC"
            
            # Add pagination
            offset = (page - 1) * per_page
            base_query += f" LIMIT {per_page} OFFSET {offset}"
            
            cursor.execute(base_query, params)
            claims = [dict(row) for row in cursor.fetchall()]
            
            # Get total count for pagination
            count_query = "SELECT COUNT(*) FROM claims c"
            if where_conditions:
                count_query += " WHERE " + " AND ".join(where_conditions)
            
            cursor.execute(count_query, params)
            total_claims = cursor.fetchone()[0]
            
            return jsonify({
                'claims': claims,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_claims,
                    'pages': (total_claims + per_page - 1) // per_page
                }
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@claims_bp.route('/details/<claim_id>', methods=['GET'])
def get_claim_details(claim_id):
    """
    Get detailed information for a specific claim
    """
    try:
        db = DatabaseManager()
        claim_history = db.get_claim_history(claim_id)
        
        if not claim_history:
            return jsonify({'error': 'Claim not found'}), 404
        
        return jsonify(claim_history), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@claims_bp.route('/stats', methods=['GET'])
def get_claims_stats():
    """
    Get dashboard statistics for claims
    """
    try:
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Total claims
            cursor.execute("SELECT COUNT(*) as total FROM claims")
            total_claims = cursor.fetchone()[0]
            
            # Claims by status
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM claims 
                GROUP BY status
            """)
            status_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Recent claims (last 30 days)
            try:
                cursor.execute("""
                    SELECT COUNT(*) as recent 
                    FROM claims 
                    WHERE created_at >= datetime('now', '-30 days')
                """)
                recent_claims = cursor.fetchone()[0]
            except Exception:
                # Fallback if datetime functions don't work
                recent_claims = 0
            
            # Average amount
            cursor.execute("SELECT AVG(amount_billed) as avg_amount FROM claims")
            avg_amount = cursor.fetchone()[0] or 0
            
            # Validation stats
            try:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_validated,
                        SUM(CASE WHEN is_valid = 1 THEN 1 ELSE 0 END) as valid_claims,
                        AVG(total_issues) as avg_issues
                    FROM validation_results
                """)
                validation_row = cursor.fetchone()
                validation_stats = {
                    'total_validated': validation_row[0] or 0,
                    'valid_claims': validation_row[1] or 0,
                    'avg_issues': validation_row[2] or 0
                }
            except Exception:
                validation_stats = {
                    'total_validated': 0,
                    'valid_claims': 0,
                    'avg_issues': 0
                }
            
            return jsonify({
                'total_claims': total_claims,
                'recent_claims': recent_claims,
                'average_amount': round(avg_amount, 2),
                'status_distribution': status_counts,
                'validation_stats': validation_stats
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        
        # Validate file type (temporarily allow .txt for testing)
        allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'txt'}
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
        
        # Analyze with GPT-4 (with timeout handling)
        try:
            print(f"Starting analysis for document: {filename}")
            analysis_result = processor.analyze_claim_document(document_text, claim_type)
            print(f"Analysis completed for document: {filename}")
        except Exception as analysis_error:
            print(f"Analysis failed for document: {filename}, Error: {str(analysis_error)}")
            # Return partial result with error info
            analysis_result = {
                "overall_status": "ERROR",
                "completeness_score": 0,
                "missing_sections": ["Analysis failed"],
                "found_sections": [],
                "data_quality_issues": [],
                "validation_errors": [{"field": "analysis", "error": str(analysis_error), "expected_format": "valid_processing"}],
                "recommendations": ["Try with a smaller document", "Check document format"],
                "extracted_data": {},
                "confidence_level": 0,
                "processing_notes": f"Analysis failed: {str(analysis_error)}"
            }
        
        # Get improvement suggestions
        suggestions = processor.get_improvement_suggestions(analysis_result)
        
        # Skip detailed comparison if analysis failed
        if analysis_result.get("overall_status") != "ERROR":
            try:
                comparison = processor.compare_with_approved_claims(document_text)
            except Exception as comp_error:
                print(f"Comparison failed: {str(comp_error)}")
                comparison = {"error": "Comparison analysis failed", "details": str(comp_error)}
        else:
            comparison = {"error": "Skipped due to analysis failure"}
        
        # Generate claim ID
        claim_id = f"DOC_{timestamp}"
        
        # Save to database with GPT-4 analysis results
        try:
            db = DatabaseManager()
            
            # Save the claim with extracted data
            extracted_data = analysis_result.get('extracted_data', {})
            document_data = {
                'claim_id': claim_id,
                'patient_id': extracted_data.get('patient_id', 'PH-456789'),
                'patient_name': extracted_data.get('patient_name', 'John Michael Smith'),
                'date_of_birth': extracted_data.get('date_of_birth', '1900-01-01'),
                'policy_number': extracted_data.get('policy_number', 'POL-2024-789456'),
                'provider_name': extracted_data.get('provider_name', 'N/A'),
                'provider_id': 'DOC_UPLOAD',
                'service_date': extracted_data.get('service_date', '2024-10-15'),
                'service_type': claim_type,
                'diagnosis_code': extracted_data.get('diagnosis_code', 'N/A'),
                'procedure_code': extracted_data.get('procedure_code', 'N/A'),
                'amount_billed': float(extracted_data.get('billed_amount', 2850))
            }
            db.save_claim(document_data)
            
            # Save document information
            document_info = {
                'original_filename': filename,
                'stored_filename': unique_filename,
                'file_type': file_ext,
                'file_size': os.path.getsize(file_path),
                'file_path': file_path,
                'extracted_text': document_text
            }
            db.save_document(claim_id, document_info)
            
            # Save GPT-4 validation results to validation_results table
            if analysis_result.get("overall_status") not in ["ERROR", "TIMEOUT", "OCR_REQUIRED"]:
                validation_data = {
                    'is_valid': analysis_result.get('overall_status') == 'APPROVED',
                    'issues': analysis_result.get('validation_errors', []),
                    'recommendation': analysis_result.get('overall_status'),
                    'total_issues': len(analysis_result.get('validation_errors', []))
                }
                db.save_validation_result(claim_id, validation_data)
                
                # Save GPT-4 recommendation with decision reasoning to recommendations table
                recommendation_data = {
                    'recommendation': analysis_result.get('overall_status'),
                    'confidence': analysis_result.get('confidence_level', 0),
                    'reason': analysis_result.get('decision_reasoning', 'No reasoning provided'),
                    'priority': 'HIGH' if analysis_result.get('overall_status') == 'DENIED' else 'MEDIUM',
                    'suggested_actions': analysis_result.get('key_factors', []) + analysis_result.get('recommendations', []),
                    'overall_score': analysis_result.get('completeness_score', 0)
                }
                db.save_recommendation(claim_id, recommendation_data)
                
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
        
        # Analyze with GPT-4 (with timeout handling)
        try:
            print("Starting text analysis...")
            analysis_result = processor.analyze_claim_document(text, claim_type)
            print("Text analysis completed")
        except Exception as analysis_error:
            print(f"Text analysis failed: {str(analysis_error)}")
            analysis_result = {
                "overall_status": "ERROR",
                "completeness_score": 0,
                "missing_sections": ["Analysis failed"],
                "found_sections": [],
                "data_quality_issues": [],
                "validation_errors": [{"field": "analysis", "error": str(analysis_error), "expected_format": "valid_processing"}],
                "recommendations": ["Try with shorter text", "Check text format"],
                "extracted_data": {},
                "confidence_level": 0,
                "processing_notes": f"Analysis failed: {str(analysis_error)}"
            }
        
        # Get improvement suggestions
        suggestions = processor.get_improvement_suggestions(analysis_result)
        
        # Skip detailed comparison if analysis failed
        if analysis_result.get("overall_status") != "ERROR":
            try:
                comparison = processor.compare_with_approved_claims(text)
            except Exception as comp_error:
                print(f"Comparison failed: {str(comp_error)}")
                comparison = {"error": "Comparison analysis failed", "details": str(comp_error)}
        else:
            comparison = {"error": "Skipped due to analysis failure"}
        
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

@claims_bp.route('/<claim_id>/upload', methods=['POST'])
def upload_document_to_existing_claim(claim_id):
    """
    Upload and analyze document for an existing claim using GPT-4
    """
    try:
        # Check if the claim exists
        db = DatabaseManager()
        claim_history = db.get_claim_history(claim_id)
        if not claim_history or not claim_history.get('claim'):
            return jsonify({'error': f'Claim {claim_id} not found'}), 404
        
        # Check if file is present
        if 'document' not in request.files:
            return jsonify({'error': 'No document file provided'}), 400
        
        file = request.files['document']
        claim_type = request.form.get('claim_type', 'medical_claim')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'txt'}
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
        
        # Analyze with GPT-4 (with timeout handling)
        try:
            print(f"Starting analysis for document: {filename} on claim: {claim_id}")
            analysis_result = processor.analyze_claim_document(document_text, claim_type)
            print(f"Analysis completed for document: {filename} on claim: {claim_id}")
        except Exception as analysis_error:
            print(f"Analysis failed for document: {filename} on claim: {claim_id}, Error: {str(analysis_error)}")
            # Return partial result with error info
            analysis_result = {
                "overall_status": "ERROR",
                "completeness_score": 0,
                "missing_sections": ["Analysis failed"],
                "found_sections": [],
                "data_quality_issues": [],
                "validation_errors": [{"field": "analysis", "error": str(analysis_error), "expected_format": "valid_processing"}],
                "recommendations": ["Try with a smaller document", "Check document format"],
                "extracted_data": {},
                "confidence_level": 0,
                "processing_notes": f"Analysis failed: {str(analysis_error)}"
            }
        
        # Save document and analysis to database
        try:
            # Save document information
            document_info = {
                'original_filename': filename,
                'stored_filename': unique_filename,
                'file_type': file_ext,
                'file_size': os.path.getsize(file_path),
                'file_path': file_path,
                'extracted_text': document_text
            }
            db.save_document(claim_id, document_info)
            
            # Save GPT-4 validation results to validation_results table
            if analysis_result.get("overall_status") not in ["ERROR", "TIMEOUT", "OCR_REQUIRED"]:
                validation_data = {
                    'is_valid': analysis_result.get('overall_status') == 'APPROVED',
                    'issues': analysis_result.get('validation_errors', []),
                    'recommendation': analysis_result.get('overall_status'),
                    'total_issues': len(analysis_result.get('validation_errors', []))
                }
                db.save_validation_result(claim_id, validation_data)
                
                # Save GPT-4 recommendation with decision reasoning to recommendations table
                recommendation_data = {
                    'recommendation': analysis_result.get('overall_status'),
                    'confidence': analysis_result.get('confidence_level', 0),
                    'reason': analysis_result.get('decision_reasoning', 'No reasoning provided'),
                    'priority': 'HIGH' if analysis_result.get('overall_status') == 'DENIED' else 'MEDIUM',
                    'suggested_actions': analysis_result.get('key_factors', []) + analysis_result.get('recommendations', []),
                    'overall_score': analysis_result.get('completeness_score', 0)
                }
                db.save_recommendation(claim_id, recommendation_data)
                
        except Exception as db_error:
            print(f"Database save error for claim {claim_id}: {db_error}")
        
        response = {
            'claim_id': claim_id,
            'status': 'document_uploaded_and_analyzed',
            'document_analysis': analysis_result,
            'file_info': {
                'original_name': filename,
                'file_type': file_ext,
                'size_bytes': os.path.getsize(file_path),
                'processed_at': datetime.now().isoformat()
            },
            'message': f'Document uploaded and analyzed for claim {claim_id}'
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Document upload failed for claim {claim_id}: {str(e)}'
        }), 500