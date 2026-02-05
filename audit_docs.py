import os
import re
from pathlib import Path

ROOT = "/home/computer001/Documents/python chat bot"
DOC_EXTENSIONS = {'.md', '.txt', '.rst', '.docx'}

# Files to ignore
IGNORE_FILES = {
    'cookies.txt', 'temp.txt', 'requirements.txt', 'requirements-pinned.txt',
    'requirements-training.txt', 'VERSION_HISTORY_FORMATTED.js', 'Full_History_riksta.txt'
}

docs = {}

# Scan root directory
for file in os.listdir(ROOT):
    if not os.path.isfile(os.path.join(ROOT, file)):
        continue
    
    name, ext = os.path.splitext(file)
    if ext.lower() not in DOC_EXTENSIONS:
        continue
    
    if file in IGNORE_FILES:
        continue
    
    filepath = os.path.join(ROOT, file)
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            size = len(content)
            lines = len(content.split('\n'))
            # Extract first 100 chars
            summary = content[:200].replace('\n', ' ')[:200]
            
            docs[file] = {
                'path': filepath,
                'type': 'root',
                'size': size,
                'lines': lines,
                'summary': summary
            }
    except Exception as e:
        pass

# Scan documentation folder
doc_folder = os.path.join(ROOT, 'documentation')
for root, dirs, files in os.walk(doc_folder):
    for file in files:
        name, ext = os.path.splitext(file)
        if ext.lower() not in DOC_EXTENSIONS:
            continue
        
        filepath = os.path.join(root, file)
        rel_path = os.path.relpath(filepath, ROOT)
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                size = len(content)
                lines = len(content.split('\n'))
                summary = content[:200].replace('\n', ' ')[:200]
                
                docs[rel_path] = {
                    'path': filepath,
                    'type': 'subfolder',
                    'size': size,
                    'lines': lines,
                    'summary': summary
                }
        except Exception as e:
            pass

# Count and categorize
print(f"\n📊 DOCUMENTATION AUDIT REPORT")
print(f"=" * 70)
print(f"\nTotal Documents: {len(docs)}")
print(f"Root-level docs: {sum(1 for d in docs.values() if d['type'] == 'root')}")
print(f"Subfolder docs: {sum(1 for d in docs.values() if d['type'] == 'subfolder')}")

print(f"\n\n📁 ROOT-LEVEL DOCUMENTATION ({sum(1 for d in docs.values() if d['type'] == 'root')} files):")
print("-" * 70)
for filename in sorted([f for f in docs if docs[f]['type'] == 'root']):
    d = docs[filename]
    print(f"  • {filename}")
    print(f"    Lines: {d['lines']:,} | Size: {d['size']:,} bytes")
    print(f"    Preview: {d['summary'][:100]}...")
    print()

print(f"\n📁 DOCUMENTATION/ SUBFOLDER FILES ({sum(1 for d in docs.values() if d['type'] == 'subfolder')} files):")
print("-" * 70)

# Group by subfolder
subfolders = {}
for filepath in sorted([f for f in docs if docs[f]['type'] == 'subfolder']):
    parts = filepath.split(os.sep)
    if len(parts) > 2:
        subfolder = parts[1]
    else:
        subfolder = 'root'
    
    if subfolder not in subfolders:
        subfolders[subfolder] = []
    subfolders[subfolder].append(filepath)

for subfolder in sorted(subfolders.keys()):
    print(f"\n  📂 {subfolder}/ ({len(subfolders[subfolder])} files)")
    for filepath in subfolders[subfolder]:
        d = docs[filepath]
        filename = os.path.basename(filepath)
        print(f"    • {filename}")
        print(f"      Lines: {d['lines']:,} | Size: {d['size']:,} bytes")

print(f"\n\n💾 TOTAL SIZE: {sum(d['size'] for d in docs.values()):,} bytes")
print(f"=" * 70)
