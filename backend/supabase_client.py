from supabase import create_client, Client
from config import Config

# Standard client (anon or service role key)
supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

# Service role client — needed for admin user management operations
# If SERVICE_ROLE_KEY is not set, fall back to SUPABASE_KEY (some operations may fail)
_service_key = Config.SUPABASE_SERVICE_ROLE_KEY or Config.SUPABASE_KEY
supabase_admin: Client = create_client(Config.SUPABASE_URL, _service_key)

def get_supabase_client():
    return supabase

def get_supabase_admin_client():
    """Returns a Supabase client initialized with the service role key.
    Required for: auth.admin operations, bypassing RLS, etc."""
    return supabase_admin
