<template>
  <div v-if="transactionStore.loading && transactionStore.transactions.length === 0" class="min-h-[70vh] flex items-center justify-center">
    <LoadingSpinner text="Generating" />
  </div>

  <div v-else class="space-y-6">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Nhật ký Giao dịch</h1>
        <p class="text-slate-500 text-xs mt-0.5">Danh sách đầy đủ các khoản thu nhập và chi tiêu của bạn.</p>
      </div>
      <button 
        @click="handleAddClick"
        class="btn-primary flex items-center gap-2 cursor-pointer self-start md:self-auto"
      >
        <Plus class="w-4 h-4" />
        <span>Giao dịch mới</span>
      </button>
    </div>

    <div class="glass-panel p-5 rounded-sm space-y-6 bg-white border border-slate-200 shadow-none">
      <div class="flex flex-col md:flex-row gap-4 justify-between">
        <div class="flex-1 max-w-md relative">
          <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
            <Search class="w-4 h-4" />
          </span>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Tìm kiếm theo mô tả..."
            class="w-full pr-4 py-2 rounded-sm glass-input text-xs"
            style="padding-left: 2.25rem !important;"
          />
        </div>

        <div class="flex items-center gap-3">
          <select 
            v-model="filterType"
            class="px-3 py-2 rounded-sm glass-input text-xs bg-white cursor-pointer font-bold w-40"
            style="padding-left: 1.25rem !important; padding-right: 2rem !important;"
          >
            <option value="all">Tất cả loại</option>
            <option value="income">Thu nhập</option>
            <option value="expense">Chi tiêu</option>
          </select>

          <select 
            v-model="filterCategory"
            class="px-3 py-2 rounded-sm glass-input text-xs bg-white cursor-pointer font-bold w-48"
            style="padding-left: 1.25rem !important; padding-right: 2rem !important;"
          >
            <option value="all">Tất cả danh mục</option>
            <option v-for="cat in allCategories" :key="cat" :value="cat">{{ cat }}</option>
          </select>
        </div>
      </div>

      <div v-if="filteredTransactions.length > 0" class="hidden sm:block overflow-x-auto">
        <table class="w-full text-center border-collapse text-xs">
          <thead>
            <tr class="text-slate-400 border-b border-slate-200 uppercase text-[9px] tracking-wider font-bold">
              <th class="py-3 px-4 border-r border-slate-200/60 text-center">Thời Gian</th>
              <th class="py-3 px-4 border-r border-slate-200/60 text-center">Danh Mục</th>
              <th class="py-3 px-4 border-r border-slate-200/60 text-center">Mô Tả</th>
              <th class="py-3 px-4 border-r border-slate-200/60 text-center">Số Tiền Gốc</th>
              <th class="py-3 px-4 border-r border-slate-200/60 text-center">Quy Đổi ({{ authStore.user?.currency }})</th>
              <th class="py-3 px-4 text-center">Hành Động</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="tx in filteredTransactions" 
              :key="tx.id"
              class="border-b border-slate-100 hover:bg-slate-50 transition"
            >
              <td class="py-3 px-4 border-r border-slate-100 text-slate-655 text-center">
                <span class="block font-bold font-mono text-[11px]">{{ formatDate(tx.date) }}</span>
                <span class="text-[9px] text-slate-400 font-mono mt-0.5 block">{{ formatTime(tx.date) }}</span>
              </td>
              <td class="py-3 px-4 border-r border-slate-100 text-center">
                <span class="px-2 py-0.5 rounded-sm text-[9px] font-bold uppercase tracking-wider" :class="getCategoryClass(tx.category)">
                  {{ tx.category }}
                </span>
              </td>
              <td class="py-3 px-4 border-r border-slate-100 text-slate-700 font-semibold truncate max-w-[200px] text-center" :title="tx.description">
                {{ tx.description || '-' }}
              </td>
              <td class="py-3 px-4 border-r border-slate-100 font-bold text-center text-slate-655 font-mono">
                {{ formatOriginalAmount(tx.amount, tx.currency) }}
              </td>
              <td class="py-3 px-4 border-r border-slate-100 font-bold text-center font-mono" :class="tx.type === 'income' ? 'text-emerald-600' : 'text-red-655'">
                {{ tx.type === 'income' ? '+' : '-' }}{{ formatBaseCurrency(tx.amount_base) }}
              </td>
              <td class="py-3 px-4 text-center">
                <button 
                  @click="handleDeleteClick(tx.id)"
                  class="p-1.5 rounded-sm text-slate-400 hover:text-red-600 hover:bg-red-50 active:scale-95 transition cursor-pointer"
                  title="Xóa giao dịch"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="filteredTransactions.length > 0" class="block sm:hidden space-y-3">
        <div 
          v-for="tx in filteredTransactions" 
          :key="tx.id"
          class="bg-white border border-slate-200 rounded-[20px] p-4 flex flex-col space-y-3 shadow-sm hover:border-purple-200 transition"
        >
          <!-- Top row: Category Badge & Actions -->
          <div class="flex justify-between items-center">
            <span class="px-2.5 py-0.5 rounded-full text-[9px] font-black uppercase tracking-wider" :class="getCategoryClass(tx.category)">
              {{ tx.category }}
            </span>
            <div class="flex items-center gap-1.5">
              <span class="text-[9px] text-slate-400 font-bold font-mono">{{ formatDate(tx.date) }} {{ formatTime(tx.date) }}</span>
              <button 
                @click="handleDeleteClick(tx.id)"
                class="p-1.5 rounded-full text-slate-400 hover:text-red-650 hover:bg-red-50 transition cursor-pointer"
                title="Xóa giao dịch"
              >
                <Trash2 class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
          
          <!-- Middle row: Description -->
          <div class="text-xs font-bold text-slate-800 break-words leading-relaxed">
            {{ tx.description || 'Không có mô tả' }}
          </div>
          
          <!-- Bottom row: Original and Converted Amount -->
          <div class="flex justify-between items-end border-t border-slate-50 pt-2 pb-0.5">
            <div>
              <div class="text-[9px] text-slate-400 font-bold uppercase tracking-wider mb-0.5">Số tiền gốc</div>
              <div class="text-[11px] font-bold text-slate-655 font-mono">{{ formatOriginalAmount(tx.amount, tx.currency) }}</div>
            </div>
            <div class="text-right">
              <div class="text-[9px] text-slate-400 font-bold uppercase tracking-wider mb-0.5">Quy đổi ({{ authStore.user?.currency }})</div>
              <div class="text-xs font-extrabold font-mono" :class="tx.type === 'income' ? 'text-emerald-600' : 'text-red-655'">
                {{ tx.type === 'income' ? '+' : '-' }}{{ formatBaseCurrency(tx.amount_base) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-12 text-slate-400">
        <History class="w-12 h-12 stroke-[1.2] mb-3 text-slate-350" />
        <h3 class="font-bold text-base text-slate-600">Không tìm thấy giao dịch</h3>
        <p class="text-xs mt-1 text-slate-400">Thử đổi bộ lọc hoặc thêm giao dịch mới để bắt đầu.</p>
      </div>
    </div>

    <div v-if="showAddModal" class="fixed inset-0 bg-black/20 z-50 flex items-center justify-center p-4 select-none">
      <div class="w-full max-w-sm bg-white border border-slate-200 rounded-[30px] p-6 space-y-4 shadow-xl">
        <div class="flex justify-between items-center border-b border-slate-100 pb-2">
          <h3 class="font-bold text-sm text-slate-800 uppercase tracking-wider">Thêm giao dịch mới</h3>
          <button @click="showAddModal = false" class="p-1 rounded-sm text-slate-400 hover:text-slate-800 hover:bg-slate-100 transition cursor-pointer">
            <X class="w-4.5 h-4.5" />
          </button>
        </div>

        <form @submit.prevent="submitAdd" class="space-y-3">
          <div class="grid grid-cols-2 gap-2 bg-slate-50 p-1 border border-slate-200 rounded-full">
            <button 
              type="button" 
              @click="form.type = 'expense'"
              class="py-1.5 rounded-full font-bold text-xs cursor-pointer transition flex items-center justify-center gap-1"
              :class="form.type === 'expense' ? 'bg-white text-red-655 shadow-sm border border-slate-200' : 'text-slate-500'"
            >
              <ArrowDownRight class="w-3.5 h-3.5" />
              <span>Chi tiêu</span>
            </button>
            <button 
              type="button" 
              @click="form.type = 'income'"
              class="py-1.5 rounded-full font-bold text-xs cursor-pointer transition flex items-center justify-center gap-1"
              :class="form.type === 'income' ? 'bg-white text-emerald-655 shadow-sm border border-slate-200' : 'text-slate-500'"
            >
              <ArrowUpRight class="w-3.5 h-3.5" />
              <span>Thu nhập</span>
            </button>
          </div>

          <div class="grid grid-cols-3 gap-2">
            <div class="col-span-2">
              <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Số tiền</label>
              <input 
                v-model="amountInputStr" 
                type="text" 
                required 
                placeholder="0"
                class="w-full mt-1 glass-input font-bold font-mono text-sm"
                @input="onAmountInput"
              />
            </div>
            <div>
              <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Tiền tệ</label>
              <select v-model="form.currency" class="w-full mt-1 glass-input text-xs bg-white cursor-pointer font-bold">
                <option value="VND">VND</option>
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
              </select>
            </div>
          </div>

          <div v-if="form.currency !== authStore.user?.currency" class="text-[11px] text-purple-700 bg-purple-50/50 p-2 rounded-full border border-purple-100 flex justify-between items-center gap-1">
            <span>Tỷ giá quy đổi:</span>
            <input 
              v-model.number="form.exchange_rate" 
              type="number" 
              step="0.0001"
              class="inline-block w-16 px-1 py-0.5 bg-white rounded-full border border-slate-200 text-center font-bold font-mono text-xs"
            />
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Danh mục</label>
              <select v-model="form.category" class="w-full mt-1 glass-input text-xs bg-white cursor-pointer font-bold">
                <option v-for="cat in availableCategories" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </div>
            <div>
              <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Thời gian</label>
              <input 
                v-model="form.date" 
                type="datetime-local" 
                required
                class="w-full mt-1 glass-input text-xs font-mono"
              />
            </div>
          </div>

          <div>
            <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Mô tả chi tiết</label>
            <input 
              v-model="form.description" 
              type="text" 
              placeholder="Ví dụ: Đóng tiền trọ tháng này"
              class="w-full mt-1 glass-input"
            />
          </div>

          <button 
            type="submit" 
            :disabled="adding"
            class="w-full btn-primary mt-2"
          >
            <Loader2 v-if="adding" class="w-4 h-4 animate-spin" />
            <span>Thêm giao dịch</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useTransactionStore } from '../stores/transaction';
import { useNotificationStore } from '../stores/notification';
import LoadingSpinner from '../components/LoadingSpinner.vue';
import { formatCurrency, formatOriginalAmount, formatDate, formatTime } from '../utils/format';
import { useAmountInput } from '../composables/useAmountInput';
import { categories, getCategoryClass } from '../utils/categories';
import { defaultExchangeRates } from '../utils/constants';
import { Plus, Search, Trash2, X, History, ArrowDownRight, ArrowUpRight, Loader2 } from 'lucide-vue-next';

const router = useRouter();
const authStore = useAuthStore();
const transactionStore = useTransactionStore();
const notificationStore = useNotificationStore();

const showAddModal = ref(false);
const adding = ref(false);

const searchQuery = ref('');
const filterType = ref('all');
const filterCategory = ref('all');

const form = reactive({
  amount: null,
  type: 'expense',
  category: 'Ăn uống',
  currency: 'VND',
  exchange_rate: 1.0,
  description: '',
  date: '',
});

watch(() => [form.currency, authStore.user?.currency], () => {
  const userBase = authStore.user?.currency || 'VND';
  const inputCurr = form.currency;
  if (defaultExchangeRates[inputCurr] && defaultExchangeRates[inputCurr][userBase]) {
    form.exchange_rate = defaultExchangeRates[inputCurr][userBase];
  } else {
    form.exchange_rate = 1.0;
  }
});

const allCategories = computed(() => {
  return [...categories.expense, ...categories.income];
});

const availableCategories = computed(() => {
  return categories[form.type];
});

watch(() => form.type, (newType) => {
  form.category = categories[newType][0];
});

const setFormDefaultDate = () => {
  const now = new Date();
  const offset = now.getTimezoneOffset() * 60000;
  const localISOTime = (new Date(now - offset)).toISOString().slice(0, 16);
  form.date = localISOTime;
};

onMounted(async () => {
  await transactionStore.fetchTransactions();
  const userBase = authStore.user?.currency || 'VND';
  form.currency = userBase;
  setFormDefaultDate();
});

const filteredTransactions = computed(() => {
  let list = transactionStore.transactions;
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    list = list.filter(tx => tx.description?.toLowerCase().includes(q));
  }
  
  if (filterType.value !== 'all') {
    list = list.filter(tx => tx.type === filterType.value);
  }
  
  if (filterCategory.value !== 'all') {
    list = list.filter(tx => tx.category === filterCategory.value);
  }
  
  return list;
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
  deleteTx(id);
};

const promptLogin = async () => {
  await notificationStore.showAlert('Vui lòng đăng nhập để thực hiện tính năng này!', 'Yêu cầu Đăng nhập');
  router.push('/login');
};

const deleteTx = async (id) => {
  const confirmResult = await notificationStore.showConfirm('Bạn có chắc chắn muốn xóa giao dịch này không?', 'Xác nhận xóa');
  if (confirmResult) {
    await transactionStore.deleteTransaction(id);
  }
};

const submitAdd = async () => {
  adding.value = true;
  try {
    const formattedDate = new Date(form.date).toISOString();
    await transactionStore.addTransaction({
      amount: form.amount,
      type: form.type,
      category: form.category,
      currency: form.currency,
      exchange_rate: form.exchange_rate,
      description: form.description || null,
      date: formattedDate
    });
    
    form.amount = null;
    form.description = '';
    setFormDefaultDate();
    showAddModal.value = false;
  } catch (err) {
    notificationStore.showAlert(err.response?.data?.detail || 'Thêm giao dịch thất bại', 'Lỗi');
  } finally {
    adding.value = false;
  }
};

const formatBaseCurrency = (value) => {
  const currency = authStore.user?.currency || 'VND';
  if (currency === 'VND') {
    return value.toLocaleString('vi-VN') + ' ₫';
  } else if (currency === 'USD') {
    return '$' + value.toLocaleString('en-US', { minimumFractionDigits: 2 });
  } else {
    return '€' + value.toLocaleString('en-US', { minimumFractionDigits: 2 });
  }
};

const { amountInputStr, onAmountInput } = useAmountInput(form, 'amount');

</script>
