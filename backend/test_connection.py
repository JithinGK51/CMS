import os
import sys

# Add the current directory to sys.path so we can import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"Checking Connection...")
print(f"URL: {SUPABASE_URL}")
print(f"Key Present: {'Yes' if SUPABASE_KEY else 'No'}")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Missing SUPABASE_URL or SUPABASE_KEY in .env")
    sys.exit(1)

try:
    print("\n1️⃣ Initializing Supabase Client...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✔ Client Initialized")

    print("\n2️⃣ Testing Read Access (system_settings)...")
    res = supabase.table('system_settings').select("*").limit(1).execute()
    print(f"✔ Read Successful: Found {len(res.data)} record(s)")
    if len(res.data) > 0:
         print(f"   Data: {res.data[0]}")

    print("\n3️⃣ Testing Write Access (departments)...")
    # Using a test entry that we can delete later
    test_dept = {"name": "Test_Connection_Check_123"}
    
    # Insert
    res_insert = supabase.table('departments').insert(test_dept).execute()
    if res_insert.data:
        print("✔ Write Successful")
        inserted_id = res_insert.data[0]['id']
        
        # Cleanup (Delete)
        print("   Cleaning up test data...")
        supabase.table('departments').delete().eq('id', inserted_id).execute()
        print("✔ Cleanup Successful")
    else:
        print("❌ Write Failed: No data returned")

    print("\n✅ CONNECTION TEST PASSED!")

except Exception as e:
    print(f"\n❌ CONNECTION TEST FAILED: {str(e)}")
    # Check for specific hints
    if "401" in str(e) or "JWT" in str(e):
        print("💡 Hint: Your SUPABASE_KEY might be invalid or expired.")
    if "403" in str(e):
        print("💡 Hint: You might be using an Anon Key for a restricted operation. Admin operations need SERVICE_ROLE key.")
