#!/usr/bin/env python3
"""
Comprehensive fix for all REAL SQLite issues in production code.
- Converts ? placeholders to %s (PostgreSQL)
- Converts .lastrowid to RETURNING id
- Updates sqlite3 imports to psycopg2
- Adds os import where needed
"""
import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Target only production files (not tests, not archives, not refactor scripts)
PRODUCTION_FILES = {
    'api.py',
    'audit.py',
    'training_data_manager.py',
}

def fix_lastrowid_pattern(content):
    """
    Fix .lastrowid patterns. Examples:
    
    Before:
        cur.execute("INSERT ... VALUES (...)")
        conn.commit()
        chat_session_id = cur.lastrowid
    
    After:
        cur.execute("INSERT ... VALUES (...) RETURNING id", ...)
        chat_session_id = cur.fetchone()[0]
    """
    # Pattern 1: cur.lastrowid assignment
    # This captures multi-line INSERT + commit + lastrowid
    pattern1 = r'cur\.execute\(\s*"(INSERT[^"]+)"\s*,\s*\(([^)]*)\)\s*\)\s*conn\.commit\(\)\s*(\w+)\s*=\s*cur\.lastrowid'
    
    def replace1(match):
        insert_stmt = match.group(1)
        params = match.group(2)
        var_name = match.group(3)
        # Add RETURNING id to INSERT
        if 'RETURNING' not in insert_stmt:
            insert_stmt = insert_stmt.rstrip() + ' RETURNING id'
        return f'cur.execute(\n                "{insert_stmt}",\n                ({params})\n            )\n            {var_name} = cur.fetchone()[0]'
    
    content = re.sub(pattern1, replace1, content, flags=re.DOTALL)
    
    # Pattern 2: Simple cur.lastrowid (as fallback for missed cases)
    content = re.sub(
        r'(\w+)\s*=\s*cur\.lastrowid',
        r'\1 = cur.fetchone()[0] if cur.rowcount >= 1 else None',
        content
    )
    
    return content

def fix_placeholders(content):
    """Convert SQLite ? placeholders to PostgreSQL %s."""
    # Be careful: only replace in SQL strings, not in comments
    
    # Pattern: VALUES (?, ?, ...) or WHERE ... = ?
    # This handles most common cases
    lines = content.split('\n')
    fixed_lines = []
    in_string = False
    
    for line in lines:
        if 'VALUES (?' in line or 'WHERE' in line and '= ?' in line:
            # Simple replacement for VALUES and WHERE clauses
            line = line.replace('(?, ', '(%s, ')
            line = line.replace(', ?)', ', %s)')
            line = line.replace('= ?', '= %s')
            line = line.replace('(? )', '(%s)')
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_sqlite_import(content):
    """Replace import sqlite3 with import psycopg2."""
    if 'import sqlite3' in content and 'psycopg2' not in content:
        content = content.replace('import sqlite3', 'import psycopg2')
        # Add os import if not present
        if 'import os' not in content:
            # Find first import and add after it
            content = re.sub(
                r'(^import [^\n]+\n)',
                r'\1import os\n',
                content,
                count=1,
                flags=re.MULTILINE
            )
    return content

def fix_sqlite_connections(content):
    """Replace sqlite3.connect() with psycopg2.connect()."""
    # Pattern: sqlite3.connect(...)
    pattern = r'sqlite3\.connect\s*\(\s*["\']([^"\']+)["\']\s*\)'
    replacement = r'psycopg2.connect(os.getenv("DATABASE_URL"))'
    content = re.sub(pattern, replacement, content)
    return content

def process_file(filepath):
    """Apply all fixes to a production file."""
    print(f"\nProcessing: {filepath.name}")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Apply fixes in order
    print(f"  - Fixing .lastrowid patterns...")
    content = fix_lastrowid_pattern(content)
    
    print(f"  - Fixing ? placeholders...")
    content = fix_placeholders(content)
    
    print(f"  - Fixing sqlite3 imports...")
    content = fix_sqlite_import(content)
    
    print(f"  - Fixing sqlite3 connections...")
    content = fix_sqlite_connections(content)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  ✓ File updated")
        return True
    else:
        print(f"  - No changes needed")
        return False

def main():
    print("=" * 80)
    print("FIXING REAL SQLITE ISSUES IN PRODUCTION CODE")
    print("=" * 80)
    
    fixed_count = 0
    for filename in PRODUCTION_FILES:
        filepath = PROJECT_ROOT / filename
        if filepath.exists():
            if process_file(filepath):
                fixed_count += 1
    
    print("\n" + "=" * 80)
    print(f"✓ Fixed {fixed_count} production files")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Run audit again: python3 comprehensive_sqlite_audit.py")
    print("2. Review changes: git diff")
    print("3. Test: pytest -v tests/")
    print("4. Commit: git add -A && git commit -m 'fix: Convert all SQLite to PostgreSQL'")
    print("=" * 80)

if __name__ == '__main__':
    main()
