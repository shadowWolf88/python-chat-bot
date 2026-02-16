#!/usr/bin/env python3
"""
Script to remove secrets from git history by creating replacement commits.
This uses BFG-style approach with native git commands.
"""
import subprocess
import sys
import re

def run_git(cmd):
    """Run a git command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

# Create expressions file for secrets to remove
secrets_pattern = """
# Groq API keys pattern
regex:gsk_[A-Za-z0-9]{48,}==>REMOVED_SECRET
"""

with open('/tmp/secrets-patterns.txt', 'w') as f:
    f.write(secrets_pattern.strip())

print("🔍 Scanning git history for secrets...")
print("=" * 60)

# Use git filter-branch as fallback
print("\nUsing git filter-branch to rewrite history...")
print("This will create a backup at refs/original/")

cmd = """
git filter-branch --force --tree-filter '
    if [ -f main.py ]; then
        python3 << "PYEOF"
import re
try:
    with open("main.py", "r") as f:
        content = f.read()
    
    # Replace Groq API key pattern
    pattern = r'"'"'gsk_[A-Za-z0-9]{48,}'"'"'
    new_content = re.sub(pattern, '"'"'GROQ_API_KEY_REMOVED'"'"', content)
    
    if content != new_content:
        with open("main.py", "w") as f:
            f.write(new_content)
        print("Removed secret from main.py")
except Exception as e:
    print(f"Error: {e}")
PYEOF
    fi
' --prune-empty --tag-name-filter cat -- --all
"""

print("\n⚠️  WARNING: This will rewrite your git history!")
print("A backup will be created at refs/original/refs/heads/main")
response = input("\nContinue? (yes/no): ")

if response.lower() != 'yes':
    print("Aborted.")
    sys.exit(0)

print("\n🔄 Rewriting history...")
result = subprocess.run(cmd, shell=True, capture_output=False, text=True)

if result.returncode == 0:
    print("\n✅ History rewritten successfully!")
    print("\nNext steps:")
    print("1. Review the changes: git log --oneline")
    print("2. Force push to GitHub: git push --force origin main")
    print("\n⚠️  Note: Force push will overwrite remote history!")
    print("If you have collaborators, coordinate with them first.")
else:
    print(f"\n❌ Error during rewrite (exit code: {result.returncode})")
    print("You may need to clean up with: git filter-branch --abort")
