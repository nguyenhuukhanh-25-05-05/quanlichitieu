import { defineStore } from 'pinia';
import api from '../services/api';

export const useAuthStore = defineStore('auth', {
  state: () => {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user'));
    return {
      user: user || null,
      token: token || null,
      isGuest: false,
      loading: false,
      error: null,
    };
  },
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async register(fullname, email, password, currency) {
      this.loading = true;
      this.error = null;
      try {
        const response = await api.post('/auth/register', {
          fullname,
          email,
          password,
          currency,
        });
        this.loading = false;
        return response.data;
      } catch (err) {
        this.loading = false;
        this.error = err.response?.data?.detail || 'Đăng ký thất bại';
        throw err;
      }
    },
    async login(email, password) {
      this.loading = true;
      this.error = null;
      try {
        const response = await api.post('/auth/login', { email, password });
        const { access_token } = response.data;
        this.token = access_token;
        this.isGuest = false;
        localStorage.setItem('token', access_token);
        
        // Fetch current user details
        const userResponse = await api.get('/auth/me');
        this.user = userResponse.data;
        localStorage.setItem('user', JSON.stringify(this.user));
        
        this.loading = false;
      } catch (err) {
        this.loading = false;
        this.error = err.response?.data?.detail || 'Đăng nhập thất bại';
        throw err;
      }
    },
    logout() {
      this.user = null;
      this.token = null;
      this.isGuest = false;
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    },
    async fetchUser() {
      if (!this.token) return;
      try {
        const response = await api.get('/auth/me');
        this.user = response.data;
        this.isGuest = false;
        localStorage.setItem('user', JSON.stringify(this.user));
      } catch (err) {
        this.logout();
      }
    }
  },
});
