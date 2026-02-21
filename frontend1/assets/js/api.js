/**
 * CMS API Client & Auth - Single source of truth
 * Connects to backend at localhost:5000
 */
const API_BASE = 'http://localhost:5000/api';

const auth = {
  setToken(t) { localStorage.setItem('cms_token', t); },
  getToken() { return localStorage.getItem('cms_token'); },
  setUser(u) { localStorage.setItem('cms_user', JSON.stringify(u)); },
  getUser() {
    try { return JSON.parse(localStorage.getItem('cms_user')) || null; } catch { return null; }
  },
  isAuthenticated() { return !!auth.getToken(); },
  logout() {
    localStorage.removeItem('cms_token');
    localStorage.removeItem('cms_user');
    const p = location.pathname;
    if (p.includes('/admin/') || p.includes('/staff/')) location.href = '../login.html';
    else location.href = 'login.html';
  }
};

const api = {
  async request(endpoint, method = 'GET', data = null, isFormData = false) {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;

    const opts = {
      method,
      headers: {}
    };

    const token = auth.getToken();
    if (token) {
      opts.headers['Authorization'] = `Bearer ${token}`;
    }

    if (data) {
      if (isFormData) {
        opts.body = data;
      } else {
        opts.headers['Content-Type'] = 'application/json';
        opts.body = JSON.stringify(data);
      }
    }

    try {
      const res = await fetch(url, opts);
      const result = await res.json();

      if (!res.ok) {
        // Handle token expiration
        if (res.status === 401 && auth.isAuthenticated()) {
          console.warn('Session expired. Logging out.');
          auth.logout();
        }
        throw new Error(result.message || `Request failed with status ${res.status}`);
      }

      return result;
    } catch (err) {
      console.error(`API Error [${method} ${endpoint}]:`, err);
      return { success: false, message: err.message || 'Connection error' };
    }
  },

  get(endpoint) { return api.request(endpoint, 'GET'); },
  post(endpoint, data, isFormData = false) { return api.request(endpoint, 'POST', data, isFormData); },
  put(endpoint, data) { return api.request(endpoint, 'PUT', data); },
  delete(endpoint) { return api.request(endpoint, 'DELETE'); }
};
