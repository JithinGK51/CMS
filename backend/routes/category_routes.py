from flask import Blueprint, request
from supabase_client import get_supabase_client
from middleware.auth_middleware import token_required
from middleware.role_guard import role_required
from utils.response_helper import success_response, error_response

category_bp = Blueprint('category', __name__)

@category_bp.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        supabase = get_supabase_client()
        res = supabase.table('categories').select('*, departments(name)').execute()
        return success_response("Categories fetched", res.data)
    except Exception as e:
        return error_response(str(e))

@category_bp.route('/api/admin/categories', methods=['POST'])
@token_required
@role_required('admin')
def create_category():
    try:
        data = request.json
        supabase = get_supabase_client()
        res = supabase.table('categories').insert(data).execute()
        return success_response("Category created", res.data[0] if res.data else {})
    except Exception as e:
        return error_response(str(e))

@category_bp.route('/api/admin/categories/<uuid:category_id>', methods=['PUT'])
@token_required
@role_required('admin')
def update_category(category_id):
    try:
        data = request.json
        supabase = get_supabase_client()
        res = supabase.table('categories').update(data).eq('id', str(category_id)).execute()
        return success_response("Category updated", res.data[0] if res.data else {})
    except Exception as e:
        return error_response(str(e))
