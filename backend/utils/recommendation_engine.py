from datetime import datetime
from typing import Dict, List, Any
import json

class RecommendationEngine:
    """
    Generates recommendations for insurance claim processing
    """
    
    def __init__(self):
        # Mock recommendation history storage
        self.recommendation_history = {}
        
        # Scoring weights for different factors
        self.scoring_weights = {
            'validation_score': 0.4,
            'eligibility_score': 0.3,
            'amount_risk': 0.2,
            'historical_data': 0.1
        }
    
    def generate_recommendation(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a recommendation based on validation and eligibility results
        """
        claim_data = request_data.get('claim_data', {})
        validation_result = request_data.get('validation_result', {})
        eligibility_result = request_data.get('eligibility_result', {})
        
        # Calculate individual scores
        validation_score = self._calculate_validation_score(validation_result)
        eligibility_score = self._calculate_eligibility_score(eligibility_result)
        amount_risk_score = self._calculate_amount_risk_score(claim_data)
        historical_score = self._calculate_historical_score(claim_data)
        
        # Calculate overall confidence score
        overall_score = (
            validation_score * self.scoring_weights['validation_score'] +
            eligibility_score * self.scoring_weights['eligibility_score'] +
            amount_risk_score * self.scoring_weights['amount_risk'] +
            historical_score * self.scoring_weights['historical_data']
        )
        
        # Generate recommendation based on score
        recommendation = self._determine_recommendation(
            overall_score, validation_result, eligibility_result
        )
        
        # Store recommendation in history
        claim_id = claim_data.get('claim_id', f"CLM_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self._store_recommendation(claim_id, recommendation)
        
        return recommendation
    
    def _calculate_validation_score(self, validation_result: Dict[str, Any]) -> float:
        """
        Calculate score based on validation results (0-100)
        """
        if not validation_result or 'issues' not in validation_result:
            return 50.0  # Neutral score if no validation data
        
        issues = validation_result['issues']
        
        if not issues:
            return 100.0  # Perfect score for no issues
        
        # Deduct points based on issue severity
        score = 100.0
        for issue in issues:
            severity = issue.get('severity', 'medium')
            if severity == 'high':
                score -= 30
            elif severity == 'medium':
                score -= 15
            elif severity == 'low':
                score -= 5
        
        return max(0.0, score)
    
    def _calculate_eligibility_score(self, eligibility_result: Dict[str, Any]) -> float:
        """
        Calculate score based on eligibility results (0-100)
        """
        if not eligibility_result:
            return 50.0  # Neutral score if no eligibility data
        
        if not eligibility_result.get('eligible', False):
            return 0.0  # Zero score if not eligible
        
        # Check individual eligibility checks
        checks = eligibility_result.get('checks', [])
        if not checks:
            return 70.0  # Default score if eligible but no detailed checks
        
        passed_critical = sum(1 for check in checks if check.get('critical', False) and check.get('passed', False))
        total_critical = sum(1 for check in checks if check.get('critical', False))
        
        if total_critical == 0:
            return 70.0
        
        return (passed_critical / total_critical) * 100
    
    def _calculate_amount_risk_score(self, claim_data: Dict[str, Any]) -> float:
        """
        Calculate risk score based on claim amount (0-100, higher is less risky)
        """
        try:
            amount = float(claim_data.get('amount_billed', 0))
        except (ValueError, TypeError):
            return 50.0  # Neutral score for invalid amount
        
        # Risk thresholds
        if amount <= 500:
            return 90.0  # Low risk
        elif amount <= 2000:
            return 75.0  # Medium-low risk
        elif amount <= 10000:
            return 60.0  # Medium risk
        elif amount <= 50000:
            return 40.0  # High risk
        else:
            return 20.0  # Very high risk
    
    def _calculate_historical_score(self, claim_data: Dict[str, Any]) -> float:
        """
        Calculate score based on historical claim patterns
        Mock implementation - in real system, would analyze past claims
        """
        # Mock historical analysis
        provider_id = claim_data.get('provider_id', '')
        patient_id = claim_data.get('patient_id', '')
        
        # Simple mock scoring based on provider/patient patterns
        score = 70.0  # Default neutral score
        
        # Mock: providers with certain patterns get different scores
        if provider_id.startswith('PROV_HIGH'):
            score = 90.0  # High trust provider
        elif provider_id.startswith('PROV_LOW'):
            score = 40.0  # Lower trust provider
        
        return score
    
    def _determine_recommendation(self, overall_score: float, validation_result: Dict[str, Any], 
                                 eligibility_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine final recommendation based on overall score and specific conditions
        """
        # Check for immediate rejection conditions
        if not eligibility_result.get('eligible', False):
            return {
                'recommendation': 'REJECT',
                'confidence': 95,
                'reason': 'Claim is not eligible for coverage',
                'priority': 'high',
                'suggested_actions': ['Notify claimant of ineligibility', 'Provide appeal process information'],
                'overall_score': overall_score,
                'timestamp': datetime.now().isoformat()
            }
        
        # Check for critical validation issues
        validation_issues = validation_result.get('issues', [])
        critical_issues = [issue for issue in validation_issues if issue.get('severity') == 'high']
        
        if critical_issues:
            return {
                'recommendation': 'RETURN_FOR_CORRECTION',
                'confidence': 90,
                'reason': 'Critical validation issues require correction',
                'priority': 'high',
                'suggested_actions': [
                    'Return claim to submitter',
                    f'Request correction of: {", ".join([issue.get("field", "unknown") for issue in critical_issues])}'
                ],
                'overall_score': overall_score,
                'issues_to_correct': critical_issues,
                'timestamp': datetime.now().isoformat()
            }
        
        # Score-based recommendations
        if overall_score >= 85:
            return {
                'recommendation': 'AUTO_APPROVE',
                'confidence': 95,
                'reason': 'High confidence in claim validity and eligibility',
                'priority': 'low',
                'suggested_actions': ['Process payment automatically'],
                'overall_score': overall_score,
                'timestamp': datetime.now().isoformat()
            }
        elif overall_score >= 70:
            return {
                'recommendation': 'APPROVE_WITH_REVIEW',
                'confidence': 80,
                'reason': 'Good confidence but recommend quick human review',
                'priority': 'medium',
                'suggested_actions': ['Quick supervisor review', 'Process if no concerns'],
                'overall_score': overall_score,
                'timestamp': datetime.now().isoformat()
            }
        elif overall_score >= 50:
            return {
                'recommendation': 'MANUAL_REVIEW',
                'confidence': 60,
                'reason': 'Moderate risk requires detailed manual review',
                'priority': 'medium',
                'suggested_actions': [
                    'Detailed claim review',
                    'Verify documentation',
                    'Contact provider if needed'
                ],
                'overall_score': overall_score,
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'recommendation': 'INTENSIVE_REVIEW',
                'confidence': 75,
                'reason': 'High risk claim requires intensive investigation',
                'priority': 'high',
                'suggested_actions': [
                    'Senior adjuster review',
                    'Verify all documentation',
                    'Investigate potential fraud indicators',
                    'Contact all parties for verification'
                ],
                'overall_score': overall_score,
                'timestamp': datetime.now().isoformat()
            }
    
    def _store_recommendation(self, claim_id: str, recommendation: Dict[str, Any]):
        """
        Store recommendation in history
        """
        if claim_id not in self.recommendation_history:
            self.recommendation_history[claim_id] = []
        
        self.recommendation_history[claim_id].append(recommendation)
    
    def get_recommendation_history(self, claim_id: str) -> Dict[str, Any]:
        """
        Retrieve recommendation history for a claim
        """
        history = self.recommendation_history.get(claim_id, [])
        
        return {
            'claim_id': claim_id,
            'recommendation_count': len(history),
            'recommendations': history,
            'timestamp': datetime.now().isoformat()
        }
    
    def validate_recommendation(self, validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Allow human reviewers to validate or override AI recommendations
        """
        claim_id = validation_data.get('claim_id')
        reviewer_decision = validation_data.get('reviewer_decision')
        reviewer_notes = validation_data.get('reviewer_notes', '')
        reviewer_id = validation_data.get('reviewer_id', 'unknown')
        
        # Store validation result
        validation_record = {
            'claim_id': claim_id,
            'reviewer_decision': reviewer_decision,
            'reviewer_notes': reviewer_notes,
            'reviewer_id': reviewer_id,
            'validation_timestamp': datetime.now().isoformat()
        }
        
        # Update recommendation history
        if claim_id in self.recommendation_history:
            latest_recommendation = self.recommendation_history[claim_id][-1]
            ai_recommendation = latest_recommendation.get('recommendation')
            
            # Check if reviewer agreed with AI
            agreement = (ai_recommendation.lower() == reviewer_decision.lower())
            
            validation_record['ai_recommendation'] = ai_recommendation
            validation_record['agreement'] = agreement
            
            # Store validation
            self.recommendation_history[claim_id].append({
                'type': 'human_validation',
                **validation_record
            })
        
        return {
            'status': 'validation_recorded',
            'validation_record': validation_record,
            'timestamp': datetime.now().isoformat()
        }