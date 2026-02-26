import os
import sys
import subprocess
import webbrowser
import time
from threading import Thread

def install_requirements():
    print("Checking dependencies...")
    try:
        import flask
        import flask_cors
        import dotenv
        import supabase
        import docx
        import requests
        print("✅ All dependencies found.")
    except ImportError:
        print("📦 Missing dependencies. Installing from requirements.txt...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully.")
        except Exception as e:
            print(f"❌ Failed to install dependencies: {e}")
            sys.exit(1)

def check_supabase():
    print("� Verifying Supabase connection...")
    try:
        from dotenv import load_dotenv
        from supabase import create_client
        
        # Load .env from backend folder
        env_path = os.path.join(os.getcwd(), "backend", ".env")
        if not os.path.exists(env_path):
            print(f"⚠️ Warning: .env not found at {env_path}")
            return False
            
        load_dotenv(env_path)
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            print("❌ Error: SUPABASE_URL or SUPABASE_KEY missing in backend/.env")
            return False
            
        supabase = create_client(url, key)
        # Try a simple query to verify connection
        supabase.table('departments').select('id').limit(1).execute()
        print("✅ Supabase connection verified.")
        return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def run_backend():
    print("🚀 Starting Backend...")
    # Change directory to backend to ensure imports work correctly
    backend_dir = os.path.join(os.getcwd(), "backend")
    os.chdir(backend_dir)
    subprocess.call([sys.executable, "app.py"])

def open_frontend(root_dir):
    # Wait a moment for the backend to start
    time.sleep(3)
    print("🌐 Opening Frontend...")
    frontend_path = os.path.abspath(os.path.join(root_dir, "frontend1", "index.html"))
    webbrowser.open(f"file://{frontend_path}")

if __name__ == "__main__":
    # Ensure we are in the root directory
    root_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root_dir)

    # 1. Check and install requirements
    install_requirements()

    # 2. Check Supabase connection
    if not check_supabase():
        print("🛑 System cannot start without a valid Supabase connection.")
        sys.exit(1)

    # 3. Open frontend in a separate thread
    Thread(target=open_frontend, args=(root_dir,), daemon=True).start()

    # 4. Run backend (this will block)
    run_backend()
