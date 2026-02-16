#!/usr/bin/env python3
"""
Fix remaining SQLite datetime functions and convert to PostgreSQL equivalents
"""

def fix_datetime_functions(filename):
    """Replace all SQLite datetime functions with PostgreSQL equivalents"""
    with open(filename, 'r') as f:
        content = f.read()
    
    original = content
    
    # Map of SQLite datetime functions to PostgreSQL equivalents
    replacements = {
        # SQLite: datetime('now', '-7 days') → PostgreSQL: CURRENT_TIMESTAMP - INTERVAL '7 days'
        "datetime('now', '-7 days')": "CURRENT_TIMESTAMP - INTERVAL '7 days'",
        "datetime('now', '-30 days')": "CURRENT_TIMESTAMP - INTERVAL '30 days'",
        "datetime('now', '-1 day')": "CURRENT_TIMESTAMP - INTERVAL '1 day'",
        "datetime('now', 'start of month')": "DATE_TRUNC('month', CURRENT_TIMESTAMP)",
        
        # SQLite: datetime('now') → PostgreSQL: CURRENT_TIMESTAMP
        "datetime('now')": "CURRENT_TIMESTAMP",
        
        # SQLite: date('now', 'localtime') → PostgreSQL: CURRENT_DATE
        "date('now', 'localtime')": "CURRENT_DATE",
        "date('now')": "CURRENT_DATE",
        
        # SQLite: date(...) function for date extraction → PostgreSQL: DATE(...)
        # Keep as is, but we need to handle datetime(col) → col
        
        # SQLite: strftime patterns
        "strftime('%Y-%m-%d', ": "TO_CHAR(",
    }
    
    for sqlite_func, pg_func in replacements.items():
        content = content.replace(sqlite_func, pg_func)
    
    # Handle datetime(column_name) → column_name (remove datetime() wrapper)
    # But be careful about CURRENT_TIMESTAMP
    import re
    content = re.sub(r'datetime\((\w+)\)', r'\1', content)
    
    # Handle date(entrestamp) = date('now', 'localtime') → DATE(entrestamp) = CURRENT_DATE
    content = re.sub(
        r"date\((\w+)\)\s*=\s*date\('now'(?:,\s*'[^']*')?\)",
        r"DATE(\1) = CURRENT_DATE",
        content
    )
    
    # Handle date(entrestamp) >= date('now', 'localtime') etc
    content = re.sub(
        r"date\((\w+)\)\s*(>=?|<=?|!=)\s*date\('now'(?:,\s*'[^']*')?\)",
        r"DATE(\1) \2 CURRENT_DATE",
        content
    )
    
    # Handle DATE(col) for simple date extraction
    content = re.sub(r'\bdate\((\w+)\)', r'DATE(\1)', content)
    
    if content != original:
        with open(filename, 'w') as f:
            f.write(content)
        return True
    return False

if __name__ == '__main__':
    for filename in ['api.py', 'training_data_manager.py']:
        try:
            if fix_datetime_functions(filename):
                print(f"✓ Fixed datetime functions in {filename}")
            else:
                print(f"✓ {filename} already clean")
        except Exception as e:
            print(f"✗ Error in {filename}: {e}")
