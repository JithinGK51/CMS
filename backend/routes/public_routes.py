from flask import Blueprint, request
import time
from services.complaint_service import ComplaintService
from services.upload_service import UploadService
from utils.response_helper import success_response, error_response

public_bp = Blueprint('public', __name__)

@public_bp.route('/api/complaints', methods=['POST'])
def create_complaint():
    try:
        # File upload
        file = request.files.get('image')
        image_url = None
        if file:
            # Generate unique filename
            timestamp = int(time.time())
            filename = f"{timestamp}_{file.filename}"
            path = f"complaints/{filename}" 
            image_url = UploadService.upload_file(file, path)
        
        # Determine defaults
        status = "submitted"
        priority = "medium"

        data = {
           "category_id": request.form.get('category_id'),
           "title": request.form.get('title'),
           "description": request.form.get('description'),
           "location": request.form.get('location'),
           "citizen_mobile": request.form.get('citizen_mobile'),
           "citizen_email": request.form.get('citizen_email'),
           "image_url": image_url,
           "status": status, 
           "priority": priority
        }
        
        # Remove None values if optional fields are missing (supasbase handles defaults or nulls)
        # However, passing None explicitly is usually fine if column is nullable.
        
        complaint = ComplaintService.create_complaint(data)
        return success_response("Complaint registered successfully", complaint)
    except Exception as e:
        return error_response(str(e))

@public_bp.route('/api/complaints/track/<token>', methods=['GET'])
def track_complaint(token):
    try:
        complaint = None

        # Try token field first (e.g. "CMP-2026-00005")
        complaint = ComplaintService.get_complaint_by_token(token)

        # Fallback: try extracting trailing numeric ID
        if not complaint:
            import re
            m = re.search(r'(\d+)$', token)
            if m:
                numeric_id = int(m.group(1))
                complaint = ComplaintService.get_complaint_by_id(numeric_id)

        if not complaint:
            return error_response("Complaint not found. Please check the ID and try again.", 404)

        # Flatten nested relations
        if complaint.get('categories'):
            complaint['category_name'] = complaint['categories']['name']
        if complaint.get('departments'):
            complaint['department_name'] = complaint['departments']['name']
        if complaint.get('staff'):
            complaint['assigned_staff_name'] = complaint['staff']['name']

        return success_response("Complaint details fetched", complaint)
    except Exception as e:
        return error_response(str(e))
