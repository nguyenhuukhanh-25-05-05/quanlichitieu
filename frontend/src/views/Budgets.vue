<template>
  <div v-if="budgetStore.loading && budgetStore.budgets.length === 0" class="min-h-[70vh] flex items-center justify-center">
    <LoadingSpinner text="Generating" />
  </div>

  <div v-else class="space-y-6">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Hạn mức Chi tiêu</h1>
        <p class="text-slate-500 text-sm mt-0.5">Kiểm soát ngân sách của bạn để tránh chi tiêu quá đà.</p>
      </div>
      <button 
        @click="handleAddClick"
        class="btn-primary flex items-center gap-2 cursor-pointer self-start md:self-auto"
      >
        <Plus class="w-4 h-4" />
        <span>Thiết lập Ngân sách</span>
      </button>
    </div>

    <div v-if="budgetStore.budgets.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="budgetStatus in budgetStore.budgets" 
        :key="budgetStatus.budget.id"
        class="glass-panel p-5 rounded-sm relative overflow-hidden flex flex-col justify-between min-h-[180px] bg-white border border-slate-200 shadow-none"
        :class="budgetStatus.is_exceeded ? 'border-red-400 bg-red-50/10' : ''"
      >
        <div class="flex justify-between items-start mb-4">
          <div>
            <span class="px-2.5 py-0.5 rounded-sm text-[9px] font-bold uppercase tracking-wider" :class="getCategoryClass(budgetStatus.budget.category)">
              {{ budgetStatus.budget.category }}
            </span>
            <p class="text-xs text-slate-550 mt-2 font-bold font-mono">
              Hạn: {{ formatDate(budgetStatus.budget.start_date) }} - {{ formatDate(budgetStatus.budget.end_date) }}
            </p>
          </div>
          <button 
            @click="handleDeleteClick(budgetStatus.budget.id)"
            class="text-slate-450 hover:text-red-500 p-1 rounded-sm hover:bg-slate-100 active:scale-95 transition cursor-pointer"
            title="Xóa ngân sách"
          >
            <Trash2 class="w-4 h-4" />
          </button>
        </div>

        <div class="space-y-2 mt-auto">
          <div class="flex justify-between text-xs">
            <span class="text-slate-550 font-semibold">Đã tiêu</span>
            <span class="font-bold text-slate-800 font-mono">
              {{ formatCurrency(budgetStatus.budget.current_spend) }} / {{ formatCurrency(budgetStatus.budget.amount_limit) }}
            </span>
          </div>

          <div class="w-full bg-slate-100 rounded-none h-2.5 overflow-hidden border border-slate-200">
            <div 
              class="h-full transition-all duration-500" 
              :class="getProgressColorClass(budgetStatus.percent_used, budgetStatus.is_exceeded)"
              :style="{ width: Math.min(budgetStatus.percent_used, 100) + '%' }"
            ></div>
          </div>

          <div class="flex justify-between text-[10px] font-bold uppercase tracking-wide">
            <span :class="budgetStatus.is_exceeded ? 'text-red-655' : 'text-slate-500'">
              {{ budgetStatus.is_exceeded ? 'Vượt quá hạn mức!' : 'Trong tầm kiểm soát' }}
            </span>
            <span class="font-black font-mono" :class="budgetStatus.is_exceeded ? 'text-red-655' : 'text-slate-550'">
              {{ budgetStatus.percent_used }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="glass-panel p-12 rounded-sm flex flex-col items-center justify-center text-slate-500 min-h-[250px] bg-white border border-slate-200 shadow-none">
      <ShieldAlert class="w-12 h-12 stroke-[1.2] mb-3 text-slate-400" />
      <h3 class="font-bold text-base text-slate-700">Chưa thiết lập ngân sách</h3>
      <p class="text-xs mt-1 mb-6 text-center max-w-md text-slate-555">Thiết lập ngân sách giúp hệ thống gửi thông báo WebSocket cảnh báo cho bạn trước khi ví tiền bị thâm hụt.</p>
      <button 
        @click="handleAddClick"
        class="btn-primary flex items-center gap-2 cursor-pointer"
      >
        Tạo ngân sách đầu tiên
      </button>
    </div>

    <div v-if="showAddModal" class="fixed inset-0 bg-black/20 z-50 flex items-center justify-center p-4 select-none">
      <div class="w-full max-w-sm bg-white border border-slate-200 rounded-[30px] p-6 space-y-4 shadow-xl">
        <div class="flex justify-between items-center border-b border-slate-100 pb-2">
          <h3 class="font-bold text-sm text-slate-800 uppercase tracking-wider">Thiết lập Ngân sách mới</h3>
          <button @click="showAddModal = false" class="p-1 rounded-sm text-slate-400 hover:text-slate-800 hover:bg-slate-100 transition cursor-pointer">
            <X class="w-4.5 h-4.5" />
          </button>
        </div>

        <form @submit.prevent="submitAdd" class="space-y-3">
          <div>
            <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Danh mục áp dụng</label>
            <select v-model="form.category" class="w-full mt-1 glass-input text-xs bg-white cursor-pointer font-bold">
              <option v-for="cat in expenseCategories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>

          <div>
            <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Hạn mức ngân sách ({{ authStore.user?.currency }})</label>
            <input 
              v-model="amountInputStr" 
              type="text" 
              required 
              placeholder="0"
              class="w-full mt-1 glass-input font-bold font-mono text-sm"
              @input="onAmountInput"
            />
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Ngày bắt đầu</label>
              <input 
                v-model="form.start_date" 
                type="date" 
                required
                :max="form.end_date"
                class="w-full mt-1 glass-input text-xs font-mono"
              />
            </div>
            <div>
              <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Ngày kết thúc</label>
              <input 
                v-model="form.end_date" 
                type="date" 
                required
                :min="form.start_date"
                class="w-full mt-1 glass-input text-xs font-mono"
              />
            </div>
          </div>

          <button 
            type="submit" 
            :disabled="adding"
            class="w-full btn-primary mt-2"
          >
            <Loader2 v-if="adding" class="w-4 h-4 animate-spin" />
            <span>Kích hoạt ngân sách</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useBudgetStore } from '../stores/budget';
import { useNotificationStore } from '../stores/notification';
import LoadingSpinner from '../components/LoadingSpinner.vue';
import { formatCurrency, formatOriginalAmount, formatDate } from '../utils/format';
import { useAmountInput } from '../composables/useAmountInput';
import { categories, getCategoryClass } from '../utils/categories';
import { Plus, Trash2, X, ShieldAlert, Loader2 } from 'lucide-vue-next';

const router = useRouter();
const authStore = useAuthStore();
const budgetStore = useBudgetStore();
const notificationStore = useNotificationStore();

const showAddModal = ref(false);
const adding = ref(false);

const expenseCategories = ['Ăn uống', 'Di chuyển', 'Mua sắm', 'Nhà cửa', 'Giải trí', 'Học tập', 'Y tế', 'Khác'];

const form = reactive({
  category: 'Ăn uống',
  amount_limit: null,
  start_date: '',
  end_date: '',
});

const setDateDefaults = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();
  
  const start = new Date(year, month, 1);
  const end = new Date(year, month + 1, 0);
  
  const toISODate = (d) => d.toISOString().slice(0, 10);
  form.start_date = toISODate(start);
  form.end_date = toISODate(end);
};

onMounted(async () => {
  await budgetStore.fetchBudgets();
  setDateDefaults();
});

const handleAddClick = () => {
  if (authStore.isGuest) {
    promptLogin();
    return;
  }
  showAddModal.value = true;
};

const handleDeleteClick = (id) => {
  if (authStore.isGuest) {
    promptLogin();
    return;
  }
  deleteBudget(id);
};

const promptLogin = async () => {
  await notificationStore.showAlert('Vui lòng đăng nhập để thực hiện tính năng này!', 'Yêu cầu Đăng nhập');
  router.push('/login');
};

const deleteBudget = async (id) => {
  const confirmResult = await notificationStore.showConfirm('Bạn có chắc chắn muốn xóa ngân sách này không?', 'Xác nhận xóa');
  if (confirmResult) {
    await budgetStore.deleteBudget(id);
  }
};

const submitAdd = async () => {
  if (new Date(form.start_date) > new Date(form.end_date)) {
    notificationStore.showAlert('Ngày bắt đầu không được lớn hơn ngày kết thúc!', 'Lỗi nhập ngày');
    return;
  }
  adding.value = true;
  try {
    const formattedStart = new Date(form.start_date).toISOString();
    const formattedEnd = new Date(form.end_date).toISOString();
    
    await budgetStore.addBudget({
      category: form.category,
      amount_limit: form.amount_limit,
      start_date: formattedStart,
      end_date: formattedEnd,
      period: 'monthly'
    });
    
    form.amount_limit = null;
    setDateDefaults();
    showAddModal.value = false;
  } catch (err) {
    notificationStore.showAlert(err.response?.data?.detail || 'Thao tác lỗi', 'Lỗi');
  } finally {
    adding.value = false;
  }
};

const { amountInputStr, onAmountInput } = useAmountInput(form, 'amount_limit');

</script>
