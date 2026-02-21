from functools import wraps
from flask import g
from utils.response_helper import error_response

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user') or not g.user:
                return error_response("User not authenticated", 401)
            
            # Check if the user's role matches the required role
            if g.user.get('role') != required_role:
                return error_response(f"Insufficient permissions. Required: {required_role}", 403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
