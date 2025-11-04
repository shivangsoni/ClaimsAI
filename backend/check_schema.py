import sqlite3

def check_schema():
    conn = sqlite3.connect('database/claims_ai.db')
    cursor = conn.cursor()
    
    # Check recommendations table schema
    cursor.execute("PRAGMA table_info(recommendations)")
    rec_columns = cursor.fetchall()
    print("=== RECOMMENDATIONS TABLE SCHEMA ===")
    for col in rec_columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Check documents table schema  
    cursor.execute("PRAGMA table_info(documents)")
    doc_columns = cursor.fetchall()
    print("\n=== DOCUMENTS TABLE SCHEMA ===")
    for col in doc_columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Check validation_results table schema
    cursor.execute("PRAGMA table_info(validation_results)")
    val_columns = cursor.fetchall()
    print("\n=== VALIDATION_RESULTS TABLE SCHEMA ===")
    for col in val_columns:
        print(f"  {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == "__main__":
    check_schema()