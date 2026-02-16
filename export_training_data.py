#!/usr/bin/env python3
"""
DEPRECATED: Automated Training Data Export Script

This script is for reference only and is not currently used.
Training data export is handled by the TrainingDataManager class
and integrated into the Flask API.

Original usage:
    python3 export_training_data.py

Note: Uses legacy SQLite code - not updated for PostgreSQL migration.
"""

import sys
print("ERROR: This script is deprecated. Use TrainingDataManager directly via the Flask API.")
sys.exit(1)

# === Legacy SQLite code below - DO NOT USE ===
import sqlite3
from datetime import datetime
from training_data_manager import TrainingDataManager
import os

def main():
    """Export training data for all consented users"""
    print(f"\n{'='*60}")
    print(f"Training Data Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Initialize training manager
    try:
        manager = TrainingDataManager()
        print("✓ TrainingDataManager initialized")
    except Exception as e:
        print(f"✗ Failed to initialize TrainingDataManager: {e}")
        sys.exit(1)
    
    # Get all users from production database
    try:
        conn = sqlite3.connect('therapist_app.db')
        cur = conn.cursor()
        
        # Get all non-clinician users with consent
        users = cur.execute(
            """SELECT username, training_consent 
               FROM users 
               WHERE role='user' OR role IS NULL
               ORDER BY username"""
        ).fetchall()
        
        conn.close()
        print(f"✓ Found {len(users)} total users")
    except Exception as e:
        print(f"✗ Failed to query users: {e}")
        sys.exit(1)
    
    # Track statistics
    consented_count = 0
    exported_count = 0
    chat_success = 0
    pattern_success = 0
    outcome_success = 0
    errors = []
    
    # Process each user
    for username, training_consent in users:
        # Check if user has consented (both in DB and training manager)
        if not training_consent:
            continue
            
        if not manager.check_user_consent(username):
            continue
        
        consented_count += 1
        print(f"\n→ Processing user: {username[:3]}***")
        
        user_success = True
        
        # Export chat sessions
        try:
            success, msg = manager.export_chat_session(username)
            if success:
                chat_success += 1
                print(f"  ✓ Chats: {msg}")
            else:
                print(f"  ⚠ Chats: {msg}")
                user_success = False
        except Exception as e:
            print(f"  ✗ Chats failed: {e}")
            errors.append(f"{username}: chat export - {e}")
            user_success = False
        
        # Export therapy patterns
        try:
            success, msg = manager.export_therapy_patterns(username)
            if success:
                pattern_success += 1
                print(f"  ✓ Patterns: {msg}")
            else:
                print(f"  ⚠ Patterns: {msg}")
        except Exception as e:
            print(f"  ✗ Patterns failed: {e}")
            errors.append(f"{username}: pattern export - {e}")
            user_success = False
        
        # Export outcome data
        try:
            success, msg = manager.export_outcome_data(username)
            if success:
                outcome_success += 1
                print(f"  ✓ Outcomes: {msg}")
            else:
                print(f"  ⚠ Outcomes: {msg}")
        except Exception as e:
            print(f"  ✗ Outcomes failed: {e}")
            errors.append(f"{username}: outcome export - {e}")
            user_success = False
        
        if user_success:
            exported_count += 1
    
    # Get final statistics from training database
    try:
        stats = manager.get_training_stats()
    except Exception as e:
        print(f"\n✗ Failed to get statistics: {e}")
        stats = {}
    
    # Print summary
    print(f"\n{'='*60}")
    print("EXPORT SUMMARY")
    print(f"{'='*60}")
    print(f"Total users: {len(users)}")
    print(f"Consented users: {consented_count}")
    print(f"Successfully exported: {exported_count}")
    print(f"\nData exported:")
    print(f"  Chat sessions: {chat_success}/{consented_count}")
    print(f"  Therapy patterns: {pattern_success}/{consented_count}")
    print(f"  Outcome data: {outcome_success}/{consented_count}")
    
    if stats:
        print(f"\nTraining database totals:")
        print(f"  Total consented users: {stats.get('consented_users', 0)}")
        print(f"  Total chat messages: {stats.get('total_chat_messages', 0)}")
        print(f"  Total patterns: {stats.get('total_patterns', 0)}")
        print(f"  Total outcomes: {stats.get('total_outcomes', 0)}")
        print(f"  Audit entries: {stats.get('audit_entries', 0)}")
    
    if errors:
        print(f"\n⚠ ERRORS ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
    else:
        print(f"\n✓ No errors")
    
    print(f"\nCompleted at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Exit with error code if there were failures
    if errors:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
