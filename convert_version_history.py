# convert_version_history.py
"""
Convert VERSION_HISTORY.txt to JS array for APP_UPDATES in index.html
Usage: python3 convert_version_history.py > updates.js
"""
import re

input_file = 'VERSION_HISTORY.txt'

entries = []
with open(input_file, encoding='utf-8') as f:
    for line in f:
        m = re.match(r"v[0-9a-f]+ \((\d{4}-\d{2}-\d{2})\): (.+)", line.strip())
        if m:
            date, msg = m.groups()
            # Try to extract a version number from the message, else use '1.0'
            version_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', msg)
            version = version_match.group(1) if version_match else '1.0'
            # Use first sentence or up to 80 chars as title
            title = msg.split('.')[0].strip()
            if len(title) > 80:
                title = title[:77] + '...'
            # Changes: split by ';' or '|' or keep as one
            changes = [msg.strip()]
            entries.append({
                'date': date,
                'version': version,
                'title': title,
                'changes': changes
            })

print('const APP_UPDATES = [')
for entry in entries:
    print('    {')
    print(f"        date: '{entry['date']}',")
    print(f"        version: '{entry['version']}',")
    print(f"        title: '{entry['title'].replace("'", "\\'")}',")
    print('        changes: [')
    for change in entry['changes']:
        print(f"            '{change.replace("'", "\\'")}',")
    print('        ]')
    print('    },')
print('];')
