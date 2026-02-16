#!/usr/bin/env python3
"""
Fix real SQLite issues in production code.
Ignores: venv, archived, test files, and refactor scripts.
"""
import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
SKIP_DIRS = {'.venv', '_archive', 'cleanenv', 'tests', 'legacy_desktop'}
SKIP_FILES = {'refactor_to_postgresql.py', 'phase5_step6_postgresql_fixes.py', 
              'comprehensive_sqlite_audit.py', 'fix_sqlite_issues.py',
              'ai_trainer.py', 'train_model.py'}  # Training/helper files

# Production code needing fixes
FIXES_NEEDED = {
    'api.py': [
        # Replace .lastrowid with RETURNING id
        (r'(\w+)\s*=\s*cur\.lastrowid', r'\1 = cur.fetchone()[0] if cur.rowcount == 1 else None'),
    ],
    'training_data_manager.py': [''
        # Replace sqlite3 connections with psycopg2
        (r'import sqlite3', r'import psycopg2'),
        (r'sqlite3\.connect\([^)]+\)', r'psycopg2.connect(os.getenv("DATABASE_URL"))'),
    ],
    'audit.py': [
        (r'import sqlite3', r'import psycopg2'),
        (r'conn\s*=\s*sqlite3\.connect\([^)]+\)', 
         r'conn = psycopg2.connect(os.getenv("DATABASE_URL"))'),
    ],
}

def should_process_file(filepath):
    """Check if file should be processed."""
    parts = filepath.relative_to(PROJECT_ROOT).parts
    if parts[0] in SKIP_DIRS:
        return False
    if filepath.name in SKIP_FILES:
        return False
    return filepath.suffix == '.py'

def fix_file(filepath):
    """Apply fixes to a single file."""
    if filepath.name not in FIXES_NEEDED:
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    fixes = FIXES_NEEDED[filepath.name]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    print("=" * 80)
    print("FIXING REAL SQLITE ISSUES IN PRODUCTION CODE")
    print("=" * 80)
    
    fixed_count = 0
    for filepath in PROJECT_ROOT.rglob('*.py'):
        if should_process_file(filepath):
            if fix_file(filepath):
                print(f"✓ Fixed: {filepath.relative_to(PROJECT_ROOT)}")
                fixed_count += 1
    
    print("=" * 80)
    print(f"Total files fixed: {fixed_count}")
    print("=" * 80)

if __name__ == '__main__':
    main()
