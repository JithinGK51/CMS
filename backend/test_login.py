import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY") # anon key

def test_staff_login():
    supabase = create_client(URL, KEY)
    email = "rajeshmama4322@gmail.com"
    password = "Staff123"
    
    print(f"Testing login for {email}...")
    try:
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        print("✅ Login successful!")
        print(f"User ID: {res.user.id}")
    except Exception as e:
        print(f"❌ Login failed: {e}")

if __name__ == "__main__":
    test_staff_login()
