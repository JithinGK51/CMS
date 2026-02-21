from supabase_client import get_supabase_client

class DashboardService:
    @staticmethod
    def get_admin_stats():
        supabase = get_supabase_client()
        
        # We can use count='exact' with head=True to get counts without fetching data
        total = supabase.table('complaints').select('*', count='exact', head=True).execute().count
        pending = supabase.table('complaints').select('*', count='exact', head=True).eq('status', 'submitted').execute().count
        in_progress = supabase.table('complaints').select('*', count='exact', head=True).eq('status', 'in_progress').execute().count
        resolved = supabase.table('complaints').select('*', count='exact', head=True).eq('status', 'resolved').execute().count
        
        # Getting aggregated data (group by) is harder via PostgREST/Supabase-py without raw SQL or RPC
        # For simplicity, we might fetch basics or use client-side aggregation if data volume is small. 
        # Alternatively, create a Postgres View for stats.
        # Here we just return the total counts.
        
        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "resolved": resolved
        }

    @staticmethod
    def get_staff_stats(staff_id):
        supabase = get_supabase_client()
        
        assigned = supabase.table('complaints').select('*', count='exact', head=True).eq('assigned_staff_id', staff_id).execute().count
        pending = supabase.table('complaints').select('*', count='exact', head=True).eq('assigned_staff_id', staff_id).eq('status', 'assigned').execute().count
        completed = supabase.table('complaints').select('*', count='exact', head=True).eq('assigned_staff_id', staff_id).eq('status', 'resolved').execute().count
        
        return {
            "assigned": assigned,
            "pending": pending,
            "completed": completed
        }
