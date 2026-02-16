#!/usr/bin/env python3
"""
Replace all SQLite ? placeholders with PostgreSQL %s in api.py
"""
import re

def fix_sql_placeholders(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # Fix WHERE clauses: WHERE col = ? → WHERE col = %s
    content = re.sub(r'WHERE\s+(\w+)\s*=\s*\?', r'WHERE \1 = %s', content)
    
    # Fix AND clauses: AND col = ? → AND col = %s
    content = re.sub(r'AND\s+(\w+)\s*=\s*\?', r'AND \1 = %s', content)
    
    # Fix IN clauses: IN (?) → IN (%s)
    content = re.sub(r'IN\s*\(\s*\?\s*\)', 'IN (%s)', content)
    
    # Fix BETWEEN: BETWEEN ? AND ? → BETWEEN %s AND %s
    content = re.sub(r'BETWEEN\s+\?\s+AND\s+\?', 'BETWEEN %s AND %s', content)
    
    # Fix comparisons: > ? → > %s, < ? → < %s, etc.
    content = re.sub(r'([><=!]+)\s*\?', r'\1 %s', content)
    
    # Fix VALUES: VALUES (?, → VALUES (%s,
    content = re.sub(r'VALUES\s*\(\s*\?', 'VALUES (%s', content)
    
    # Fix remaining comma-separated: , ? → , %s
    content = re.sub(r',\s*\?', ', %s', content)
    
    with open(filename, 'w') as f:
        f.write(content)
    
    return True

if __name__ == '__main__':
    for filename in ['api.py', 'training_data_manager.py']:
        try:
            if fix_sql_placeholders(filename):
                print(f"✓ Fixed: {filename}")
        except Exception as e:
            print(f"✗ Error in {filename}: {e}")
