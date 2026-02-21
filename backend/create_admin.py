import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def create_admin():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    email = "admin@cms.com"
    password = "AdminPassword123"
    name = "System Administrator"
    
    print(f"Creating admin user: {email}")
    
    try:
        # Create in Auth
        # Note: This requires the SERVICE_ROLE key
        user_res = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True
        })
        
        user_id = user_res.user.id
        print(f"Auth user created with ID: {user_id}")
        
        # Create in Staff table
        staff_data = {
            "id": user_id,
            "name": name,
            "email": email,
            "role": "admin",
            "is_active": True
        }
        
        supabase.table('staff').insert(staff_data).execute()
        print("Staff record created successfully.")
        
    except Exception as e:
        print(f"Error: {e}")
        if "already exists" in str(e).lower():
            print("Admin user might already exist in Auth but not in Staff table.")
            # Try to find user in auth if possible or just try to sync
            # Since we can't easily query auth.users, we might need to rely on the user knowing.

if __name__ == "__main__":
    create_admin()
