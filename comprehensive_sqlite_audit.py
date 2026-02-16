#!/usr/bin/env python3
"""
COMPREHENSIVE SQLITE AUDIT & CLEANUP
Scans entire project for SQLite syntax, imports, and references
"""

import os
import re
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = '/home/computer001/Documents/python chat bot'
ISSUES_FOUND = defaultdict(list)

SQLITE_PATTERNS = {
    'imports': [
        (r'import\s+sqlite3', 'SQLite import'),
        (r'from\s+sqlite3', 'SQLite from import'),
    ],
    'connections': [
        (r'sqlite3\.connect\s*\(', 'SQLite direct connection'),
    ],
    'database_paths': [
        (r'DB_PATH\s*=', 'DB_PATH variable'),
        (r'PET_DB_PATH\s*=', 'PET_DB_PATH variable'),
        (r'TRAINING_DB_PATH\s*=', 'TRAINING_DB_PATH variable'),
        (r'get_db_path\s*\(', 'get_db_path function'),
        (r'get_pet_db_path\s*\(', 'get_pet_db_path function'),
    ],
    'sql_syntax': [
        (r'\.lastrowid', 'SQLite lastrowid'),
        (r'INSERT\s+OR\s+REPLACE', 'SQLite INSERT OR REPLACE'),
        (r'PRAGMA\s+', 'SQLite PRAGMA'),
        (r'sqlite_master', 'SQLite sqlite_master'),
    ],
}

def find_python_files():
    """Find all Python files"""
    python_files = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', 'env', 'backups'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return sorted(python_files)

def scan_file(filepath):
    """Scan file for SQLite issues"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        ISSUES_FOUND['read_errors'].append(f"{filepath}: {str(e)}")
        return
    
    relative_path = filepath.replace(PROJECT_ROOT, '').lstrip('/')
    
    for category, patterns in SQLITE_PATTERNS.items():
        for pattern, description in patterns:
            try:
                matches = list(re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE))
                if matches:
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        line_content = lines[line_num - 1] if line_num <= len(lines) else ''
                        
                        ISSUES_FOUND[category].append({
                            'file': relative_path,
                            'line': line_num,
                            'pattern': description,
                            'content': line_content.strip()[:100],
                        })
            except Exception:
                pass

def main():
    """Run audit"""
    print("=" * 100)
    print("COMPREHENSIVE SQLITE AUDIT")
    print("=" * 100)
    print()
    
    python_files = find_python_files()
    print(f"[*] Found {len(python_files)} Python files")
    print()
    
    print("[*] Scanning for SQLite patterns...")
    for filepath in python_files:
        scan_file(filepath)
    print()
    
    # Print results
    print("=" * 100)
    print("RESULTS")
    print("=" * 100)
    print()
    
    if not ISSUES_FOUND:
        print("✅ NO SQLITE ISSUES FOUND!")
        print("   Project is fully migrated to PostgreSQL")
        return 0
    
    total = 0
    for category in sorted(ISSUES_FOUND.keys()):
        issues = ISSUES_FOUND[category]
        if not issues:
            continue
        
        print(f"\n[{category.upper()}] {len(issues)} issue(s)")
        for issue in issues:
            total += 1
            print(f"  {total}. {issue['file']}:{issue['line']}")
            print(f"     {issue['pattern']}")
            print(f"     {issue['content']}")
    
    print()
    print("=" * 100)
    print(f"TOTAL: {total} SQLite issue(s) found")
    print("=" * 100)
    
    return 1 if total > 0 else 0

if __name__ == '__main__':
    exit(main())
