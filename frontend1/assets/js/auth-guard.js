/**
 * Auth guard - protects admin/staff pages. Load AFTER api.js
 */
(function () {
  const path = location.pathname;
  const publicPaths = ['index.html', 'login.html', 'submit-complaint.html', 'track-complaint.html', 'success.html', 'select-category.html'];
  const page = path.split('/').pop() || '';
  if (publicPaths.includes(page) && !path.includes('/admin/') && !path.includes('/staff/')) return;

  if (typeof auth === 'undefined' || !auth.isAuthenticated()) {
    const base = (path.includes('/admin/') || path.includes('/staff/')) ? '../' : '';
    location.replace(base + 'login.html');
    return;
  }

  const user = auth.getUser();
  if (!user) return;

  if (path.includes('/admin/') && user.role !== 'admin') {
    location.replace('../staff/dashboard.html');
    return;
  }
  if (path.includes('/staff/') && user.role !== 'staff') {
    location.replace('../admin/dashboard.html');
  }
})();
