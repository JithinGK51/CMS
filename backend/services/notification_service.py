from supabase_client import get_supabase_client

class NotificationService:
    @staticmethod
    def create_notification(user_id, title, message):
        supabase = get_supabase_client()
        data = {
            "user_id": user_id,
            "title": title,
            "message": message,
            "is_read": False
        }
        res = supabase.table('notifications').insert(data).execute()
        return res.data

    @staticmethod
    def notify_admins(title, message):
        supabase = get_supabase_client()
        # Fetch all admins
        admins = supabase.table('staff').select('id').eq('role', 'admin').eq('is_active', True).execute()
        notifications = []
        for admin in admins.data:
            notifications.append({
                "user_id": admin['id'],
                "title": title,
                "message": message,
                "is_read": False
            })
        if notifications:
            supabase.table('notifications').insert(notifications).execute()
            
    @staticmethod
    def get_user_notifications(user_id):
        supabase = get_supabase_client()
        res = supabase.table('notifications').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(50).execute()
        return res.data
