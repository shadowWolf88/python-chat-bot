# convert_version_history.py
"""
Convert VERSION_HISTORY.txt to JS array for APP_UPDATES in index.html
Usage: python3 convert_version_history.py > updates.js
"""
import re

input_file = 'VERSION_HISTORY.txt'

entries = []
with open(input_file, encoding='utf-8') as f:
    raw_entries = []
    for line in f:
        m = re.match(r"v[0-9a-f]+ \((\d{4}-\d{2}-\d{2})\): (.+)", line.strip())
        if m:
            date, msg = m.groups()
            # Use first sentence or up to 80 chars as title
            title = msg.split('.')[0].strip()
            if len(title) > 80:
                title = title[:77] + '...'
            changes = [msg.strip()]
            raw_entries.append({
                'date': date,
                'title': title,
                'changes': changes
            })

    # Assign version numbers oldest to newest
    version_major = 1
    version_minor = 0
    for entry in reversed(raw_entries):
        version = f"{version_major}.{version_minor}"
        version_minor += 1
        if version_minor >= 10:
            version_major += 1
            version_minor = 0
        entry['version'] = version
        entries.append(entry)
    entries.reverse()  # So newest is last in the output

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
