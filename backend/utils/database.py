import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    """
    SQLite Database manager for Claims AI system
    """
    
    def __init__(self, db_path='database/claims_ai.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """
        Initialize database and create tables
        """
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create claims table with CMS-1500 form fields
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS claims (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    claim_id TEXT UNIQUE NOT NULL,
                    -- Field 1: Insurance Type
                    insurance_type TEXT,
                    -- Field 2: Patient's Name (Last, First, Middle Initial)
                    patient_name TEXT NOT NULL,
                    patient_id TEXT NOT NULL,
                    -- Field 3: Patient's Birth Date and Sex
                    date_of_birth DATE NOT NULL,
                    patient_sex TEXT,
                    -- Field 4: Insured's Name
                    insured_name TEXT,
                    -- Field 5: Patient's Address
                    patient_address TEXT,
                    patient_city TEXT,
                    patient_state TEXT,
                    patient_zip TEXT,
                    -- Field 6: Patient Relationship to Insured
                    patient_relationship TEXT,
                    -- Field 7: Insured's Address
                    insured_address TEXT,
                    insured_city TEXT,
                    insured_state TEXT,
                    insured_zip TEXT,
                    -- Field 9: Patient's SSN
                    patient_ssn TEXT,
                    -- Field 11: Insured's Policy Group or FECA Number
                    policy_number TEXT NOT NULL,
                    policy_group_number TEXT,
                    -- Field 14: Date of Current Illness/Injury/Pregnancy
                    illness_injury_date DATE,
                    -- Field 17: Referring Provider's Name and NPI
                    referring_provider_name TEXT,
                    referring_provider_npi TEXT,
                    -- Field 21: Diagnosis Codes (up to 4)
                    diagnosis_code TEXT NOT NULL,
                    diagnosis_code_2 TEXT,
                    diagnosis_code_3 TEXT,
                    diagnosis_code_4 TEXT,
                    -- Field 24A-H: Service line items (stored as JSON for multiple services)
                    service_lines TEXT, -- JSON string for multiple service dates, procedures, etc.
                    -- Common service fields (for backward compatibility)
                    service_date DATE NOT NULL,
                    service_type TEXT,
                    procedure_code TEXT NOT NULL,
                    procedure_code_2 TEXT,
                    procedure_modifier TEXT,
                    procedure_modifier_2 TEXT,
                    procedure_modifier_3 TEXT,
                    procedure_modifier_4 TEXT,
                    -- Field 24F: Diagnosis Pointer
                    diagnosis_pointer TEXT,
                    -- Field 24G: Days or Units
                    days_units TEXT,
                    -- Field 24J: Rendering Provider NPI
                    rendering_provider_npi TEXT,
                    -- Field 28: Total Charge
                    amount_billed DECIMAL(10,2) NOT NULL,
                    -- Field 31: Signature of Physician or Supplier
                    physician_signature TEXT,
                    physician_signature_date DATE,
                    -- Field 33: Billing Provider Information
                    provider_name TEXT NOT NULL,
                    provider_id TEXT NOT NULL,
                    provider_npi TEXT,
                    provider_address TEXT,
                    provider_city TEXT,
                    provider_state TEXT,
                    provider_zip TEXT,
                    provider_tax_id TEXT,
                    -- Additional fields
                    status TEXT DEFAULT 'submitted',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create policies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS policies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    policy_number TEXT UNIQUE NOT NULL,
                    policy_holder TEXT NOT NULL,
                    policy_type TEXT NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    deductible DECIMAL(10,2) NOT NULL,
                    max_coverage DECIMAL(12,2) NOT NULL,
                    covered_services TEXT, -- JSON string
                    excluded_services TEXT, -- JSON string
                    copay_percentage DECIMAL(4,3) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create validation_results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS validation_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    claim_id TEXT NOT NULL,
                    is_valid BOOLEAN NOT NULL,
                    issues TEXT, -- JSON string
                    recommendation TEXT,
                    total_issues INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (claim_id) REFERENCES claims (claim_id)
                )
            ''')
            
            # Create eligibility_results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS eligibility_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    claim_id TEXT,
                    policy_number TEXT NOT NULL,
                    eligible BOOLEAN NOT NULL,
                    checks TEXT, -- JSON string
                    coverage_calculation TEXT, -- JSON string
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (claim_id) REFERENCES claims (claim_id)
                )
            ''')
            
            # Create recommendations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    claim_id TEXT,
                    recommendation TEXT NOT NULL,
                    confidence INTEGER NOT NULL,
                    reason TEXT,
                    priority TEXT,
                    suggested_actions TEXT, -- JSON string
                    overall_score DECIMAL(5,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (claim_id) REFERENCES claims (claim_id)
                )
            ''')
            
            # Create reviewer_validations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reviewer_validations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    claim_id TEXT NOT NULL,
                    recommendation_id INTEGER,
                    reviewer_decision TEXT NOT NULL,
                    reviewer_notes TEXT,
                    reviewer_id TEXT NOT NULL,
                    ai_recommendation TEXT,
                    agreement BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (claim_id) REFERENCES claims (claim_id),
                    FOREIGN KEY (recommendation_id) REFERENCES recommendations (id)
                )
            ''')
            
            # Create documents table for storing uploaded files
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    claim_id TEXT NOT NULL,
                    original_filename TEXT NOT NULL,
                    stored_filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER,
                    file_path TEXT NOT NULL,
                    extracted_text TEXT,
                    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (claim_id) REFERENCES claims (claim_id)
                )
            ''')
            
            conn.commit()
            self.insert_sample_data()
    
    def insert_sample_data(self):
        """
        Insert sample policies for testing
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if sample data already exists
            cursor.execute("SELECT COUNT(*) FROM policies")
            if cursor.fetchone()[0] > 0:
                return  # Sample data already exists
            
            # Insert sample policies
            sample_policies = [
                (
                    'POL12345678', 'John Doe', 'comprehensive',
                    '2023-01-01', '2024-12-31', 500.00, 50000.00,
                    '["emergency", "surgery", "diagnostics", "pharmacy"]',
                    '["cosmetic", "experimental"]', 0.20
                ),
                (
                    'POL87654321', 'Jane Smith', 'basic',
                    '2023-06-01', '2024-05-31', 1000.00, 25000.00,
                    '["emergency", "diagnostics"]',
                    '["surgery", "cosmetic", "experimental"]', 0.30
                ),
                (
                    'POL11111111', 'Bob Johnson', 'premium',
                    '2023-01-01', '2025-12-31', 250.00, 100000.00,
                    '["emergency", "surgery", "diagnostics", "pharmacy", "mental_health"]',
                    '["cosmetic"]', 0.10
                )
            ]
            
            cursor.executemany('''
                INSERT INTO policies 
                (policy_number, policy_holder, policy_type, start_date, end_date,
                 deductible, max_coverage, covered_services, excluded_services, copay_percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_policies)
            
            conn.commit()
    
    def get_connection(self):
        """
        Get database connection
        """
        return sqlite3.connect(self.db_path)
    
    def save_claim(self, claim_data):
        """
        Save claim to database with CMS-1500 form fields
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO claims 
                (claim_id, insurance_type, patient_id, patient_name, date_of_birth, patient_sex,
                 insured_name, patient_address, patient_city, patient_state, patient_zip,
                 patient_relationship, insured_address, insured_city, insured_state, insured_zip,
                 patient_ssn, policy_number, policy_group_number, illness_injury_date,
                 referring_provider_name, referring_provider_npi,
                 diagnosis_code, diagnosis_code_2, diagnosis_code_3, diagnosis_code_4,
                 service_lines, service_date, service_type,
                 procedure_code, procedure_code_2, procedure_modifier, procedure_modifier_2,
                 procedure_modifier_3, procedure_modifier_4, diagnosis_pointer, days_units,
                 rendering_provider_npi, amount_billed,
                 physician_signature, physician_signature_date,
                 provider_name, provider_id, provider_npi, provider_address, provider_city,
                 provider_state, provider_zip, provider_tax_id, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                claim_data.get('claim_id'),
                claim_data.get('insurance_type'),
                claim_data.get('patient_id'),
                claim_data.get('patient_name'),
                claim_data.get('date_of_birth'),
                claim_data.get('patient_sex'),
                claim_data.get('insured_name'),
                claim_data.get('patient_address'),
                claim_data.get('patient_city'),
                claim_data.get('patient_state'),
                claim_data.get('patient_zip'),
                claim_data.get('patient_relationship'),
                claim_data.get('insured_address'),
                claim_data.get('insured_city'),
                claim_data.get('insured_state'),
                claim_data.get('insured_zip'),
                claim_data.get('patient_ssn'),
                claim_data.get('policy_number'),
                claim_data.get('policy_group_number'),
                claim_data.get('illness_injury_date'),
                claim_data.get('referring_provider_name'),
                claim_data.get('referring_provider_npi'),
                claim_data.get('diagnosis_code'),
                claim_data.get('diagnosis_code_2'),
                claim_data.get('diagnosis_code_3'),
                claim_data.get('diagnosis_code_4'),
                claim_data.get('service_lines'),  # JSON string
                claim_data.get('service_date'),
                claim_data.get('service_type'),
                claim_data.get('procedure_code'),
                claim_data.get('procedure_code_2'),
                claim_data.get('procedure_modifier'),
                claim_data.get('procedure_modifier_2'),
                claim_data.get('procedure_modifier_3'),
                claim_data.get('procedure_modifier_4'),
                claim_data.get('diagnosis_pointer'),
                claim_data.get('days_units'),
                claim_data.get('rendering_provider_npi'),
                claim_data.get('amount_billed'),
                claim_data.get('physician_signature'),
                claim_data.get('physician_signature_date'),
                claim_data.get('provider_name'),
                claim_data.get('provider_id'),
                claim_data.get('provider_npi'),
                claim_data.get('provider_address'),
                claim_data.get('provider_city'),
                claim_data.get('provider_state'),
                claim_data.get('provider_zip'),
                claim_data.get('provider_tax_id'),
                claim_data.get('notes')
            ))
            
            conn.commit()
    
    def get_policy(self, policy_number):
        """
        Get policy by policy number
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM policies WHERE policy_number = ?', (policy_number,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def save_validation_result(self, claim_id, validation_result):
        """
        Save validation result to database
        """
        import json
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO validation_results 
                (claim_id, is_valid, issues, recommendation, total_issues)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                claim_id,
                validation_result.get('is_valid', False),
                json.dumps(validation_result.get('issues', [])),
                validation_result.get('recommendation'),
                validation_result.get('total_issues', 0)
            ))
            
            conn.commit()
    
    def save_eligibility_result(self, claim_id, policy_number, eligibility_result):
        """
        Save eligibility result to database
        """
        import json
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO eligibility_results 
                (claim_id, policy_number, eligible, checks, coverage_calculation)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                claim_id,
                policy_number,
                eligibility_result.get('eligible', False),
                json.dumps(eligibility_result.get('checks', [])),
                json.dumps(eligibility_result.get('coverage_calculation', {}))
            ))
            
            conn.commit()
    
    def save_recommendation(self, claim_id, recommendation):
        """
        Save AI recommendation to database
        """
        import json
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO recommendations 
                (claim_id, recommendation, confidence, reason, priority, 
                 suggested_actions, overall_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                claim_id,
                recommendation.get('recommendation'),
                recommendation.get('confidence'),
                recommendation.get('reason'),
                recommendation.get('priority'),
                json.dumps(recommendation.get('suggested_actions', [])),
                recommendation.get('overall_score')
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def save_reviewer_validation(self, validation_data):
        """
        Save reviewer validation to database
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO reviewer_validations 
                (claim_id, reviewer_decision, reviewer_notes, reviewer_id,
                 ai_recommendation, agreement)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                validation_data.get('claim_id'),
                validation_data.get('reviewer_decision'),
                validation_data.get('reviewer_notes'),
                validation_data.get('reviewer_id'),
                validation_data.get('ai_recommendation'),
                validation_data.get('agreement')
            ))
            
            conn.commit()
    
    def get_claim_history(self, claim_id):
        """
        Get complete history for a claim
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get claim details
            cursor.execute('SELECT * FROM claims WHERE claim_id = ?', (claim_id,))
            claim = cursor.fetchone()
            
            if not claim:
                return None
            
            # Get validation results
            cursor.execute('SELECT * FROM validation_results WHERE claim_id = ? ORDER BY created_at', (claim_id,))
            validations = [dict(row) for row in cursor.fetchall()]
            
            # Get eligibility results
            cursor.execute('SELECT * FROM eligibility_results WHERE claim_id = ? ORDER BY created_at', (claim_id,))
            eligibility = [dict(row) for row in cursor.fetchall()]
            
            # Get recommendations
            cursor.execute('SELECT * FROM recommendations WHERE claim_id = ? ORDER BY created_at', (claim_id,))
            recommendations = [dict(row) for row in cursor.fetchall()]
            
            # Get reviewer validations
            cursor.execute('SELECT * FROM reviewer_validations WHERE claim_id = ? ORDER BY created_at', (claim_id,))
            reviews = [dict(row) for row in cursor.fetchall()]
            
            # Get documents
            cursor.execute('SELECT * FROM documents WHERE claim_id = ? ORDER BY upload_timestamp', (claim_id,))
            documents = [dict(row) for row in cursor.fetchall()]
            
            return {
                'claim': dict(claim),
                'validations': validations,
                'eligibility': eligibility,
                'recommendations': recommendations,
                'reviews': reviews,
                'documents': documents
            }

    def save_document(self, claim_id, document_info):
        """
        Save document information to database
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO documents 
                (claim_id, original_filename, stored_filename, file_type, 
                 file_size, file_path, extracted_text)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                claim_id,
                document_info['original_filename'],
                document_info['stored_filename'], 
                document_info['file_type'],
                document_info['file_size'],
                document_info['file_path'],
                document_info.get('extracted_text', '')
            ))
            
            conn.commit()
            return cursor.lastrowid

    def get_documents_for_claim(self, claim_id):
        """
        Get all documents for a specific claim
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM documents WHERE claim_id = ? ORDER BY upload_timestamp', (claim_id,))
            return [dict(row) for row in cursor.fetchall()]

# Initialize database when module is imported
if __name__ == '__main__':
    db = DatabaseManager()
    print("Database initialized successfully!")