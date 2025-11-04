import sqlite3
from datetime import datetime

def add_gpt4_analysis_to_claim():
    claim_id = "CLM_20251103_202320"
    
    conn = sqlite3.connect('claims.db')
    cursor = conn.cursor()
    
    # Add recommendation record
    recommendation_data = {
        'claim_id': claim_id,
        'recommendation': 'APPROVED',
        'confidence': 95,
        'overall_score': 100,
        'priority': 'MEDIUM',
        'reason': 'The claim submitted by John Michael Smith is complete and meets all necessary criteria for approval. The incident occurred within the policy coverage dates, and the details provided align with the documentation submitted, including a police report and photos of the damage. There are no red flags present, such as citations or indications of fraud. The estimated repair cost of $2,850.00 is reasonable given the nature of the damages described, which are consistent with a minor rear-end collision. Overall, the claim adheres to standard insurance practices and poses no significant risk to the insurer.',
        'suggested_actions': '["Incident occurred within policy coverage dates", "Complete documentation including police report and damage assessment", "No citations or indications of fault on the policyholder\'s part", "Reasonable repair costs aligned with the damages reported", "No signs of fraudulent activity"]',
        'created_at': datetime.now().isoformat()
    }
    
    cursor.execute('''
        INSERT INTO recommendations (claim_id, recommendation, confidence, overall_score, priority, reason, suggested_actions, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        recommendation_data['claim_id'],
        recommendation_data['recommendation'],
        recommendation_data['confidence'],
        recommendation_data['overall_score'],
        recommendation_data['priority'],
        recommendation_data['reason'],
        recommendation_data['suggested_actions'],
        recommendation_data['created_at']
    ))
    
    # Add validation record
    validation_data = {
        'claim_id': claim_id,
        'is_valid': 1,
        'recommendation': 'APPROVED',
        'issues': '[]',
        'total_issues': 0,
        'created_at': datetime.now().isoformat()
    }
    
    cursor.execute('''
        INSERT INTO validation_results (claim_id, is_valid, recommendation, issues, total_issues, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        validation_data['claim_id'],
        validation_data['is_valid'],
        validation_data['recommendation'],
        validation_data['issues'],
        validation_data['total_issues'],
        validation_data['created_at']
    ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Added GPT-4 analysis results for claim {claim_id}")
    print("- Recommendation: APPROVED")
    print("- Confidence: 95%")
    print("- Completeness: 100%")
    print("- Decision reasoning added")

if __name__ == "__main__":
    add_gpt4_analysis_to_claim()