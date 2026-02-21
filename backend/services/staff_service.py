from supabase_client import get_supabase_client, get_supabase_admin_client

class StaffService:
    @staticmethod
    def create_staff(email, password, name, role, department_id=None, phone=None):
        # Use admin client to create auth user without signing in
        supabase_admin = get_supabase_admin_client()
        supabase = get_supabase_client()
        
        # 1. Create the auth user using admin privileges
        try:
            print(f"[StaffService] Creating auth user for: {email}")
            user_res = supabase_admin.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True
            })
            if not user_res or not user_res.user:
                raise Exception("Auth user creation returned no user")
            print(f"[StaffService] Auth user created successfully: {user_res.user.id}")
        except Exception as e:
            print(f"[StaffService] Auth creation failed: {str(e)}")
            raise Exception(f"Failed to create user account: {str(e)}")
            
        user_id = user_res.user.id
        
        # 2. Insert into staff table
        data = {
            "id":            user_id,
            "name":          name,
            "email":         email,
            "role":          role or 'staff',
            "department_id": department_id if department_id else None,
            "phone":         phone,
            "is_active":     True
        }
        
        try:
            res = supabase.table('staff').insert(data).execute()
            print(f"[StaffService] Staff record created: {res.data}")
            return res.data[0] if res.data else None
        except Exception as e:
            # If staff insert fails, try to clean up the auth user
            try:
                supabase_admin.auth.admin.delete_user(user_id)
            except:
                pass
            raise Exception(f"Failed to create staff record: {str(e)}")

    @staticmethod
    def get_all_staff():
        supabase = get_supabase_client()
        res = supabase.table('staff').select('*, departments(name)').order('name').execute()
        return res.data

    @staticmethod
    def update_staff(staff_id, updates):
        supabase = get_supabase_client()
        res = supabase.table('staff').update(updates).eq('id', staff_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def get_staff_by_dept(department_id):
        supabase = get_supabase_client()
        res = supabase.table('staff').select('id, name').eq('department_id', department_id).eq('is_active', True).execute()
        return res.data

    @staticmethod
    def get_staff_performance():
        """Returns assignment count per active staff member."""
        supabase = get_supabase_client()
        staff_res = supabase.table('staff').select('id, name').eq('is_active', True).execute()
        perf = []
        for s in (staff_res.data or []):
            count_res = supabase.table('complaints').select('id', count='exact').eq('assigned_staff_id', s['id']).execute()
            resolved  = supabase.table('complaints').select('id', count='exact').eq('assigned_staff_id', s['id']).eq('status', 'resolved').execute()
            perf.append({
                'name':     s['name'],
                'assigned': count_res.count or 0,
                'resolved': resolved.count or 0
            })
        return sorted(perf, key=lambda x: x['assigned'], reverse=True)
