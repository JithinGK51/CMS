from flask import Blueprint, request, g
from services.staff_service import StaffService
from services.complaint_service import ComplaintService
from services.dashboard_service import DashboardService
from services.report_service import ReportService
from services.settings_service import SettingsService
from middleware.auth_middleware import token_required
from middleware.role_guard import role_required
from utils.response_helper import success_response, error_response

admin_bp = Blueprint('admin', __name__)

# ─── STAFF MANAGEMENT ───────────────────────────────────────────────────────
@admin_bp.route('/api/admin/staff', methods=['POST'])
@token_required
@role_required('admin')
def create_staff():
    try:
        data = request.json
        if not data.get('email') or not data.get('password') or not data.get('name'):
            return error_response("name, email and password are required", 400)
        staff = StaffService.create_staff(
            data['email'], data['password'], data['name'],
            data.get('role', 'staff'), data.get('department_id'),
            data.get('phone')
        )
        return success_response("Staff created successfully", staff)
    except Exception as e:
        return error_response(str(e))

@admin_bp.route('/api/admin/staff', methods=['GET'])
@token_required
@role_required('admin')
def get_staff():
    try:
        staff_list = StaffService.get_all_staff()
        return success_response("Staff list fetched", staff_list)
    except Exception as e:
        return error_response(str(e))

@admin_bp.route('/api/admin/staff/<string:staff_id>', methods=['PUT'])
@token_required
@role_required('admin')
def update_staff(staff_id):
    try:
        data = request.json
        updates = {}
        if 'role' in data: updates['role'] = data['role']
        if 'department_id' in data: updates['department_id'] = data['department_id']
        if 'is_active' in data: updates['is_active'] = data['is_active']
        if 'name' in data: updates['name'] = data['name']
        if 'phone' in data: updates['phone'] = data['phone']
        staff = StaffService.update_staff(staff_id, updates)
        return success_response("Staff updated successfully", staff)
    except Exception as e:
        return error_response(str(e))

# ─── COMPLAINT MANAGEMENT ────────────────────────────────────────────────────
@admin_bp.route('/api/admin/complaints', methods=['GET'])
@token_required
@role_required('admin')
def get_complaints():
    try:
        filters = {}
        if request.args.get('status'):    filters['status']        = request.args.get('status')
        if request.args.get('category'):  filters['category_id']   = request.args.get('category')
        if request.args.get('dept'):      filters['department_id'] = request.args.get('dept')
        if request.args.get('search'):    filters['search']        = request.args.get('search')
        complaints = ComplaintService.get_all_complaints(filters)
        return success_response("Complaints fetched", complaints)
    except Exception as e:
        return error_response(str(e))

@admin_bp.route('/api/admin/complaints/<int:complaint_id>', methods=['GET'])
@token_required
@role_required('admin')
def get_complaint_detail(complaint_id):
    try:
        complaint = ComplaintService.get_complaint_by_id(complaint_id)
        if not complaint:
            return error_response("Complaint not found", 404)
        return success_response("Complaint details fetched", complaint)
    except Exception as e:
        return error_response(str(e))

@admin_bp.route('/api/admin/assign/<int:complaint_id>', methods=['PUT'])
@token_required
@role_required('admin')
def assign_complaint(complaint_id):
    try:
        data = request.json or {}
        staff_id = data.get('assigned_staff_id') or data.get('staff_id')
        if not staff_id:
            return error_response("assigned_staff_id is required", 400)
        result = ComplaintService.assign_staff(
            complaint_id,
            staff_id,
            data.get('department_id'),   # fully optional
            g.user['id']
        )
        return success_response("Complaint assigned successfully", result)
    except Exception as e:
        return error_response(str(e))

@admin_bp.route('/api/admin/status/<int:complaint_id>', methods=['PUT'])
@token_required
@role_required('admin')
def update_status(complaint_id):
    try:
        data = request.json
        result = ComplaintService.update_status(
            complaint_id,
            data['status'],
            g.user['id'],
            'admin',
            data.get('note')
        )
        return success_response("Status updated successfully", result)
    except Exception as e:
        return error_response(str(e))

@admin_bp.route('/api/admin/complaints/<int:complaint_id>/note', methods=['POST'])
@token_required
@role_required('admin')
def add_complaint_note(complaint_id):
    try:
        data = request.json
        note_text = data.get('note', '').strip()
        if not note_text:
            return error_response("Note text is required", 400)
        ComplaintService.add_note(complaint_id, g.user['id'], note_text)
        return success_response("Note added successfully", {})
    except Exception as e:
        return error_response(str(e))

# ─── DASHBOARD ───────────────────────────────────────────────────────────────
@admin_bp.route('/api/admin/dashboard', methods=['GET'])
@token_required
@role_required('admin')
def dashboard_stats():
    try:
        stats = DashboardService.get_admin_stats()
        return success_response("Dashboard stats fetched", stats)
    except Exception as e:
        return error_response(str(e))

# ─── REPORTS ─────────────────────────────────────────────────────────────────
@admin_bp.route('/api/admin/reports/summary', methods=['GET'])
@token_required
@role_required('admin')
def get_report_summary():
    try:
        return success_response("Summary fetched", ReportService.get_summary())
    except Exception as e:
        return error_response(str(e))

@admin_bp.route('/api/admin/reports/trends', methods=['GET'])
@token_required
@role_required('admin')
def get_report_trends():
    try:
        return success_response("Trends fetched", ReportService.get_complaint_trends())
    except Exception as e:
        return error_response(str(e))

@admin_bp.route('/api/admin/reports/monthly', methods=['GET'])
@token_required
@role_required('admin')
def get_report_monthly():
    try:
        return success_response("Monthly trends fetched", ReportService.get_monthly_trends())
    except Exception as e:
        return error_response(str(e))

@admin_bp.route('/api/admin/reports/status', methods=['GET'])
@token_required
@role_required('admin')
def get_report_status():
    try:
        return success_response("Status distribution fetched", ReportService.get_status_distribution())
    except Exception as e:
        return error_response(str(e))

@admin_bp.route('/api/admin/reports/categories', methods=['GET'])
@token_required
@role_required('admin')
def get_report_categories():
    try:
        return success_response("Category distribution fetched", ReportService.get_category_distribution())
    except Exception as e:
        return error_response(str(e))

@admin_bp.route('/api/admin/reports/priority', methods=['GET'])
@token_required
@role_required('admin')
def get_report_priority():
    try:
        return success_response("Priority distribution fetched", ReportService.get_priority_distribution())
    except Exception as e:
        return error_response(str(e))

@admin_bp.route('/api/admin/reports/performance', methods=['GET'])
@token_required
@role_required('admin')
def get_report_performance():
    try:
        return success_response("Performance fetched", ReportService.get_staff_performance())
    except Exception as e:
        return error_response(str(e))

@admin_bp.route('/api/admin/reports/departments', methods=['GET'])
@token_required
@role_required('admin')
def get_report_departments():
    try:
        return success_response("Department stats fetched", ReportService.get_department_stats())
    except Exception as e:
        return error_response(str(e))

@admin_bp.route('/api/admin/reports/resolution', methods=['GET'])
@token_required
@role_required('admin')
def get_report_resolution():
    try:
        return success_response("Resolution stats fetched", ReportService.get_resolution_time_stats())
    except Exception as e:
        return error_response(str(e))


# ─── SETTINGS ────────────────────────────────────────────────────────────────
@admin_bp.route('/api/admin/settings', methods=['GET'])
@token_required
@role_required('admin')
def get_settings_route():
    try:
        settings = SettingsService.get_settings()
        return success_response("Settings fetched", settings)
    except Exception as e:
        return error_response(str(e))

@admin_bp.route('/api/admin/settings', methods=['POST', 'PUT'])
@token_required
@role_required('admin')
def update_settings_route():
    try:
        data = request.json
        settings = SettingsService.update_settings(data)
        return success_response("Settings updated", settings)
    except Exception as e:
        return error_response(str(e))

# ─── UNASSIGNED COMPLAINTS ───────────────────────────────────────────────────
@admin_bp.route('/api/admin/unassigned-complaints', methods=['GET'])
@token_required
@role_required('admin')
def get_unassigned_complaints():
    try:
        complaints = ComplaintService.get_all_complaints({'assigned_staff_id': 'null'})
        return success_response("Unassigned complaints fetched", complaints)
    except Exception as e:
        return error_response(str(e))
