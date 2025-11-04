import sqlite3

def check_database():
    conn = sqlite3.connect('database/claims_ai.db')
    cursor = conn.cursor()
    
    # Check recent claims
    cursor.execute('SELECT claim_id, patient_name, status FROM claims ORDER BY created_at DESC LIMIT 5')
    claims = cursor.fetchall()
    print('Recent Claims:')
    for row in claims:
        print(f'  {row[0]} - {row[1]} - {row[2]}')
    
    # Check recommendations count
    cursor.execute('SELECT COUNT(*) FROM recommendations')
    rec_count = cursor.fetchone()[0]
    print(f'\nTotal Recommendations: {rec_count}')
    
    # Check validation_results count
    cursor.execute('SELECT COUNT(*) FROM validation_results')
    val_count = cursor.fetchone()[0]
    print(f'Total Validations: {val_count}')
    
    # Check specific recommendations
    if rec_count > 0:
        cursor.execute('SELECT claim_id, recommendation, confidence, overall_score FROM recommendations LIMIT 3')
        recommendations = cursor.fetchall()
        print('\nRecent Recommendations:')
        for row in recommendations:
            print(f'  Claim: {row[0]} - Decision: {row[1]} - Confidence: {row[2]}% - Score: {row[3]}%')
    
    # Check documents
    try:
        cursor.execute('SELECT COUNT(*) FROM documents')
        doc_count = cursor.fetchone()[0]
        print(f'\nTotal Documents: {doc_count}')
        
        if doc_count > 0:
            cursor.execute('SELECT claim_id, original_filename, file_type FROM documents ORDER BY upload_timestamp DESC LIMIT 3')
            documents = cursor.fetchall()
            print('\nRecent Documents:')
            for row in documents:
                print(f'  Claim: {row[0]} - File: {row[1]} - Type: {row[2]}')
    except Exception as e:
        print(f'\nDocuments table error: {e}')
    
    conn.close()

if __name__ == "__main__":
    check_database()