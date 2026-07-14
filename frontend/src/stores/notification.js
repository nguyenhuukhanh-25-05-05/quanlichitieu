import { defineStore } from 'pinia';
import { useAuthStore } from './auth';
import { getWsUrl } from '../utils/apiUrl';

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    alerts: [],
    socket: null,
    activeToast: null, // Holds the current visible toast alert
    dialog: {
      show: false,
      title: 'Thông báo',
      message: '',
      type: 'alert', // 'alert' | 'confirm'
      resolve: null,
    }
  }),
  actions: {
    showAlert(message, title = 'Thông báo') {
      this.dialog.show = false; // reset
      return new Promise((resolve) => {
        this.dialog = {
          show: true,
          title,
          message,
          type: 'alert',
          resolve,
        };
      });
    },
    showConfirm(message, title = 'Xác nhận') {
      this.dialog.show = false; // reset
      return new Promise((resolve) => {
        this.dialog = {
          show: true,
          title,
          message,
          type: 'confirm',
          resolve,
        };
      });
    },
    closeDialog(result) {
      if (this.dialog.resolve) {
        this.dialog.resolve(result);
      }
      this.dialog.show = false;
      this.dialog.resolve = null;
    },
    connectWebSocket() {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated || !authStore.user) return;

      const userId = authStore.user.id;
      const token = authStore.token;
      
      if (this.socket) {
        this.socket.close();
      }

      const wsBase = getWsUrl();
      const wsUrl = `${wsBase}/ws/${userId}`;
      this.socket = new WebSocket(wsUrl, [token]);

      this.socket.onmessage = (event) => {
        try {
          const alert = JSON.parse(event.data);
          const newAlert = {
            id: Date.now(),
            ...alert,
            read: false,
            time: new Date(),
          };
          this.alerts.unshift(newAlert);
          
          // Set as active toast
          this.activeToast = newAlert;
          
          // Auto clear toast after 8 seconds
          setTimeout(() => {
            if (this.activeToast?.id === newAlert.id) {
              this.activeToast = null;
            }
          }, 8000);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      this.socket.onclose = () => {
        // Reconnect after 5s if still logged in
        setTimeout(() => {
          const reAuth = useAuthStore();
          if (reAuth.isAuthenticated) {
            this.connectWebSocket();
          }
        }, 5000);
      };
    },
    disconnectWebSocket() {
      if (this.socket) {
        this.socket.close();
        this.socket = null;
      }
    },
    removeToast() {
      this.activeToast = null;
    },
    markAllAsRead() {
      this.alerts.forEach(a => a.read = true);
    }
  }
});
