import { defineStore } from 'pinia';
import api from '../services/api';
import { useAuthStore } from './auth';
import { mockBudgets } from '../mocks/mockData';

export const useBudgetStore = defineStore('budget', {
  state: () => ({
    budgets: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchBudgets() {
      this.loading = true;
      const startTime = Date.now();
      const authStore = useAuthStore();
      
      try {
        if (authStore.isGuest) {
          if (this.budgets.length === 0) {
            this.budgets = [...mockBudgets];
          }
        } else {
          const response = await api.get('/budgets/');
          this.budgets = response.data;
        }
      } catch (err) {
        this.error = err.response?.data?.detail || 'Lấy danh sách ngân sách thất bại';
      } finally {
        const elapsed = Date.now() - startTime;
        if (elapsed < 800) {
          await new Promise(resolve => setTimeout(resolve, 800 - elapsed));
        }
        this.loading = false;
      }
    },
    async addBudget(budgetData) {
      const authStore = useAuthStore();
      if (authStore.isGuest) {
        this.loading = true;
        await new Promise(resolve => setTimeout(resolve, 400));
        
        const newBudgetStatus = {
          budget: {
            id: Date.now(),
            user_id: 0,
            category: budgetData.category,
            amount_limit: budgetData.amount_limit,
            current_spend: 0, // Freshly created
            period: budgetData.period,
            start_date: budgetData.start_date,
            end_date: budgetData.end_date,
            created_at: new Date().toISOString()
          },
          percent_used: 0,
          is_exceeded: false
        };
        
        // Recalculate based on existing guest transactions
        const txStore = await import('./transaction').then(m => m.useTransactionStore());
        const start = new Date(budgetData.start_date);
        const end = new Date(budgetData.end_date);
        
        const matchSpend = txStore.transactions
          .filter(t => t.category === budgetData.category && t.type === 'expense' && new Date(t.date) >= start && new Date(t.date) <= end)
          .reduce((sum, t) => sum + t.amount_base, 0);
          
        newBudgetStatus.budget.current_spend = matchSpend;
        newBudgetStatus.percent_used = budgetData.amount_limit > 0 ? parseFloat((matchSpend / budgetData.amount_limit * 100).toFixed(2)) : 0;
        newBudgetStatus.is_exceeded = matchSpend >= budgetData.amount_limit;

        this.budgets.unshift(newBudgetStatus);
        this.loading = false;
        return newBudgetStatus.budget;
      }

      this.loading = true;
      try {
        const response = await api.post('/budgets/', budgetData);
        await this.fetchBudgets();
        this.loading = false;
        return response.data;
      } catch (err) {
        this.loading = false;
        this.error = err.response?.data?.detail || 'Tạo ngân sách thất bại';
        throw err;
      }
    },
    async deleteBudget(id) {
      const authStore = useAuthStore();
      if (authStore.isGuest) {
        this.loading = true;
        await new Promise(resolve => setTimeout(resolve, 300));
        this.budgets = this.budgets.filter(b => b.budget.id !== id);
        this.loading = false;
        return;
      }

      this.loading = true;
      try {
        await api.delete(`/budgets/${id}`);
        await this.fetchBudgets();
        this.loading = false;
      } catch (err) {
        this.loading = false;
        this.error = err.response?.data?.detail || 'Xóa ngân sách thất bại';
        throw err;
      }
    }
  },
});
