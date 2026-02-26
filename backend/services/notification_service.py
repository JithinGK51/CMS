from supabase_client import get_supabase_client

class NotificationService:
    @staticmethod
    def _get_settings():
        supabase = get_supabase_client()
        res = supabase.table('system_settings').select('*').eq('id', 1).single().execute()
        return res.data if res.data else {}

    @staticmethod
    def create_notification(user_id, title, message):
        supabase = get_supabase_client()
        settings = NotificationService._get_settings()
        
        # In-app notification
        data = {
            "user_id": user_id,
            "title": title,
            "message": message,
            "is_read": False,
            "settings_id": 1
        }
        res = supabase.table('notifications').insert(data).execute()
        
        # Check for Email/SMS features
        if settings.get('email_enabled'):
            # Fetch user email
            user = supabase.table('staff').select('email').eq('id', user_id).single().execute()
            if user.data and user.data.get('email'):
                print(f"[FEATURE: EMAIL] Sending notification email to {user.data['email']}: {title}")
                # email_provider.send(...)
        
        if settings.get('sms_enabled'):
            # Fetch user phone
            user = supabase.table('staff').select('phone').eq('id', user_id).single().execute()
            if user.data and user.data.get('phone'):
                print(f"[FEATURE: SMS] Sending notification SMS to {user.data['phone']}: {title}")
                # sms_provider.send(...)
                
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
                "is_read": False,
                "settings_id": 1
            })
        if notifications:
            supabase.table('notifications').insert(notifications).execute()
            
    @staticmethod
    def get_user_notifications(user_id):
        supabase = get_supabase_client()
        res = supabase.table('notifications').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(50).execute()
        return res.data
