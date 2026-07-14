import { defineStore } from 'pinia';
import api from '../services/api';
import { useAuthStore } from './auth';
import { mockRecurrings } from '../mocks/mockData';

export const useRecurringStore = defineStore('recurring', {
  state: () => ({
    recurrings: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchRecurrings() {
      this.loading = true;
      const startTime = Date.now();
      const authStore = useAuthStore();
      
      try {
        if (authStore.isGuest) {
          if (this.recurrings.length === 0) {
            this.recurrings = [...mockRecurrings];
          }
        } else {
          const response = await api.get('/recurring/');
          this.recurrings = response.data;
        }
      } catch (err) {
        this.error = err.response?.data?.detail || 'Lấy danh sách giao dịch định kỳ thất bại';
      } finally {
        const elapsed = Date.now() - startTime;
        if (elapsed < 800) {
          await new Promise(resolve => setTimeout(resolve, 800 - elapsed));
        }
        this.loading = false;
      }
    },
    async addRecurring(recurringData) {
      const authStore = useAuthStore();
      if (authStore.isGuest) {
        this.loading = true;
        await new Promise(resolve => setTimeout(resolve, 400));
        
        const newRec = {
          id: Date.now(),
          user_id: 0,
          amount: recurringData.amount,
          type: recurringData.type,
          category: recurringData.category,
          currency: recurringData.currency,
          description: recurringData.description || "",
          frequency: recurringData.frequency,
          next_run_date: recurringData.next_run_date,
          is_active: true,
          created_at: new Date().toISOString()
        };
        
        this.recurrings.unshift(newRec);
        this.loading = false;
        return newRec;
      }

      this.loading = true;
      try {
        const response = await api.post('/recurring/', recurringData);
        await this.fetchRecurrings();
        this.loading = false;
        return response.data;
      } catch (err) {
        this.loading = false;
        this.error = err.response?.data?.detail || 'Tạo giao dịch định kỳ thất bại';
        throw err;
      }
    },
    async deleteRecurring(id) {
      const authStore = useAuthStore();
      if (authStore.isGuest) {
        this.loading = true;
        await new Promise(resolve => setTimeout(resolve, 300));
        this.recurrings = this.recurrings.filter(r => r.id !== id);
        this.loading = false;
        return;
      }

      this.loading = true;
      try {
        await api.delete(`/recurring/${id}`);
        await this.fetchRecurrings();
        this.loading = false;
      } catch (err) {
        this.loading = false;
        this.error = err.response?.data?.detail || 'Xóa giao dịch định kỳ thất bại';
        throw err;
      }
    }
  },
});
