from datetime import datetime, timedelta
from typing import Dict, List, Any

class EligibilityChecker:
    """
    Checks eligibility for insurance claims based on policy and patient data
    """
    
    def __init__(self):
        # Use database for policy lookup
        from utils.database import DatabaseManager
        self.db = DatabaseManager()
    
    def check_eligibility(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main eligibility checking method
        """
        policy_number = claim_data.get('policy_number')
        service_type = claim_data.get('service_type', 'general')
        service_date = claim_data.get('service_date')
        amount_billed = float(claim_data.get('amount_billed', 0))
        
        # Get policy details
        policy = self.get_policy_details(policy_number)
        
        if 'error' in policy:
            return {
                'eligible': False,
                'reason': 'Policy not found or invalid',
                'details': policy
            }
        
        # Check eligibility criteria
        eligibility_checks = []
        
        # 1. Check policy active status
        active_check = self._check_policy_active(policy, service_date)
        eligibility_checks.append(active_check)
        
        # 2. Check service coverage
        service_check = self._check_service_coverage(policy, service_type)
        eligibility_checks.append(service_check)
        
        # 3. Check coverage limits
        limit_check = self._check_coverage_limits(policy, amount_billed)
        eligibility_checks.append(limit_check)
        
        # 4. Check deductible and copay
        cost_check = self._calculate_patient_costs(policy, amount_billed)
        eligibility_checks.append(cost_check)
        
        # Determine overall eligibility
        is_eligible = all(check['passed'] for check in eligibility_checks if check['critical'])
        
        # Calculate coverage amounts
        coverage_calculation = self._calculate_coverage(policy, amount_billed, is_eligible)
        
        return {
            'eligible': is_eligible,
            'policy_number': policy_number,
            'checks': eligibility_checks,
            'coverage_calculation': coverage_calculation,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_policy_details(self, policy_number: str) -> Dict[str, Any]:
        """
        Retrieve policy details by policy number
        """
        if not policy_number:
            return {
                'error': 'Policy number required',
                'policy_number': policy_number
            }
        
        policy = self.db.get_policy(policy_number)
        
        if not policy:
            return {
                'error': 'Policy not found',
                'policy_number': policy_number
            }
        
        # Convert JSON strings back to lists
        import json
        try:
            policy['covered_services'] = json.loads(policy.get('covered_services', '[]'))
            policy['excluded_services'] = json.loads(policy.get('excluded_services', '[]'))
        except json.JSONDecodeError:
            policy['covered_services'] = []
            policy['excluded_services'] = []
        
        return policy
    
    def _check_policy_active(self, policy: Dict[str, Any], service_date: str) -> Dict[str, Any]:
        """
        Check if policy is active on service date
        """
        try:
            service_dt = datetime.strptime(service_date, '%Y-%m-%d')
            start_dt = datetime.strptime(policy['start_date'], '%Y-%m-%d')
            end_dt = datetime.strptime(policy['end_date'], '%Y-%m-%d')
            
            is_active = start_dt <= service_dt <= end_dt
            
            return {
                'check_type': 'policy_active',
                'passed': is_active,
                'critical': True,
                'message': 'Policy is active' if is_active else f'Policy not active on {service_date}',
                'details': {
                    'policy_start': policy['start_date'],
                    'policy_end': policy['end_date'],
                    'service_date': service_date
                }
            }
        except ValueError:
            return {
                'check_type': 'policy_active',
                'passed': False,
                'critical': True,
                'message': 'Invalid date format',
                'details': {}
            }
    
    def _check_service_coverage(self, policy: Dict[str, Any], service_type: str) -> Dict[str, Any]:
        """
        Check if the service type is covered by the policy
        """
        covered_services = policy.get('covered_services', [])
        excluded_services = policy.get('excluded_services', [])
        
        is_covered = service_type.lower() in [s.lower() for s in covered_services]
        is_excluded = service_type.lower() in [s.lower() for s in excluded_services]
        
        if is_excluded:
            return {
                'check_type': 'service_coverage',
                'passed': False,
                'critical': True,
                'message': f'Service type "{service_type}" is explicitly excluded',
                'details': {
                    'service_type': service_type,
                    'excluded_services': excluded_services
                }
            }
        elif is_covered:
            return {
                'check_type': 'service_coverage',
                'passed': True,
                'critical': True,
                'message': f'Service type "{service_type}" is covered',
                'details': {
                    'service_type': service_type,
                    'covered_services': covered_services
                }
            }
        else:
            return {
                'check_type': 'service_coverage',
                'passed': False,
                'critical': True,
                'message': f'Service type "{service_type}" is not in covered services',
                'details': {
                    'service_type': service_type,
                    'covered_services': covered_services
                }
            }
    
    def _check_coverage_limits(self, policy: Dict[str, Any], amount_billed: float) -> Dict[str, Any]:
        """
        Check if the claim amount is within policy limits
        """
        max_coverage = policy.get('max_coverage', 0)
        
        within_limit = amount_billed <= max_coverage
        
        return {
            'check_type': 'coverage_limits',
            'passed': within_limit,
            'critical': True,
            'message': f'Amount within coverage limit' if within_limit else f'Amount exceeds maximum coverage of ${max_coverage:,.2f}',
            'details': {
                'amount_billed': amount_billed,
                'max_coverage': max_coverage,
                'excess_amount': max(0, amount_billed - max_coverage)
            }
        }
    
    def _calculate_patient_costs(self, policy: Dict[str, Any], amount_billed: float) -> Dict[str, Any]:
        """
        Calculate patient's deductible and copay responsibilities
        """
        deductible = policy.get('deductible', 0)
        copay_percentage = policy.get('copay_percentage', 0)
        
        # Simplified calculation - assumes deductible not yet met
        amount_after_deductible = max(0, amount_billed - deductible)
        patient_copay = amount_after_deductible * copay_percentage
        insurance_pays = amount_after_deductible - patient_copay
        
        return {
            'check_type': 'cost_calculation',
            'passed': True,
            'critical': False,
            'message': 'Patient cost calculation completed',
            'details': {
                'amount_billed': amount_billed,
                'deductible_amount': min(amount_billed, deductible),
                'copay_amount': patient_copay,
                'insurance_pays': insurance_pays,
                'patient_total': min(amount_billed, deductible) + patient_copay
            }
        }
    
    def _calculate_coverage(self, policy: Dict[str, Any], amount_billed: float, is_eligible: bool) -> Dict[str, Any]:
        """
        Calculate final coverage amounts
        """
        if not is_eligible:
            return {
                'approved_amount': 0,
                'patient_responsibility': amount_billed,
                'insurance_payment': 0,
                'coverage_percentage': 0
            }
        
        deductible = policy.get('deductible', 0)
        copay_percentage = policy.get('copay_percentage', 0)
        max_coverage = policy.get('max_coverage', amount_billed)
        
        # Calculate covered amount
        covered_amount = min(amount_billed, max_coverage)
        amount_after_deductible = max(0, covered_amount - deductible)
        patient_copay = amount_after_deductible * copay_percentage
        insurance_payment = amount_after_deductible - patient_copay
        patient_total = min(covered_amount, deductible) + patient_copay
        
        coverage_percentage = (insurance_payment / amount_billed * 100) if amount_billed > 0 else 0
        
        return {
            'approved_amount': covered_amount,
            'patient_responsibility': patient_total,
            'insurance_payment': insurance_payment,
            'coverage_percentage': round(coverage_percentage, 2),
            'deductible_applied': min(covered_amount, deductible),
            'copay_applied': patient_copay
        }