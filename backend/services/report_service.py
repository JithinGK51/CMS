from supabase_client import get_supabase_client
from datetime import datetime, timedelta

class ReportService:

    @staticmethod
    def get_complaint_trends():
        """Daily complaint count for the last 30 days."""
        supabase = get_supabase_client()
        last_30_days = (datetime.utcnow() - timedelta(days=30)).isoformat()
        res = supabase.table('complaints').select('created_at').gte('created_at', last_30_days).execute()

        trends = {}
        for c in res.data:
            date = c['created_at'][:10]
            trends[date] = trends.get(date, 0) + 1

        sorted_trends = [{"date": k, "count": v} for k, v in sorted(trends.items())]
        return sorted_trends

    @staticmethod
    def get_status_distribution():
        """Complaint count per status for pie chart."""
        supabase = get_supabase_client()
        res = supabase.table('complaints').select('status').execute()

        dist = {}
        for c in res.data:
            s = c.get('status', 'submitted')
            dist[s] = dist.get(s, 0) + 1

        return [{"status": k, "count": v} for k, v in dist.items()]

    @staticmethod
    def get_category_distribution():
        """Complaint count per category for doughnut chart."""
        supabase = get_supabase_client()
        res = supabase.table('complaints').select('categories(name)').execute()

        dist = {}
        for c in res.data:
            cat = c.get('categories')
            name = cat['name'] if cat else 'Uncategorized'
            dist[name] = dist.get(name, 0) + 1

        return [{"category": k, "count": v} for k, v in sorted(dist.items(), key=lambda x: -x[1])]

    @staticmethod
    def get_department_stats():
        """Department-wise total, resolved, and resolution rate."""
        supabase = get_supabase_client()
        depts_res = supabase.table('departments').select('id, name').execute()
        stats = []
        for d in (depts_res.data or []):
            total_res    = supabase.table('complaints').select('id', count='exact').eq('department_id', d['id']).execute()
            resolved_res = supabase.table('complaints').select('id', count='exact').eq('department_id', d['id']).eq('status', 'resolved').execute()
            total    = total_res.count or 0
            resolved = resolved_res.count or 0
            rate = round((resolved / total * 100), 1) if total > 0 else 0
            stats.append({
                "department": d['name'],
                "total":      total,
                "resolved":   resolved,
                "rate":       rate
            })
        return sorted(stats, key=lambda x: -x['total'])

    @staticmethod
    def get_staff_performance():
        """Per-staff assigned and resolved counts."""
        supabase = get_supabase_client()
        staff_res = supabase.table('staff').select('id, name').eq('is_active', True).neq('role', 'admin').execute()
        perf = []
        for s in (staff_res.data or []):
            assigned_res = supabase.table('complaints').select('id', count='exact').eq('assigned_staff_id', s['id']).execute()
            resolved_res = supabase.table('complaints').select('id', count='exact').eq('assigned_staff_id', s['id']).eq('status', 'resolved').execute()
            assigned = assigned_res.count or 0
            resolved = resolved_res.count or 0
            if assigned > 0:
                perf.append({
                    "staff": s['name'],
                    "assigned": assigned,
                    "resolved_count": resolved
                })
        return sorted(perf, key=lambda x: -x['assigned'])

    @staticmethod
    def get_resolution_time_stats():
        """Average resolution time in days."""
        supabase = get_supabase_client()
        res = supabase.table('complaints').select('id, created_at').eq('status', 'resolved').execute()
        complaint_ids = [c['id'] for c in res.data]

        if not complaint_ids:
            return {"average_days": 0, "total_resolved": 0, "fastest_hours": 0}

        id_list = ','.join(map(str, complaint_ids))
        timeline_res = supabase.table('complaint_timeline') \
            .select('complaint_id, created_at') \
            .eq('status', 'resolved') \
            .execute()

        total_seconds = 0
        count = 0
        min_seconds = None

        complaint_start = {
            c['id']: datetime.fromisoformat(c['created_at'].replace('Z', '+00:00').replace('+00:00', '').rstrip())
            for c in res.data
        }

        for entry in timeline_res.data:
            cid = entry['complaint_id']
            if cid in complaint_start:
                try:
                    resolved_time = datetime.fromisoformat(entry['created_at'].replace('Z', '+00:00').replace('+00:00', '').rstrip())
                    diff = (resolved_time - complaint_start[cid]).total_seconds()
                    if diff >= 0:
                        total_seconds += diff
                        count += 1
                        if min_seconds is None or diff < min_seconds:
                            min_seconds = diff
                except:
                    pass

        if count == 0:
            return {"average_days": 0, "total_resolved": len(complaint_ids), "fastest_hours": 0}

        avg_days   = round(total_seconds / (count * 86400), 2)
        fastest_hrs = round((min_seconds or 0) / 3600, 1)
        return {
            "average_days":    avg_days,
            "total_resolved":  len(complaint_ids),
            "fastest_hours":   fastest_hrs
        }

    @staticmethod
    def get_monthly_trends():
        """Monthly complaint volume for the last 6 months."""
        supabase = get_supabase_client()
        last_6m = (datetime.utcnow() - timedelta(days=183)).isoformat()
        res = supabase.table('complaints').select('created_at, status').gte('created_at', last_6m).execute()

        monthly = {}  # "YYYY-MM" -> {total, resolved}
        for c in res.data:
            month = c['created_at'][:7]
            if month not in monthly:
                monthly[month] = {'total': 0, 'resolved': 0}
            monthly[month]['total'] += 1
            if c.get('status') == 'resolved':
                monthly[month]['resolved'] += 1

        return [{"month": k, "total": v['total'], "resolved": v['resolved']}
                for k, v in sorted(monthly.items())]

    @staticmethod
    def get_priority_distribution():
        """Complaint count by priority."""
        supabase = get_supabase_client()
        res = supabase.table('complaints').select('priority').execute()
        dist = {}
        for c in res.data:
            p = c.get('priority', 'medium')
            dist[p] = dist.get(p, 0) + 1
        return [{"priority": k, "count": v} for k, v in dist.items()]

    @staticmethod
    def get_summary():
        """High-level summary KPIs."""
        supabase = get_supabase_client()
        total_res    = supabase.table('complaints').select('id', count='exact').execute()
        resolved_res = supabase.table('complaints').select('id', count='exact').eq('status', 'resolved').execute()
        pending_res  = supabase.table('complaints').select('id', count='exact').eq('status', 'submitted').execute()
        staff_res    = supabase.table('staff').select('id', count='exact').eq('is_active', True).execute()

        total    = total_res.count or 0
        resolved = resolved_res.count or 0
        return {
            "total":            total,
            "resolved":         resolved,
            "pending":          pending_res.count or 0,
            "active_staff":     staff_res.count or 0,
            "resolution_rate":  round(resolved / total * 100, 1) if total > 0 else 0
        }
