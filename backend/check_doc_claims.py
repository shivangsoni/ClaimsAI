import sqlite3

conn = sqlite3.connect('database/claims_ai.db')
cursor = conn.cursor()

print('=== Recent Document Claims ===')
cursor.execute("SELECT claim_id, patient_name, created_at FROM claims WHERE claim_id LIKE 'DOC_%' ORDER BY created_at DESC LIMIT 3")
recent_docs = cursor.fetchall()

for doc in recent_docs:
    print(f'Claim: {doc[0]} - Patient: {doc[1]} - Created: {doc[2]}')

print('\n=== Checking Recommendations for Latest Document ===')
if recent_docs:
    latest_claim = recent_docs[0][0]
    cursor.execute("SELECT recommendation, confidence, reason, overall_score FROM recommendations WHERE claim_id = ?", (latest_claim,))
    recommendations = cursor.fetchall()
    
    print(f'Found {len(recommendations)} recommendations for {latest_claim}')
    for rec in recommendations:
        print(f'  Recommendation: {rec[0]}')
        print(f'  Confidence: {rec[1]}%')
        print(f'  Score: {rec[3]}%')
        print(f'  Reasoning: {rec[2][:100]}...' if rec[2] else 'No reasoning')

print('\n=== Checking Validations for Latest Document ===')
if recent_docs:
    cursor.execute("SELECT is_valid, recommendation, total_issues FROM validation_results WHERE claim_id = ?", (latest_claim,))
    validations = cursor.fetchall()
    
    print(f'Found {len(validations)} validations for {latest_claim}')
    for val in validations:
        print(f'  Valid: {val[0]}')
        print(f'  Recommendation: {val[1]}')
        print(f'  Issues: {val[2]}')

conn.close()