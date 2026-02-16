#!/usr/bin/env python3
"""
Production SQLite fix - handles:
1. ? placeholders → %s
2. .lastrowid → RETURNING id + fetchone()[0]
3. sqlite3 imports → psycopg2
4. sqlite3.connect() calls
"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

def fix_api_py():
    """Fix api.py - the main file with all the issues."""
    api_file = PROJECT_ROOT / 'api.py'
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = 0
    
    # FIX 1: Convert ? to %s in INSERT statements
    # Pattern: VALUES (?, 'literal', 1) → VALUES (%s, 'literal', 1)
    content = re.sub(r'VALUES\s*\(\?', 'VALUES (%s', content)
    if content != original:
        changes += 1
        print("✓ Fixed ? placeholders in INSERT statements")
    
    # FIX 2: Convert .lastrowid to RETURNING id with fetchone()
    # Pattern: INSERT ... VALUES (...) ... commit() ... var = cur.lastrowid
    # We need to add RETURNING id to INSERT and change assignment
    
    # Find all lastrowid patterns and the INSERT before them
    lastrowid_pattern = r'cur\.execute\(\s*"(INSERT[^"]*VALUES\s*\([^)]*\))"\s*,\s*(\([^)]*\))\s*\)\s*conn\.commit\(\)\s*(\w+)\s*=\s*cur\.lastrowid'
    
    def replace_lastrowid(match):
        insert_part = match.group(1)
        params = match.group(2)
        var_name = match.group(3)
        
        # Add RETURNING id if not present
        if 'RETURNING' not in insert_part:
            insert_part = insert_part.rstrip() + ' RETURNING id'
        
        return (f'cur.execute(\n'
                f'                "{insert_part}",\n'
                f'                {params}\n'
                f'            )\n'
                f'            {var_name} = cur.fetchone()[0]')
    
    new_content = re.sub(lastrowid_pattern, replace_lastrowid, content, flags=re.DOTALL)
    if new_content != content:
        content = new_content
        changes += 1
        print("✓ Fixed .lastrowid patterns (added RETURNING id)")
    
    # FIX 3: Fallback - simple cur.lastrowid → cur.fetchone()[0]
    content = re.sub(r'(\w+)\s*=\s*cur\.lastrowid\b', r'\1 = cur.fetchone()[0]', content)
    
    if content != original:
        with open(api_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✓ api.py fixed successfully")
        return True
    else:
        print("\n✗ api.py: No changes needed")
        return False

def fix_training_data_manager():
    """Fix training_data_manager.py - has sqlite3 imports and connections."""
    file = PROJECT_ROOT / 'training_data_manager.py'
    if not file.exists():
        return False
    
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # FIX 1: Replace import sqlite3 with psycopg2
    if 'import sqlite3' in content:
        content = content.replace('import sqlite3', 'import psycopg2')
        print("✓ Replaced import sqlite3 with psycopg2")
    
    # FIX 2: Add os import if not present
    if 'import os' not in content:
        content = re.sub(
            r'^(import [^\n]+)',
            r'\1\nimport os',
            content,
            count=1,
            flags=re.MULTILINE
        )
        print("✓ Added import os")
    
    # FIX 3: Replace sqlite3.connect() with psycopg2.connect()
    content = re.sub(
        r'sqlite3\.connect\s*\(\s*["\']([^"\']+)["\']\s*\)',
        r'psycopg2.connect(os.getenv("DATABASE_URL"))',
        content
    )
    if content != original:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✓ training_data_manager.py fixed successfully")
        return True
    else:
        print("\n✗ training_data_manager.py: No changes needed")
        return False

def fix_audit_py():
    """Fix audit.py - has sqlite3 imports."""
    file = PROJECT_ROOT / 'audit.py'
    if not file.exists():
        return False
    
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # FIX: Replace import sqlite3 with psycopg2
    if 'import sqlite3' in content:
        content = content.replace('import sqlite3', 'import psycopg2')
        print("✓ Replaced import sqlite3 with psycopg2")
    
    # FIX: Add os import if not present
    if 'import os' not in content:
        content = re.sub(
            r'^(import [^\n]+)',
            r'\1\nimport os',
            content,
            count=1,
            flags=re.MULTILINE
        )
        print("✓ Added import os")
    
    # FIX: Replace sqlite3.connect() with psycopg2.connect()
    content = re.sub(
        r'sqlite3\.connect\s*\(\s*["\']([^"\']+)["\']\s*\)',
        r'psycopg2.connect(os.getenv("DATABASE_URL"))',
        content
    )
    
    if content != original:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✓ audit.py fixed successfully")
        return True
    else:
        print("\n✗ audit.py: No changes needed")
        return False

def main():
    print("=" * 80)
    print("FIXING PRODUCTION SQLITE ISSUES")
    print("=" * 80)
    
    fixed = []
    
    print("\n[1] Fixing api.py...")
    if fix_api_py():
        fixed.append('api.py')
    
    print("\n[2] Fixing training_data_manager.py...")
    if fix_training_data_manager():
        fixed.append('training_data_manager.py')
    
    print("\n[3] Fixing audit.py...")
    if fix_audit_py():
        fixed.append('audit.py')
    
    print("\n" + "=" * 80)
    if fixed:
        print(f"✓ Fixed {len(fixed)} files: {', '.join(fixed)}")
        print("\nNext: python3 comprehensive_sqlite_audit.py")
    else:
        print("No production files needed fixing")
    print("=" * 80)

if __name__ == '__main__':
    main()
