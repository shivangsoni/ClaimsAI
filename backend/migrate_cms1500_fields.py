"""
Database migration script to add CMS-1500 form fields to existing claims table.
This script adds new columns without losing existing data.
"""
import sqlite3
import os

def migrate_database():
    """
    Add CMS-1500 form fields to the claims table
    """
    db_path = 'database/claims_ai.db'
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Database will be created on first run.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(claims)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    
    # Define new columns to add
    new_columns = [
        ('insurance_type', 'TEXT'),
        ('patient_sex', 'TEXT'),
        ('insured_name', 'TEXT'),
        ('patient_address', 'TEXT'),
        ('patient_city', 'TEXT'),
        ('patient_state', 'TEXT'),
        ('patient_zip', 'TEXT'),
        ('patient_relationship', 'TEXT'),
        ('insured_address', 'TEXT'),
        ('insured_city', 'TEXT'),
        ('insured_state', 'TEXT'),
        ('insured_zip', 'TEXT'),
        ('patient_ssn', 'TEXT'),
        ('policy_group_number', 'TEXT'),
        ('illness_injury_date', 'DATE'),
        ('referring_provider_name', 'TEXT'),
        ('referring_provider_npi', 'TEXT'),
        ('diagnosis_code_2', 'TEXT'),
        ('diagnosis_code_3', 'TEXT'),
        ('diagnosis_code_4', 'TEXT'),
        ('service_lines', 'TEXT'),
        ('procedure_code_2', 'TEXT'),
        ('procedure_modifier', 'TEXT'),
        ('procedure_modifier_2', 'TEXT'),
        ('procedure_modifier_3', 'TEXT'),
        ('procedure_modifier_4', 'TEXT'),
        ('diagnosis_pointer', 'TEXT'),
        ('days_units', 'TEXT'),
        ('rendering_provider_npi', 'TEXT'),
        ('physician_signature', 'TEXT'),
        ('physician_signature_date', 'DATE'),
        ('provider_npi', 'TEXT'),
        ('provider_address', 'TEXT'),
        ('provider_city', 'TEXT'),
        ('provider_state', 'TEXT'),
        ('provider_zip', 'TEXT'),
        ('provider_tax_id', 'TEXT'),
        ('notes', 'TEXT'),
    ]
    
    # Add columns that don't exist
    added_count = 0
    for column_name, column_type in new_columns:
        if column_name not in existing_columns:
            try:
                cursor.execute(f'ALTER TABLE claims ADD COLUMN {column_name} {column_type}')
                print(f"Added column: {column_name}")
                added_count += 1
            except sqlite3.OperationalError as e:
                print(f"Error adding column {column_name}: {e}")
    
    conn.commit()
    conn.close()
    
    if added_count > 0:
        print(f"\nMigration completed! Added {added_count} new columns.")
    else:
        print("\nNo new columns needed. Database is up to date.")

if __name__ == "__main__":
    migrate_database()

