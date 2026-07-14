<template>
  <div v-if="recurringStore.loading && recurringStore.recurrings.length === 0" class="min-h-[70vh] flex items-center justify-center">
    <LoadingSpinner text="Generating" />
  </div>

  <div v-else class="space-y-6">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Giao dịch Định kỳ</h1>
        <p class="text-slate-500 text-sm mt-0.5">Tự động chèn các khoản thu/chi lặp lại theo lịch cố định.</p>
      </div>
      <button 
        @click="handleAddClick"
        class="btn-primary flex items-center gap-2 cursor-pointer self-start md:self-auto"
      >
        <Plus class="w-4 h-4" />
        <span>Tạo giao dịch định kỳ</span>
      </button>
    </div>

    <div v-if="recurringStore.recurrings.length > 0" class="glass-panel p-5 rounded-sm bg-white border border-slate-200 shadow-none">
      <div class="hidden sm:block overflow-x-auto">
        <table class="w-full text-center border-collapse text-xs">
          <thead>
            <tr class="text-slate-400 border-b border-slate-200 uppercase text-[9px] tracking-wider font-bold">
              <th class="py-3 px-4 border-r border-slate-200/60 text-center">Tần suất</th>
              <th class="py-3 px-4 border-r border-slate-200/60 text-center">Danh mục</th>
              <th class="py-3 px-4 border-r border-slate-200/60 text-center">Mô tả</th>
              <th class="py-3 px-4 border-r border-slate-200/60 text-center">Ngày thực thi kế tiếp</th>
              <th class="py-3 px-4 border-r border-slate-200/60 text-center">Số tiền gốc</th>
              <th class="py-3 px-4 border-r border-slate-200/60 text-center">Trạng thái</th>
              <th class="py-3 px-4 text-center">Hành động</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="rec in recurringStore.recurrings" 
              :key="rec.id"
              class="border-b border-slate-100 hover:bg-slate-50 transition"
            >
              <td class="py-3 px-4 border-r border-slate-100 capitalize font-semibold text-slate-700 text-center">
                <span class="px-2 py-0.5 rounded-sm text-[9px] font-bold bg-slate-100 border border-slate-200 uppercase tracking-wide">
                  {{ formatFrequency(rec.frequency) }}
                </span>
              </td>
              <td class="py-3 px-4 border-r border-slate-100 text-center">
                <span class="px-2 py-0.5 rounded-sm text-[9px] font-bold uppercase tracking-wider" :class="getCategoryClass(rec.category)">
                  {{ rec.category }}
                </span>
              </td>
              <td class="py-3 px-4 border-r border-slate-100 text-slate-700 font-semibold truncate max-w-[200px] text-center" :title="rec.description">
                {{ rec.description || '-' }}
              </td>
              <td class="py-3 px-4 border-r border-slate-100 text-purple-600 font-mono font-bold text-xs text-center">{{ formatDate(rec.next_run_date) }}</td>
              <td class="py-3 px-4 border-r border-slate-100 font-bold text-center font-mono" :class="rec.type === 'income' ? 'text-emerald-600' : 'text-red-655'">
                {{ rec.type === 'income' ? '+' : '-' }}{{ formatOriginalAmount(rec.amount, rec.currency) }}
              </td>
              <td class="py-3 px-4 border-r border-slate-100 text-center">
                <span 
                  class="px-2 py-0.5 rounded-sm text-[9px] font-bold border uppercase tracking-wider"
                  :class="rec.is_active ? 'bg-emerald-50 text-emerald-700 border-emerald-100' : 'bg-slate-50 text-slate-500 border-slate-200'"
                >
                  {{ rec.is_active ? 'Đang chạy' : 'Đã ngưng' }}
                </span>
              </td>
              <td class="py-3 px-4 text-center">
                <button 
                  @click="handleDeleteClick(rec.id)"
                  class="p-1.5 rounded-sm text-slate-400 hover:text-red-600 hover:bg-red-50 active:scale-95 transition cursor-pointer"
                  title="Hủy tự động"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="block sm:hidden space-y-3">
        <div 
          v-for="rec in recurringStore.recurrings" 
          :key="rec.id"
          class="bg-white border border-slate-200 rounded-[20px] p-4 flex flex-col space-y-3 shadow-sm hover:border-purple-200 transition"
        >
          <!-- Top row: Category Badge & Status/Actions -->
          <div class="flex justify-between items-center">
            <span class="px-2.5 py-0.5 rounded-full text-[9px] font-black uppercase tracking-wider" :class="getCategoryClass(rec.category)">
              {{ rec.category }}
            </span>
            <div class="flex items-center gap-1.5">
              <span 
                class="px-2 py-0.5 rounded-full text-[8px] font-black border uppercase tracking-wider"
                :class="rec.is_active ? 'bg-emerald-50 text-emerald-700 border-emerald-100' : 'bg-slate-50 text-slate-500 border-slate-200'"
              >
                {{ rec.is_active ? 'Đang chạy' : 'Đã ngưng' }}
              </span>
              <button 
                @click="handleDeleteClick(rec.id)"
                class="p-1.5 rounded-full text-slate-400 hover:text-red-650 hover:bg-red-50 transition cursor-pointer"
                title="Hủy tự động"
              >
                <Trash2 class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
          
          <!-- Middle row: Description & Next Run -->
          <div class="space-y-1">
            <div class="text-xs font-bold text-slate-800 break-words leading-relaxed">
              {{ rec.description || 'Không có mô tả' }}
            </div>
            <div class="text-[10px] text-slate-500 font-medium">
              Thực thi kế tiếp: <span class="text-purple-650 font-mono font-bold">{{ formatDate(rec.next_run_date) }}</span>
            </div>
          </div>
          
          <!-- Bottom row: Frequency & Amount -->
          <div class="flex justify-between items-end border-t border-slate-50 pt-2 pb-0.5">
            <div>
              <div class="text-[9px] text-slate-400 font-bold uppercase tracking-wider mb-0.5">Tần suất</div>
              <span class="px-2 py-0.5 rounded-sm text-[9px] font-bold bg-slate-100 border border-slate-200 uppercase tracking-wide font-mono">
                {{ formatFrequency(rec.frequency) }}
              </span>
            </div>
            <div class="text-right">
              <div class="text-[9px] text-slate-400 font-bold uppercase tracking-wider mb-0.5">Số tiền gốc</div>
              <div class="text-xs font-extrabold font-mono" :class="rec.type === 'income' ? 'text-emerald-600' : 'text-red-655'">
                {{ rec.type === 'income' ? '+' : '-' }}{{ formatOriginalAmount(rec.amount, rec.currency) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="glass-panel p-12 rounded-sm flex flex-col items-center justify-center text-slate-500 min-h-[250px] bg-white border border-slate-200 shadow-none">
      <CalendarClock class="w-12 h-12 stroke-[1.2] mb-3 text-slate-400" />
      <h3 class="font-bold text-base text-slate-700">Không có lịch trình lặp lại</h3>
      <p class="text-xs mt-1 mb-6 text-center max-w-md text-slate-555">Thiết lập các khoản đóng tiền nhà, đăng ký Netflix hàng tháng hay nhận lương để hệ thống tự động hóa giúp bạn.</p>
      <button 
        @click="handleAddClick"
        class="btn-primary flex items-center gap-2 cursor-pointer"
      >
        Lên lịch đầu tiên
      </button>
    </div>

    <div v-if="showAddModal" class="fixed inset-0 bg-black/20 z-50 flex items-center justify-center p-4 select-none">
      <div class="w-full max-w-sm bg-white border border-slate-200 rounded-[30px] p-6 space-y-4 shadow-xl">
        <div class="flex justify-between items-center border-b border-slate-100 pb-2">
          <h3 class="font-bold text-sm text-slate-800 uppercase tracking-wider">Lên lịch giao dịch mới</h3>
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
              <span>Khoản chi lặp lại</span>
            </button>
            <button 
              type="button" 
              @click="form.type = 'income'"
              class="py-1.5 rounded-full font-bold text-xs cursor-pointer transition flex items-center justify-center gap-1"
              :class="form.type === 'income' ? 'bg-white text-emerald-655 shadow-sm border border-slate-200' : 'text-slate-500'"
            >
              <ArrowUpRight class="w-3.5 h-3.5" />
              <span>Khoản thu lặp lại</span>
            </button>
          </div>

          <div class="grid grid-cols-3 gap-2">
            <div class="col-span-2">
              <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Số tiền gốc</label>
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

          <div class="grid grid-cols-3 gap-2">
            <div class="col-span-2">
              <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Danh mục</label>
              <select v-model="form.category" class="w-full mt-1 glass-input text-xs bg-white cursor-pointer font-bold">
                <option v-for="cat in availableCategories" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </div>
            <div>
              <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Chu kỳ</label>
              <select v-model="form.frequency" class="w-full mt-1 glass-input text-xs bg-white cursor-pointer font-bold">
                <option value="daily">Hàng ngày</option>
                <option value="weekly">Hàng tuần</option>
                <option value="monthly">Hàng tháng</option>
              </select>
            </div>
          </div>

          <div>
            <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Ngày thực thi đầu tiên</label>
            <input 
              v-model="form.next_run_date" 
              type="datetime-local" 
              required
              class="w-full mt-1 glass-input text-xs font-mono"
            />
          </div>

          <div>
            <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Mô tả ngắn</label>
            <input 
              v-model="form.description" 
              type="text" 
              placeholder="Ví dụ: Đăng ký dịch vụ Netflix"
              class="w-full mt-1 glass-input"
            />
          </div>

          <button 
            type="submit" 
            :disabled="adding"
            class="w-full btn-primary mt-2"
          >
            <Loader2 v-if="adding" class="w-4 h-4 animate-spin" />
            <span>Kích hoạt lịch tự động</span>
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
import { useRecurringStore } from '../stores/recurring';
import { useNotificationStore } from '../stores/notification';
import LoadingSpinner from '../components/LoadingSpinner.vue';
import { formatCurrency, formatOriginalAmount, formatDate } from '../utils/format';
import { useAmountInput } from '../composables/useAmountInput';
import { categories, getCategoryClass } from '../utils/categories';
import { Plus, Trash2, X, CalendarClock, ArrowDownRight, ArrowUpRight, Loader2 } from 'lucide-vue-next';

const router = useRouter();
const authStore = useAuthStore();
const recurringStore = useRecurringStore();
const notificationStore = useNotificationStore();

const showAddModal = ref(false);
const adding = ref(false);

const form = reactive({
  amount: null,
  type: 'expense',
  category: 'Ăn uống',
  currency: 'VND',
  frequency: 'monthly',
  next_run_date: '',
  description: '',
});

const availableCategories = computed(() => {
  return categories[form.type];
});

watch(() => form.type, (newType) => {
  form.category = categories[newType][0];
});

const setNextRunDefaultDate = () => {
  const now = new Date();
  const offset = now.getTimezoneOffset() * 60000;
  const localISOTime = (new Date(now - offset)).toISOString().slice(0, 16);
  form.next_run_date = localISOTime;
};

onMounted(async () => {
  await recurringStore.fetchRecurrings();
  const userBase = authStore.user?.currency || 'VND';
  form.currency = userBase;
  setNextRunDefaultDate();
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
  deleteRec(id);
};

const promptLogin = async () => {
  await notificationStore.showAlert('Vui lòng đăng nhập để thực hiện tính năng này!', 'Yêu cầu Đăng nhập');
  router.push('/login');
};

const deleteRec = async (id) => {
  const confirmResult = await notificationStore.showConfirm('Bạn có chắc muốn hủy lịch giao dịch tự động này?', 'Xác nhận xóa');
  if (confirmResult) {
    await recurringStore.deleteRecurring(id);
  }
};

const submitAdd = async () => {
  adding.value = true;
  try {
    const formattedDate = new Date(form.next_run_date).toISOString();
    await recurringStore.addRecurring({
      amount: form.amount,
      type: form.type,
      category: form.category,
      currency: form.currency,
      frequency: form.frequency,
      next_run_date: formattedDate,
      description: form.description || null
    });
    
    form.amount = null;
    form.description = '';
    setNextRunDefaultDate();
    showAddModal.value = false;
  } catch (err) {
    notificationStore.showAlert(err.response?.data?.detail || 'Thao tác lỗi', 'Lỗi');
  } finally {
    adding.value = false;
  }
};

const formatFrequency = (freq) => {
  const dictionary = {
    daily: 'Hàng ngày',
    weekly: 'Hàng tuần',
    monthly: 'Hàng tháng'
  };
  return dictionary[freq] || freq;
};

const { amountInputStr, onAmountInput } = useAmountInput(form, 'amount');

</script>
