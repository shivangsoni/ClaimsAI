from flask import Blueprint, request, jsonify
from datetime import datetime
from utils.recommendation_engine import RecommendationEngine

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/generate', methods=['POST'])
def generate_recommendation():
    """
    Iteration 3: Generate recommendations for human reviewers
    """
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                'error': 'No recommendation data provided'
            }), 400
        
        engine = RecommendationEngine()
        recommendation = engine.generate_recommendation(request_data)
        
        return jsonify(recommendation), 200
    
    except Exception as e:
        return jsonify({
            'error': f'Recommendation generation failed: {str(e)}'
        }), 500

@recommendations_bp.route('/history/<claim_id>', methods=['GET'])
def get_recommendation_history(claim_id):
    """
    Get recommendation history for a specific claim
    """
    try:
        engine = RecommendationEngine()
        history = engine.get_recommendation_history(claim_id)
        
        return jsonify(history), 200
    
    except Exception as e:
        return jsonify({
            'error': f'History lookup failed: {str(e)}'
        }), 500

@recommendations_bp.route('/validate', methods=['POST'])
def validate_recommendation():
    """
    Allow human reviewers to validate or override recommendations
    """
    try:
        validation_data = request.get_json()
        
        engine = RecommendationEngine()
        result = engine.validate_recommendation(validation_data)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({
            'error': f'Validation failed: {str(e)}'
        }), 500