import { createRouter, createWebHashHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
  },
  {
    path: '/transactions',
    name: 'Transactions',
    component: () => import('../views/Transactions.vue'),
  },
  {
    path: '/budgets',
    name: 'Budgets',
    component: () => import('../views/Budgets.vue'),
  },
  {
    path: '/recurring',
    name: 'Recurring',
    component: () => import('../views/Recurring.vue'),
  },
  {
    path: '/toxic-ai',
    name: 'ToxicAI',
    component: () => import('../views/ToxicAI.vue'),
  },
  {
    path: '/yearly-summary',
    name: 'YearlySummary',
    component: () => import('../views/YearlySummary.vue'),
  },
  { path: '/:pathMatch(.*)*', name: 'NotFound', redirect: '/' },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const isAuthPath = to.path === '/login' || to.path === '/register';
  if (!isAuthPath && !authStore.isAuthenticated) {
    next('/login');
  } else {
    next();
  }
});

export default router;
