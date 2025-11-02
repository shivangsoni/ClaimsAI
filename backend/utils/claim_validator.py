import re
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any

class ClaimValidator:
    """
    Validates insurance claims and detects inconsistencies
    """
    
    def __init__(self):
        self.required_fields = [
            'patient_id', 'patient_name', 'date_of_birth', 'policy_number',
            'provider_name', 'provider_id', 'service_date', 'diagnosis_code',
            'procedure_code', 'amount_billed'
        ]
        
        self.date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        self.policy_pattern = r'^[A-Z0-9]{8,12}$'
        self.diagnosis_pattern = r'^[A-Z]\d{2}\.\d$'  # ICD-10 format
    
    def validate_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main validation method that checks for inconsistencies and missing data
        """
        issues = []
        missing_fields = []
        inconsistencies = []
        
        # Check for missing required fields
        for field in self.required_fields:
            if field not in claim_data or not claim_data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            issues.append({
                'type': 'missing_data',
                'severity': 'high',
                'fields': missing_fields,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            })
        
        # Validate data formats and consistency
        format_issues = self._validate_formats(claim_data)
        consistency_issues = self._check_consistency(claim_data)
        
        issues.extend(format_issues)
        issues.extend(consistency_issues)
        
        # Determine overall status
        has_critical_issues = any(issue['severity'] == 'high' for issue in issues)
        
        return {
            'is_valid': not has_critical_issues,
            'issues': issues,
            'total_issues': len(issues),
            'recommendation': self._get_recommendation(issues),
            'validation_timestamp': datetime.now().isoformat()
        }
    
    def _validate_formats(self, claim_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Validate data formats
        """
        format_issues = []
        
        # Validate dates
        date_fields = ['date_of_birth', 'service_date']
        for field in date_fields:
            if field in claim_data and claim_data[field]:
                if not re.match(self.date_pattern, str(claim_data[field])):
                    format_issues.append({
                        'type': 'format_error',
                        'severity': 'medium',
                        'field': field,
                        'message': f'{field} must be in YYYY-MM-DD format'
                    })
        
        # Validate policy number
        if 'policy_number' in claim_data and claim_data['policy_number']:
            if not re.match(self.policy_pattern, str(claim_data['policy_number'])):
                format_issues.append({
                    'type': 'format_error',
                    'severity': 'high',
                    'field': 'policy_number',
                    'message': 'Policy number format is invalid'
                })
        
        # Validate diagnosis code
        if 'diagnosis_code' in claim_data and claim_data['diagnosis_code']:
            if not re.match(self.diagnosis_pattern, str(claim_data['diagnosis_code'])):
                format_issues.append({
                    'type': 'format_error',
                    'severity': 'medium',
                    'field': 'diagnosis_code',
                    'message': 'Diagnosis code should follow ICD-10 format (e.g., A12.3)'
                })
        
        # Validate amount
        if 'amount_billed' in claim_data and claim_data['amount_billed']:
            try:
                amount = float(claim_data['amount_billed'])
                if amount <= 0:
                    format_issues.append({
                        'type': 'data_error',
                        'severity': 'high',
                        'field': 'amount_billed',
                        'message': 'Billed amount must be greater than zero'
                    })
                elif amount > 100000:  # Flag unusually high amounts
                    format_issues.append({
                        'type': 'data_warning',
                        'severity': 'low',
                        'field': 'amount_billed',
                        'message': 'Unusually high billed amount - please verify'
                    })
            except (ValueError, TypeError):
                format_issues.append({
                    'type': 'format_error',
                    'severity': 'high',
                    'field': 'amount_billed',
                    'message': 'Amount billed must be a valid number'
                })
        
        return format_issues
    
    def _check_consistency(self, claim_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check for logical inconsistencies in the data
        """
        consistency_issues = []
        
        # Check date consistency
        if 'date_of_birth' in claim_data and 'service_date' in claim_data:
            try:
                dob = datetime.strptime(claim_data['date_of_birth'], '%Y-%m-%d')
                service_date = datetime.strptime(claim_data['service_date'], '%Y-%m-%d')
                
                if service_date < dob:
                    consistency_issues.append({
                        'type': 'logical_error',
                        'severity': 'high',
                        'message': 'Service date cannot be before patient birth date'
                    })
                
                # Check if service date is in the future
                if service_date > datetime.now():
                    consistency_issues.append({
                        'type': 'logical_error',
                        'severity': 'medium',
                        'message': 'Service date is in the future'
                    })
                
                # Check patient age at service date
                age_at_service = (service_date - dob).days / 365.25
                if age_at_service > 120:
                    consistency_issues.append({
                        'type': 'data_warning',
                        'severity': 'medium',
                        'message': 'Patient age seems unusually high - please verify'
                    })
                
            except ValueError:
                pass  # Date format errors already caught in format validation
        
        # Check name consistency
        if 'patient_name' in claim_data and claim_data['patient_name']:
            name = str(claim_data['patient_name']).strip()
            if len(name.split()) < 2:
                consistency_issues.append({
                    'type': 'data_warning',
                    'severity': 'low',
                    'message': 'Patient name appears to be incomplete (missing first/last name)'
                })
        
        return consistency_issues
    
    def _get_recommendation(self, issues: List[Dict[str, Any]]) -> str:
        """
        Generate recommendation based on validation results
        """
        high_issues = [i for i in issues if i['severity'] == 'high']
        medium_issues = [i for i in issues if i['severity'] == 'medium']
        
        if high_issues:
            return "REJECT - Critical issues found. Return to submitter for correction."
        elif medium_issues:
            return "FLAG - Medium priority issues found. Manual review recommended."
        elif issues:
            return "APPROVE_WITH_NOTES - Minor issues noted but claim can proceed."
        else:
            return "APPROVE - No issues found."