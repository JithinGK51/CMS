import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def reset_staff_password():
    # USing service role key to bypass auth barriers
    supabase = create_client(URL, SERVICE_KEY)
    email = "rajeshmama4322@gmail.com"
    new_password = "Staff123"
    
    print(f"Resetting password for {email} to {new_password}...")
    
    try:
        # Get user ID first
        # Use auth.admin to list or find user if possible, 
        # but since we know the email, we can iterate or use a direct update if we have the ID.
        # Let's get the ID from the staff table first.
        staff_res = supabase.table('staff').select('id').eq('email', email).single().execute()
        if not staff_res.data:
            print("❌ User not found in staff table.")
            return
            
        user_id = staff_res.data['id']
        print(f"Found User ID: {user_id}")
        
        # Update user in Auth
        supabase.auth.admin.update_user_by_id(
            user_id,
            {"password": new_password}
        )
        print("✅ Password reset successful!")
        
    except Exception as e:
        print(f"❌ Reset failed: {e}")

if __name__ == "__main__":
    reset_staff_password()
