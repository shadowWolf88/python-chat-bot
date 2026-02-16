"""
Quick verification that all messaging endpoints are registered
"""
import subprocess
import json

# Get all registered routes
result = subprocess.run(
    ['python3', '-c', '''
import sys
sys.path.insert(0, ".")
from api import app

messaging_routes = {}
for rule in app.url_map.iter_rules():
    if "messages" in rule.rule and "api" in rule.rule:
        messaging_routes[rule.rule] = list(rule.methods - {"HEAD", "OPTIONS"})

for route, methods in sorted(messaging_routes.items()):
    print(f"{route:<50} {methods}")

print(f"\nTotal messaging endpoints: {len(messaging_routes)}")
'''],
    capture_output=True,
    text=True,
    cwd='/home/computer001/Documents/python chat bot'
)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
