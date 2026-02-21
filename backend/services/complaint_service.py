from supabase_client import get_supabase_client
from services.notification_service import NotificationService
from datetime import datetime
import random

class ComplaintService:
    @staticmethod
    def create_complaint(data):
        supabase = get_supabase_client()
        res = supabase.table('complaints').insert(data).execute()
        
        if not res.data:
            raise Exception("Failed to create complaint")

        # Refetch to get the generated token (trigger sets it)
        inserted_id = res.data[0]['id']
        complaint_res = supabase.table('complaints').select('*, categories(name)').eq('id', inserted_id).single().execute()
        complaint = complaint_res.data
        
        # Initial timeline entry
        ComplaintService.add_timeline(complaint['id'], 'submitted', None, 'Complaint submitted by citizen')
        
        # Auto-assign if enabled
        try:
            settings_res = supabase.table('system_settings').select('auto_assign').limit(1).execute()
            if settings_res.data and settings_res.data[0].get('auto_assign'):
                ComplaintService.auto_assign(complaint)
        except Exception as e:
            print(f"Auto-assign check failed: {e}")
        
        # Notify admins
        try:
            NotificationService.notify_admins("New Complaint", f"New complaint received: {complaint.get('title','')}")
        except Exception as e:
            print(f"Notification failed: {e}")
        
        return complaint

    @staticmethod
    def auto_assign(complaint):
        """Auto-assign complaint to least-busy active staff based on category department."""
        supabase = get_supabase_client()
        try:
            dept_id = complaint.get('department_id')
            
            # Build staff query — prefer matching department if possible
            query = supabase.table('staff').select('id, name').eq('is_active', True).neq('role', 'admin')
            if dept_id:
                query = query.eq('department_id', dept_id)
            
            staff_res = query.execute()
            
            if not staff_res.data:
                # Fall back to any active staff
                staff_res = supabase.table('staff').select('id, name').eq('is_active', True).neq('role', 'admin').execute()
            
            if staff_res.data:
                chosen = random.choice(staff_res.data)
                updates = {
                    "assigned_staff_id": chosen['id'],
                    "status": "assigned"
                }
                supabase.table('complaints').update(updates).eq('id', complaint['id']).execute()
                ComplaintService.add_timeline(complaint['id'], 'assigned', None, f"Auto-assigned to {chosen['name']}")
                NotificationService.create_notification(chosen['id'], "Complaint Assigned", "A new complaint has been auto-assigned to you.")
        except Exception as e:
            print(f"Auto-assign error: {e}")

    @staticmethod
    def get_complaint_by_token(token):
        supabase = get_supabase_client()
        try:
            res = supabase.table('complaints').select('*, departments(name), categories(name), staff(name)').eq('token', token).single().execute()
            if res.data:
                # Use explicit join for updated_by
                timeline_res = supabase.table('complaint_timeline').select('*, staff:updated_by(name)').eq('complaint_id', res.data['id']).order('created_at').execute()
                res.data['timeline'] = timeline_res.data
            return res.data
        except:
            return None

    @staticmethod
    def get_complaint_by_id(complaint_id):
        supabase = get_supabase_client()
        try:
            res = supabase.table('complaints').select('*, departments(name), categories(name), staff(name)').eq('id', complaint_id).single().execute()
            if res.data:
                timeline_res = supabase.table('complaint_timeline').select('*, staff:updated_by(name)').eq('complaint_id', complaint_id).order('created_at').execute()
                res.data['timeline'] = timeline_res.data
            return res.data
        except:
            return None

    @staticmethod
    def assign_staff(complaint_id, staff_id, department_id, admin_id):
        supabase = get_supabase_client()
        
        # Get staff name for timeline
        staff_name = "Unknown"
        try:
            s = supabase.table('staff').select('name').eq('id', staff_id).single().execute()
            if s.data:
                staff_name = s.data['name']
        except:
            pass
        
        updates = {
            "assigned_staff_id": staff_id,
            "status": "assigned"
        }
        if department_id:
            updates["department_id"] = department_id
        
        res = supabase.table('complaints').update(updates).eq('id', complaint_id).execute()
        ComplaintService.add_timeline(complaint_id, 'assigned', admin_id, f"Complaint assigned to {staff_name}")
        
        try:
            NotificationService.create_notification(staff_id, "Complaint Assigned", "You have been assigned a new complaint.")
        except:
            pass
        
        return res.data[0] if res.data else None

    @staticmethod
    def update_status(complaint_id, new_status, user_id, role, note=None):
        supabase = get_supabase_client()
        updates = {"status": new_status}
        res = supabase.table('complaints').update(updates).eq('id', complaint_id).execute()
        ComplaintService.add_timeline(complaint_id, new_status, user_id, note or f"Status updated to {new_status}")
        return res.data[0] if res.data else None

    @staticmethod
    def add_note(complaint_id, user_id, note_text):
        """Add an internal note to a complaint's history."""
        supabase = get_supabase_client()
        # Get current status
        c = supabase.table('complaints').select('status').eq('id', complaint_id).single().execute()
        current_status = c.data['status'] if c.data else 'note'
        ComplaintService.add_timeline(complaint_id, current_status, user_id, note_text)

    @staticmethod
    def add_timeline(complaint_id, status, user_id, note):
        supabase = get_supabase_client()
        data = {
            "complaint_id": complaint_id,
            "status": status,
            "updated_by": user_id,
            "note": note
        }
        supabase.table('complaint_timeline').insert(data).execute()

    @staticmethod
    def get_all_complaints(filters=None):
        supabase = get_supabase_client()
        query = supabase.table('complaints').select('*, departments(name), categories(name), staff(name)')
        
        if filters:
            if filters.get('status'):
                query = query.eq('status', filters['status'])
            if filters.get('category_id'):
                query = query.eq('category_id', filters['category_id'])
            if filters.get('department_id'):
                query = query.eq('department_id', filters['department_id'])
            if filters.get('search'):
                query = query.ilike('token', f"%{filters['search']}%")
            if 'assigned_staff_id' in filters:
                if filters['assigned_staff_id'] == 'null':
                    query = query.is_('assigned_staff_id', 'null')
                else:
                    query = query.eq('assigned_staff_id', filters['assigned_staff_id'])
                
        res = query.order('created_at', desc=True).execute()
        return res.data
