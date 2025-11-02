from flask import Blueprint, request, jsonify
from datetime import datetime
from utils.eligibility_checker import EligibilityChecker

eligibility_bp = Blueprint('eligibility', __name__)

@eligibility_bp.route('/check', methods=['POST'])
def check_eligibility():
    """
    Iteration 2: Evaluate whether a claim is eligible for coverage
    """
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                'error': 'No eligibility data provided'
            }), 400
        
        checker = EligibilityChecker()
        eligibility_result = checker.check_eligibility(request_data)
        
        return jsonify(eligibility_result), 200
    
    except Exception as e:
        return jsonify({
            'error': f'Eligibility check failed: {str(e)}'
        }), 500

@eligibility_bp.route('/policy/<policy_number>', methods=['GET'])
def get_policy_details(policy_number):
    """
    Get policy details for coverage verification
    """
    try:
        checker = EligibilityChecker()
        policy_details = checker.get_policy_details(policy_number)
        
        return jsonify(policy_details), 200
    
    except Exception as e:
        return jsonify({
            'error': f'Policy lookup failed: {str(e)}'
        }), 500