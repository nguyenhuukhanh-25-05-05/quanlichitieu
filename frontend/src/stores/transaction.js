import { defineStore } from 'pinia';
import api from '../services/api';
import { useAuthStore } from './auth';
import { useBudgetStore } from './budget';
import { useNotificationStore } from './notification';
import { mockTransactions, calculateMockSummary, generateMockInsights, round } from '../mocks/mockData';

export const useTransactionStore = defineStore('transaction', {
  state: () => ({
    transactions: [],
    summary: null,
    insights: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchTransactions() {
      this.loading = true;
      const startTime = Date.now();
      const authStore = useAuthStore();
      
      try {
        if (authStore.isGuest) {
          if (this.transactions.length === 0) {
            this.transactions = [...mockTransactions];
          }
        } else {
          const response = await api.get('/transactions/');
          this.transactions = response.data;
        }
      } catch (err) {
        this.error = err.response?.data?.detail || 'Lấy danh sách giao dịch thất bại';
      } finally {
        const elapsed = Date.now() - startTime;
        if (elapsed < 800) {
          await new Promise(resolve => setTimeout(resolve, 800 - elapsed));
        }
        this.loading = false;
      }
    },
    async fetchSummary() {
      const authStore = useAuthStore();
      if (authStore.isGuest) {
        if (this.transactions.length === 0) {
          this.transactions = [...mockTransactions];
        }
        this.summary = calculateMockSummary(this.transactions);
        return;
      }
      
      try {
        const response = await api.get('/transactions/summary');
        this.summary = response.data;
      } catch (err) {
        console.error('Failed to fetch summary:', err);
      }
    },
    async fetchInsights() {
      const authStore = useAuthStore();
      if (authStore.isGuest) {
        if (this.transactions.length === 0) {
          this.transactions = [...mockTransactions];
        }
        const s = calculateMockSummary(this.transactions);
        this.insights = generateMockInsights(s);
        return;
      }

      try {
        const response = await api.get('/transactions/insights');
        this.insights = response.data;
      } catch (err) {
        console.error('Failed to fetch insights:', err);
      }
    },
    async addTransaction(transactionData) {
      const authStore = useAuthStore();
      if (authStore.isGuest) {
        this.loading = true;
        await new Promise(resolve => setTimeout(resolve, 500));
        const newTx = {
          id: Date.now(),
          user_id: 0,
          amount: transactionData.amount,
          amount_base: transactionData.amount * transactionData.exchange_rate,
          type: transactionData.type,
          category: transactionData.category,
          currency: transactionData.currency,
          exchange_rate: transactionData.exchange_rate,
          description: transactionData.description || "",
          date: transactionData.date || new Date().toISOString(),
          created_at: new Date().toISOString()
        };
        
        this.transactions.unshift(newTx);
        
        // Re-calculate balance in authStore demoUser
        const balanceChange = newTx.type === 'income' ? newTx.amount_base : -newTx.amount_base;
        authStore.user.balance += balanceChange;
        
        this.summary = calculateMockSummary(this.transactions);
        this.insights = generateMockInsights(this.summary);
        
        // Dynamic check for budget alerts
        const budgetStore = useBudgetStore();
        const budget = budgetStore.budgets.find(b => b.budget.category === newTx.category);
        if (budget && newTx.type === 'expense') {
          budget.budget.current_spend += newTx.amount_base;
          budget.percent_used = round((budget.budget.current_spend / budget.budget.amount_limit * 100), 2);
          budget.is_exceeded = budget.budget.current_spend >= budget.budget.amount_limit;
          
          // Trigger websocket notification mock
          if (budget.is_exceeded) {
            const notifStore = useNotificationStore();
            notifStore.alerts.unshift({
              id: Date.now(),
              type: "BUDGET_ALERT",
              level: "CRITICAL",
              message: `Nguy cấp! Bạn đã chi tiêu ${budget.budget.current_spend.toLocaleString()} / ${budget.budget.amount_limit.toLocaleString()} VND vượt hạn mức chi tiêu cho '${newTx.category}'!`,
              read: false,
              time: new Date()
            });
            notifStore.activeToast = notifStore.alerts[0];
          }
        }
        
        this.loading = false;
        return newTx;
      }
      
      this.loading = true;
      try {
        const response = await api.post('/transactions/', transactionData);
        await this.fetchTransactions();
        await this.fetchSummary();
        await this.fetchInsights();
        this.loading = false;
        return response.data;
      } catch (err) {
        this.loading = false;
        this.error = err.response?.data?.detail || 'Thêm giao dịch thất bại';
        throw err;
      }
    },
    async deleteTransaction(id) {
      const authStore = useAuthStore();
      if (authStore.isGuest) {
        this.loading = true;
        await new Promise(resolve => setTimeout(resolve, 300));
        
        const txIndex = this.transactions.findIndex(t => t.id === id);
        if (txIndex !== -1) {
          const tx = this.transactions[txIndex];
          const balanceChange = tx.type === 'income' ? -tx.amount_base : tx.amount_base;
          authStore.user.balance += balanceChange;
          
          // Revert budget spend if expense
          if (tx.type === 'expense') {
            const budgetStore = useBudgetStore();
            const budget = budgetStore.budgets.find(b => b.budget.category === tx.category);
            if (budget) {
              budget.budget.current_spend = Math.max(0, budget.budget.current_spend - tx.amount_base);
              budget.percent_used = round((budget.budget.current_spend / budget.budget.amount_limit * 100), 2);
              budget.is_exceeded = budget.budget.current_spend >= budget.budget.amount_limit;
            }
          }

          this.transactions.splice(txIndex, 1);
        }
        
        this.summary = calculateMockSummary(this.transactions);
        this.insights = generateMockInsights(this.summary);
        this.loading = false;
        return;
      }
      
      this.loading = true;
      try {
        await api.delete(`/transactions/${id}`);
        await this.fetchTransactions();
        await this.fetchSummary();
        await this.fetchInsights();
        this.loading = false;
      } catch (err) {
        this.loading = false;
        this.error = err.response?.data?.detail || 'Xóa giao dịch thất bại';
        throw err;
      }
    },
    async downloadCSV() {
      const authStore = useAuthStore();
      if (authStore.isGuest) {
        const url = 'data:text/csv;charset=utf-8,' + encodeURIComponent(
          "Mã Giao Dịch,Thời Gian,Loại,Danh Mục,Số Tiền Gốc,Đơn Vị Tiền Tệ,Tỷ Giá Quy Đổi,Số Tiền Quy Đổi,Mô Tả\n" +
          mockTransactions.map(t => `${t.id},${t.date},${t.type === 'income' ? 'Thu nhập' : 'Chi tiêu'},${t.category},${t.amount},${t.currency},${t.exchange_rate},${t.amount_base},${t.description}`).join("\n")
        );
        const a = document.createElement('a');
        a.href = url;
        a.download = 'aura_finance_report.csv';
        a.click();
        return;
      }
      try {
        const response = await api.get('/reports/csv', { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/csv;charset=utf-8' }));
        const a = document.createElement('a');
        a.href = url;
        a.download = `aura_finance_report_${new Date().toISOString().slice(0, 10)}.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      } catch (err) {
        const notificationStore = useNotificationStore();
        notificationStore.showAlert(err.response?.data?.detail || 'Không thể xuất báo cáo CSV', 'Lỗi xuất CSV');
      }
    }
  },
});
