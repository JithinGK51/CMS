from flask import Blueprint, request, g
from services.complaint_service import ComplaintService
from services.upload_service import UploadService
from middleware.auth_middleware import token_required
from middleware.role_guard import role_required
from utils.response_helper import success_response, error_response
from supabase_client import get_supabase_client
import time

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/api/staff/complaints', methods=['GET'])
@token_required
@role_required('staff')
def get_complaints():
    try:
        filters = {'assigned_staff_id': g.user['id']}
        complaints = ComplaintService.get_all_complaints(filters)
        return success_response("Assigned complaints fetched", complaints)
    except Exception as e:
        return error_response(str(e))

@staff_bp.route('/api/staff/complaint/<int:complaint_id>', methods=['GET'])
@token_required
@role_required('staff')
def get_single_complaint(complaint_id):
    try:
        supabase = get_supabase_client()
        res = supabase.table('complaints').select(
            '*, categories(name), departments(name), complaint_files(file_url)'
        ).eq('id', complaint_id).eq('assigned_staff_id', g.user['id']).single().execute()
        if not res.data:
            return error_response("Complaint not found or not assigned to you", 404)
        data = res.data
        data['category_name'] = data['categories']['name'] if data.get('categories') else None
        data['department_name'] = data['departments']['name'] if data.get('departments') else None
        data['files'] = data.get('complaint_files', [])
        return success_response("Complaint fetched", data)
    except Exception as e:
        return error_response(str(e))

@staff_bp.route('/api/staff/status/<int:complaint_id>', methods=['PUT'])
@token_required
@role_required('staff')
def update_status(complaint_id):
    try:
        data = request.json
        # Validate allowed transitions for staff
        allowed = ['submitted', 'assigned', 'in_progress', 'resolved', 'closed']
        if data.get('status') not in allowed:
            return error_response(f"Invalid status. Allowed: {', '.join(allowed)}", 400)
            
        result = ComplaintService.update_status(
            complaint_id,
            data['status'],
            g.user['id'],
            'staff',
            data.get('note')
        )
        return success_response("Status updated", result)
    except Exception as e:
         return error_response(str(e))

@staff_bp.route('/api/staff/upload-proof', methods=['POST'])
@token_required
@role_required('staff')
def upload_proof():
    try:
        file = request.files.get('file')
        complaint_id = request.form.get('complaint_id')
        
        if not file or not complaint_id:
            return error_response("File and complaint_id required", 400)
            
        timestamp = int(time.time())
        filename = f"proof_{complaint_id}_{timestamp}_{file.filename}"
        path = f"proofs/{filename}"
        
        file_url = UploadService.upload_file(file, path)
        
        # Insert into complaint_files
        supabase = get_supabase_client()
        supabase.table('complaint_files').insert({
            "complaint_id": complaint_id,
            "file_url": file_url,
            "uploaded_by": g.user['id']
        }).execute()
        
        return success_response("Proof uploaded", {"file_url": file_url})
    except Exception as e:
        return error_response(str(e))
@staff_bp.route('/api/staff/profile', methods=['GET'])
@token_required
@role_required('staff')
def get_profile():
    try:
        supabase = get_supabase_client()
        res = supabase.table('staff').select(
            'id, name, email, role, is_active, phone, department_id, departments(name)'
        ).eq('id', g.user['id']).single().execute()
        data = res.data or {}
        if 'departments' in data and data['departments']:
            data['department_name'] = data['departments']['name']
        return success_response("Profile fetched", data)
    except Exception as e:
        return error_response(str(e))

@staff_bp.route('/api/staff/profile', methods=['PUT'])
@token_required
@role_required('staff')
def update_profile():
    try:
        data = request.json or {}
        updates = {}
        if 'name'  in data: updates['name']  = data['name']
        if 'phone' in data: updates['phone'] = data['phone']

        if not updates:
            return error_response("No valid fields to update", 400)

        supabase = get_supabase_client()
        res = supabase.table('staff').update(updates).eq('id', g.user['id']).execute()
        return success_response("Profile updated", res.data[0] if res.data else None)
    except Exception as e:
        return error_response(str(e))
