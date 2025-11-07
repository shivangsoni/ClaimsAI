#!/usr/bin/env python3
"""
Script to delete the claims table from the database
"""

import sqlite3
import os
from backend.utils.database import DatabaseManager

def delete_claims_table():
    """
    Delete the claims table and all related data
    """
    
    # Database paths to check
    db_paths = [
        'backend/database/claims_ai.db',
        'database/claims_ai.db',
        '../claims.db'
    ]
    
    deleted_count = 0
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"Processing database: {db_path}")
            
            try:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Check if claims table exists
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name='claims'
                    """)
                    
                    if cursor.fetchone():
                        # Get count of records before deletion
                        cursor.execute("SELECT COUNT(*) FROM claims")
                        record_count = cursor.fetchone()[0]
                        print(f"  Found claims table with {record_count} records")
                        
                        # Delete related data first (due to foreign keys)
                        tables_to_clean = [
                            'status_transitions',
                            'documents', 
                            'recommendations',
                            'reviewer_validations',
                            'eligibility_results',
                            'validation_results'
                        ]
                        
                        for table in tables_to_clean:
                            cursor.execute(f"DELETE FROM {table} WHERE claim_id IN (SELECT claim_id FROM claims)")
                            deleted_related = cursor.rowcount
                            if deleted_related > 0:
                                print(f"  Deleted {deleted_related} records from {table}")
                        
                        # Now delete the claims table
                        cursor.execute("DROP TABLE claims")
                        print(f"  ✅ Successfully dropped claims table")
                        
                        conn.commit()
                        deleted_count += 1
                        
                    else:
                        print(f"  ℹ️  Claims table not found in {db_path}")
                        
            except sqlite3.Error as e:
                print(f"  ❌ Error processing {db_path}: {e}")
    
    if deleted_count > 0:
        print(f"\n✅ Successfully deleted claims table from {deleted_count} database(s)")
        print("\n🔄 To recreate the table structure, run:")
        print("   python -c \"from backend.utils.database import DatabaseManager; DatabaseManager()\"")
    else:
        print("\n❌ No claims tables found to delete")

def delete_claims_data_only():
    """
    Delete all data from claims table but keep the structure
    """
    
    # Database paths to check
    db_paths = [
        'backend/database/claims_ai.db',
        'database/claims_ai.db', 
        '../claims.db'
    ]
    
    deleted_count = 0
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"Processing database: {db_path}")
            
            try:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Check if claims table exists
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name='claims'
                    """)
                    
                    if cursor.fetchone():
                        # Get count of records before deletion
                        cursor.execute("SELECT COUNT(*) FROM claims")
                        record_count = cursor.fetchone()[0]
                        print(f"  Found claims table with {record_count} records")
                        
                        if record_count > 0:
                            # Delete related data first (due to foreign keys)
                            tables_to_clean = [
                                'status_transitions',
                                'documents',
                                'recommendations', 
                                'reviewer_validations',
                                'eligibility_results',
                                'validation_results'
                            ]
                            
                            for table in tables_to_clean:
                                cursor.execute(f"DELETE FROM {table} WHERE claim_id IN (SELECT claim_id FROM claims)")
                                deleted_related = cursor.rowcount
                                if deleted_related > 0:
                                    print(f"  Deleted {deleted_related} records from {table}")
                            
                            # Delete all claims data
                            cursor.execute("DELETE FROM claims")
                            print(f"  ✅ Successfully deleted all {record_count} records from claims table")
                            
                            # Reset auto-increment counter
                            cursor.execute("DELETE FROM sqlite_sequence WHERE name='claims'")
                            
                            conn.commit()
                            deleted_count += 1
                        else:
                            print(f"  ℹ️  Claims table is already empty")
                            
                    else:
                        print(f"  ℹ️  Claims table not found in {db_path}")
                        
            except sqlite3.Error as e:
                print(f"  ❌ Error processing {db_path}: {e}")
    
    if deleted_count > 0:
        print(f"\n✅ Successfully deleted claims data from {deleted_count} database(s)")
        print("📋 Table structure preserved - ready for new data")
    else:
        print("\n❌ No claims data found to delete")

if __name__ == "__main__":
    print("Claims Table Deletion Tool")
    print("=" * 40)
    print("1. Drop entire table (structure + data)")
    print("2. Delete data only (keep structure)")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            confirm = input("\n⚠️  This will permanently delete the entire claims table. Continue? (yes/no): ").strip().lower()
            if confirm == "yes":
                delete_claims_table()
            else:
                print("Operation cancelled")
            break
            
        elif choice == "2":
            confirm = input("\n⚠️  This will delete all claims data but keep the table structure. Continue? (yes/no): ").strip().lower()
            if confirm == "yes":
                delete_claims_data_only()
            else:
                print("Operation cancelled")
            break
            
        elif choice == "3":
            print("Exiting...")
            break
            
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")