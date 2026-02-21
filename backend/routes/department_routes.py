from flask import Blueprint, request
from supabase_client import get_supabase_client
from middleware.auth_middleware import token_required
from middleware.role_guard import role_required
from utils.response_helper import success_response, error_response

dept_bp = Blueprint('department', __name__)

@dept_bp.route('/api/departments', methods=['GET'])
def get_departments():
    try:
        supabase = get_supabase_client()
        res = supabase.table('departments').select('*').execute()
        return success_response("Departments fetched", res.data)
    except Exception as e:
        return error_response(str(e))

@dept_bp.route('/api/admin/departments', methods=['POST'])
@token_required
@role_required('admin')
def create_department():
    try:
        data = request.json
        supabase = get_supabase_client()
        res = supabase.table('departments').insert(data).execute()
        return success_response("Department created", res.data[0] if res.data else {})
    except Exception as e:
        return error_response(str(e))
