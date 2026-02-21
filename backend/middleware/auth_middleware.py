from functools import wraps
from flask import request, g
from supabase_client import get_supabase_client
from utils.response_helper import error_response

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return error_response("Token is missing", 401)
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            
            supabase = get_supabase_client()
            # Verify the token using Supabase Auth
            user_response = supabase.auth.get_user(token)
            user = user_response.user
            
            if not user:
                 return error_response("Invalid token", 401)

            # Check if user exists in staff table and is active
            # We use the user.id from auth to find the corresponding staff record
            stf = supabase.table('staff').select('id, name, email, role, is_active, department_id').eq('id', user.id).single().execute()
            
            if not stf.data:
                return error_response("User not found in staff records. Please contact admin.", 403)
            
            if not stf.data.get('is_active', False):
                return error_response("User account is inactive", 403)

            # Store the staff object in g for access in routes
            g.user = stf.data
            g.token = token
            
        except Exception as e:
            return error_response(f"Authentication failed", 401)
        
        return f(*args, **kwargs)
    return decorated
