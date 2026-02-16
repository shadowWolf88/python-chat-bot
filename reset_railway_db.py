"""
Reset Railway Database - Delete All Users for Testing
"""
import requests
import sys

# Your Railway deployment URL
RAILWAY_URL = input("Enter your Railway URL (e.g., https://your-app.railway.app): ").strip()

if not RAILWAY_URL:
    print("Error: Railway URL is required")
    sys.exit(1)

# Remove trailing slash if present
RAILWAY_URL = RAILWAY_URL.rstrip('/')

print(f"\n⚠️  WARNING: This will DELETE ALL USERS from {RAILWAY_URL}")
print("This includes:")
print("  - All patient accounts")
print("  - All clinician accounts")
print("  - All mood logs, chat history, assessments")
print("  - All patient approvals and notifications")
print()

confirm = input("Type 'DELETE_ALL_USERS' to confirm: ").strip()

if confirm != "DELETE_ALL_USERS":
    print("❌ Cancelled. You must type 'DELETE_ALL_USERS' exactly.")
    sys.exit(0)

print("\n🔄 Sending reset request to Railway...")

try:
    response = requests.post(
        f"{RAILWAY_URL}/api/admin/reset-users",
        json={"confirm": "DELETE_ALL_USERS"},
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS!")
        print(f"   Users remaining: {data.get('users_remaining', 0)}")
        print(f"   Approvals remaining: {data.get('approvals_remaining', 0)}")
        print(f"   Message: {data.get('message')}")
    else:
        print(f"\n❌ ERROR: {response.status_code}")
        print(f"   {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"\n❌ Connection Error: {e}")
    print("\nMake sure:")
    print("  1. Your Railway URL is correct")
    print("  2. Your Railway app is deployed and running")
    print("  3. The /api/admin/reset-users endpoint exists")
