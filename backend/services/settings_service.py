from supabase_client import get_supabase_client

class SettingsService:
    @staticmethod
    def get_settings():
        supabase = get_supabase_client()
        res = supabase.table('system_settings').select('*').limit(1).execute()
        if res.data:
            return res.data[0]
        return None

    @staticmethod
    def update_settings(data):
        supabase = get_supabase_client()
        # Check if settings row exists
        existing = supabase.table('system_settings').select('id').limit(1).execute()
        if existing.data:
            res = supabase.table('system_settings').update(data).eq('id', existing.data[0]['id']).execute()
        else:
            res = supabase.table('system_settings').insert(data).execute()
        return res.data[0] if res.data else None
