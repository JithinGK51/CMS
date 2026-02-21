from flask import Blueprint, request
from supabase_client import get_supabase_client
from utils.response_helper import success_response, error_response

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not email or not password:
            return error_response("Email and password are required", 400)

        supabase = get_supabase_client()

        # Sign in with Supabase auth
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if not auth_response.user:
            return error_response("Invalid email or password", 401)

        user = auth_response.user
        token = auth_response.session.access_token

        # Get staff record
        staff_res = supabase.table('staff').select(
            'id, name, email, role, is_active, department_id, departments(name)'
        ).eq('id', user.id).single().execute()

        if not staff_res.data:
            return error_response("User not found in staff records. Contact admin.", 403)

        staff = staff_res.data
        if not staff.get('is_active', False):
            return error_response("Your account is inactive. Contact admin.", 403)

        # Flatten department name
        if staff.get('departments'):
            staff['department_name'] = staff['departments']['name']
        else:
            staff['department_name'] = None

        return success_response("Login successful", {
            "token": token,
            "user": {
                "id": staff['id'],
                "name": staff['name'],
                "email": staff['email'],
                "role": staff['role'],
                "department_id": staff.get('department_id'),
                "department_name": staff.get('department_name'),
            }
        })

    except Exception as e:
        err = str(e)
        if 'Invalid login credentials' in err or 'invalid_credentials' in err:
            return error_response("Invalid email or password", 401)
        return error_response(f"Login failed: {err}", 500)


@auth_bp.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.json
        email = data.get('email', '').strip()
        if not email:
            return error_response("Email is required", 400)

        supabase = get_supabase_client()
        supabase.auth.reset_password_email(email)

        return success_response("Password reset email sent. Please check your inbox.", {})
    except Exception as e:
        return error_response(f"Failed to send reset email: {str(e)}", 500)
