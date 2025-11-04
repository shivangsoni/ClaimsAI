import sqlite3

def check_specific_claim(claim_id):
    conn = sqlite3.connect('database/claims_ai.db')
    cursor = conn.cursor()
    
    print(f"=== CHECKING CLAIM: {claim_id} ===")
    
    # Check claim details
    cursor.execute('SELECT * FROM claims WHERE claim_id = ?', (claim_id,))
    claim = cursor.fetchone()
    if claim:
        print(f"✅ Claim found: {claim[2]} - ${claim[12]} - {claim[9]}")
    else:
        print("❌ Claim not found")
        return
    
    # Check recommendations
    cursor.execute('SELECT * FROM recommendations WHERE claim_id = ?', (claim_id,))
    recommendations = cursor.fetchall()
    print(f"\n📋 Recommendations: {len(recommendations)}")
    for rec in recommendations:
        print(f"  - Decision: {rec[2]}")
        print(f"  - Confidence: {rec[3]}%") 
        print(f"  - Score: {rec[4]}%")
        print(f"  - Reason: {rec[6][:100]}...")
    
    # Check validations
    cursor.execute('SELECT * FROM validation_results WHERE claim_id = ?', (claim_id,))
    validations = cursor.fetchall()
    print(f"\n✓ Validations: {len(validations)}")
    for val in validations:
        print(f"  - Valid: {val[2]}")
        print(f"  - Recommendation: {val[3]}")
        print(f"  - Issues: {val[4]}")
    
    # Check documents
    cursor.execute('SELECT * FROM documents WHERE claim_id = ?', (claim_id,))
    documents = cursor.fetchall()
    print(f"\n📎 Documents: {len(documents)}")
    for doc in documents:
        print(f"  - File: {doc[2]} ({doc[4]} bytes)")
        print(f"  - Type: {doc[5]}")
        print(f"  - Path: {doc[7]}")
    
    conn.close()

if __name__ == "__main__":
    check_specific_claim("DOC_20251103_203114")