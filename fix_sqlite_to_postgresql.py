#!/usr/bin/env python3
"""
Convert SQLite parameter placeholders (?) to PostgreSQL placeholders (%s)
in api.py and other files using PostgreSQL
"""
import re

def fix_file(filepath):
    """Convert ? to %s in SQL queries"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern to match SQL strings with ? placeholders
    # This regex finds execute() calls with SQL strings containing ?
    
    # We need to be careful to only replace ? inside SQL strings
    # Split by execute( and process each part
    
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Only process lines with execute( or executemany(
        if 'execute(' not in line and 'executemany(' not in line:
            fixed_lines.append(line)
            continue
        
        # Check if this line contains a string with ?
        if '?' not in line:
            fixed_lines.append(line)
            continue
        
        # Replace ? with %s but only in SQL strings
        # Match patterns like "... WHERE x=?" or 'VALUES (?, ?, ?)'
        # Count the number of ? in this line
        question_count = line.count('?')
        
        # Replace ? with %s
        # But we need to be smart about it - only in SQL contexts
        new_line = line
        
        # Find all string literals in the line and replace ? only in them
        # This is a simple approach: replace ? with %s
        # The execute() call will have tuple with correct number of args
        
        # Pattern: anything in quotes followed by ?, replace with %s
        # Being careful not to replace in comments
        
        if '#' in line:
            # Split by comment
            code_part, comment_part = line.split('#', 1)
            code_part = code_part.replace('?', '%s')
            new_line = code_part + '#' + comment_part
        else:
            new_line = line.replace('?', '%s')
        
        fixed_lines.append(new_line)
    
    fixed_content = '\n'.join(fixed_lines)
    
    if fixed_content != original_content:
        with open(filepath, 'w') as f:
            f.write(fixed_content)
        return True
    return False

# Fix api.py
print("Fixing api.py...")
if fix_file('/home/computer001/Documents/python chat bot/api.py'):
    print("✅ api.py fixed")
else:
    print("⚠️  api.py had no changes")

# Fix audit.py
print("Fixing audit.py...")
if fix_file('/home/computer001/Documents/python chat bot/audit.py'):
    print("✅ audit.py fixed")
else:
    print("⚠️  audit.py had no changes")

# Fix fhir_export.py
print("Fixing fhir_export.py...")
if fix_file('/home/computer001/Documents/python chat bot/fhir_export.py'):
    print("✅ fhir_export.py fixed")
else:
    print("⚠️  fhir_export.py had no changes")

# Fix training_data_manager.py
print("Fixing training_data_manager.py...")
if fix_file('/home/computer001/Documents/python chat bot/training_data_manager.py'):
    print("✅ training_data_manager.py fixed")
else:
    print("⚠️  training_data_manager.py had no changes")

print("\n✅ All files processed!")
