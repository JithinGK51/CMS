/**
 * Shared layout for admin/staff dashboards - populates user and nav
 */
function renderLayout(config) {
  const user = auth.getUser();
  if (!user) return;

  document.querySelectorAll('.user-name').forEach(el => { el.textContent = user.name || 'User'; });
  document.querySelectorAll('.user-role').forEach(el => { el.textContent = (user.role === 'admin' ? 'Admin' : (user.department_name || user.role || 'Staff')); });

  const page = config.page || '';
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.remove('active');
    const href = (link.getAttribute('href') || '').replace('.html', '');
    if (page && href.includes(page)) link.classList.add('active');
    if (link.classList.contains('logout')) {
      link.onclick = (e) => { e.preventDefault(); auth.logout(); };
    }
  });
}
