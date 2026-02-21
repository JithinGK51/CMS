import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SUPABASE_URL              = os.getenv("SUPABASE_URL", "https://wsfyvoboxidzbkmfncaw.supabase.co")
    SUPABASE_KEY              = os.getenv("SUPABASE_KEY")          # anon key
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # service role key (for admin ops)
    SECRET_KEY                = os.getenv("SECRET_KEY", "dev-secret-key")
