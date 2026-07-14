<template>
  <div v-if="transactionStore.loading && !transactionStore.summary" class="min-h-[70vh] flex items-center justify-center">
    <LoadingSpinner text="Generating" />
  </div>

  <div v-else class="space-y-6">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Tổng quan Tài chính</h1>
        <p class="text-slate-500 text-xs mt-0.5 flex items-center gap-1 flex-wrap">
          <span>Chào mừng trở lại,</span>
          <span class="font-bold text-slate-800 inline-flex items-center gap-0.5">
            {{ authStore.user?.fullname || 'Bạn' }}
            <Crown v-if="unlockedGoldenBadge" class="w-3.5 h-3.5 text-amber-500 shrink-0 inline-block align-text-bottom" />
          </span>
        </p>
      </div>
      <div class="flex items-center justify-center md:justify-end gap-3 w-full md:w-auto">
        <button 
          v-if="!authStore.isGuest"
          @click="transactionStore.downloadCSV()"
          class="btn-secondary flex items-center gap-2"
        >
          <Download class="w-4 h-4" />
          <span>Xuất Báo Cáo CSV</span>
        </button>
        <button 
          v-else
          @click="promptLogin"
          class="btn-secondary flex items-center gap-2 cursor-pointer"
        >
          <Download class="w-4 h-4" />
          <span>Xuất Báo Cáo CSV</span>
        </button>

        <button 
          @click="handleQuickAddClick"
          class="btn-primary flex items-center gap-2 cursor-pointer"
        >
          <Plus class="w-4 h-4" />
          <span>Giao dịch mới</span>
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="glass-panel glass-card-blue p-5 rounded-sm relative overflow-hidden flex flex-col justify-between h-[130px] bg-white">
        <div class="flex justify-between items-start">
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Số dư khả dụng</span>
          <div class="p-1.5 rounded-sm bg-purple-50 text-[#8000ff] border border-purple-100">
            <Wallet class="w-4.5 h-4.5" />
          </div>
        </div>
        <div>
          <div class="text-2xl font-black text-slate-900 tracking-wide font-mono">
            {{ formatCurrency(transactionStore.summary?.balance || 0) }}
          </div>
          <p class="text-[9px] text-slate-400 mt-1 uppercase font-semibold tracking-wider">Đơn vị: {{ authStore.user?.currency }}</p>
        </div>
      </div>

      <div class="glass-panel glass-card-green p-5 rounded-sm relative overflow-hidden flex flex-col justify-between h-[130px] bg-white">
        <div class="flex justify-between items-start">
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Tổng thu nhập tháng</span>
          <div class="p-1.5 rounded-sm bg-emerald-50 text-emerald-600 border border-emerald-100">
            <ArrowUpRight class="w-4.5 h-4.5" />
          </div>
        </div>
        <div>
          <div class="text-2xl font-black text-emerald-600 tracking-wide font-mono">
            +{{ formatCurrency(transactionStore.summary?.total_income || 0) }}
          </div>
          <p class="text-[9px] text-slate-400 mt-1 uppercase font-semibold tracking-wider">Các nguồn thu hợp lệ</p>
        </div>
      </div>

      <div class="glass-panel glass-card-red p-5 rounded-sm relative overflow-hidden flex flex-col justify-between h-[130px] bg-white">
        <div class="flex justify-between items-start">
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Tổng chi tiêu tháng</span>
          <div class="p-1.5 rounded-sm bg-red-50 text-red-650 border border-red-100">
            <ArrowDownRight class="w-4.5 h-4.5" />
          </div>
        </div>
        <div>
          <div class="text-2xl font-black text-red-650 tracking-wide font-mono">
            -{{ formatCurrency(transactionStore.summary?.total_expense || 0) }}
          </div>
          <p class="text-[9px] text-slate-400 mt-1 uppercase font-semibold tracking-wider">Ngân sách khả dụng bị trừ</p>
        </div>
      </div>
    </div>


    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <div class="glass-panel p-5 rounded-sm lg:col-span-5 flex flex-col justify-between min-h-[320px] bg-white">
        <h2 class="font-bold text-sm text-slate-800 uppercase tracking-wider mb-4">Chi tiêu theo Danh mục</h2>
        <div v-if="hasExpenseData" class="flex-1 flex items-center justify-center">
          <apexchart 
            type="donut" 
            width="100%" 
            :options="pieChartOptions" 
            :series="pieChartSeries"
          ></apexchart>
        </div>
        <div v-else class="flex-1 flex flex-col items-center justify-center text-slate-400">
          <PieChart class="w-10 h-10 stroke-[1.2] mb-2 text-slate-350" />
          <span class="text-xs">Chương có dữ liệu chi tiêu trong tháng này</span>
        </div>
      </div>

      <div class="glass-panel p-5 rounded-sm lg:col-span-7 flex flex-col min-h-[320px] bg-white">
        <div class="flex justify-between items-center mb-4">
          <h2 class="font-bold text-sm text-slate-800 uppercase tracking-wider">Giao dịch gần đây</h2>
          <router-link to="/transactions" class="text-xs text-[#8000ff] hover:text-purple-750 font-bold flex items-center gap-0.5">
            <span>Xem tất cả</span>
            <span class="text-[9px] font-sans">→</span>
          </router-link>
        </div>
        
        <div v-if="recentTransactions.length > 0" class="hidden sm:block flex-1 overflow-x-auto">
          <table class="w-full text-center border-collapse text-xs">
            <thead>
              <tr class="text-slate-400 border-b border-slate-200 uppercase text-[9px] tracking-wider font-bold">
                <th class="py-2.5 px-4 border-r border-slate-200/60 text-center">Ngày</th>
                <th class="py-2.5 px-4 border-r border-slate-200/60 text-center">Danh mục</th>
                <th class="py-2.5 px-4 border-r border-slate-200/60 text-center">Mô tả</th>
                <th class="py-2.5 px-4 text-center">Số tiền</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="tx in recentTransactions" 
                :key="tx.id"
                class="border-b border-slate-100 hover:bg-slate-50 transition"
              >
                <td class="py-2.5 px-4 border-r border-slate-100 text-slate-550 text-center font-mono">{{ formatDate(tx.date) }}</td>
                <td class="py-2.5 px-4 border-r border-slate-100 text-center">
                  <span class="px-2 py-0.5 rounded-sm text-[9px] font-bold uppercase tracking-wider" :class="getCategoryClass(tx.category)">
                    {{ tx.category }}
                  </span>
                </td>
                <td class="py-2.5 px-4 border-r border-slate-100 text-slate-700 font-medium truncate max-w-[150px] text-center">{{ tx.description || '-' }}</td>
                <td class="py-2.5 px-4 font-bold text-center font-mono" :class="tx.type === 'income' ? 'text-emerald-600' : 'text-red-655'">
                  {{ tx.type === 'income' ? '+' : '-' }}{{ formatOriginalAmount(tx.amount, tx.currency) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="recentTransactions.length > 0" class="block sm:hidden space-y-2.5 flex-1">
          <div 
            v-for="tx in recentTransactions" 
            :key="tx.id"
            class="bg-slate-50/50 border border-slate-100 rounded-xl p-3 flex flex-col space-y-2"
          >
            <div class="flex justify-between items-center">
              <span class="px-2.5 py-0.5 rounded-full text-[8px] font-black uppercase tracking-wider" :class="getCategoryClass(tx.category)">
                {{ tx.category }}
              </span>
              <span class="text-[9px] text-slate-400 font-bold font-mono">{{ formatDate(tx.date) }}</span>
            </div>
            <div class="text-[11px] font-bold text-slate-800 break-words leading-normal">
              {{ tx.description || 'Không có mô tả' }}
            </div>
            <div class="flex justify-between items-center border-t border-slate-100/50 pt-1.5 mt-0.5">
              <span class="text-[8px] text-slate-400 font-bold uppercase tracking-wider">Số tiền</span>
              <span class="text-[11px] font-mono font-extrabold" :class="tx.type === 'income' ? 'text-emerald-600' : 'text-red-655'">
                {{ tx.type === 'income' ? '+' : '-' }}{{ formatOriginalAmount(tx.amount, tx.currency) }}
              </span>
            </div>
          </div>
        </div>
        
        <div v-else class="flex-1 flex flex-col items-center justify-center text-slate-400">
          <History class="w-10 h-10 stroke-[1.2] mb-2 text-slate-350" />
          <span class="text-xs">Chưa ghi nhận giao dịch nào</span>
        </div>
      </div>
    </div>

    <div class="glass-panel p-5 rounded-sm bg-white mt-6">
      <div class="flex justify-between items-center flex-wrap gap-2 mb-4 border-b border-slate-100 pb-3">
        <div class="flex items-center gap-2">
          <CalendarClock class="w-4.5 h-4.5" :class="activeTheme === 'gold' ? 'text-amber-500' : 'text-[#8000ff]'" />
          <h2 class="font-bold text-sm text-slate-800 uppercase tracking-wider">Thử thách & Thói quen Tài chính Hàng ngày</h2>
        </div>
        <div v-if="unlockedGoldenTheme" class="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-full px-2.5 py-1">
          <span class="text-[10px] font-bold text-slate-500">Chủ đề:</span>
          <button 
            @click="toggleTheme" 
            class="text-[10px] font-black cursor-pointer uppercase transition tracking-wider hover:opacity-85"
            :class="activeTheme === 'gold' ? 'text-amber-500' : 'text-[#8000ff]'"
          >
            {{ activeTheme === 'gold' ? 'Hoàng Kim' : 'Nebula Purple' }}
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-12 gap-4 items-center bg-slate-50/70 border border-slate-200/50 rounded-xl p-4 mb-4 select-none">
        <div class="md:col-span-4 space-y-1">
          <div class="flex items-center gap-2.5">
            <Trophy class="w-5 h-5 text-amber-500 shrink-0" />
            <div>
              <div class="text-[10px] font-black text-slate-400 uppercase tracking-wider">Danh hiệu thói quen</div>
              <div class="text-xs font-bold text-slate-850">{{ levelInfo.title }}</div>
            </div>
          </div>
        </div>

        <div class="md:col-span-5 space-y-1">
          <div class="flex justify-between text-[10px] font-bold text-slate-500">
            <span>{{ totalHabitPoints }} Điểm</span>
            <span>Cần {{ levelInfo.max }} để lên cấp</span>
          </div>
          <div class="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
            <div 
              class="h-full transition-all duration-500 ease-out"
              :class="activeTheme === 'gold' ? 'bg-gradient-to-r from-amber-400 to-yellow-500' : 'bg-gradient-to-r from-[#8000ff] to-[#b772ff]'"
              :style="{ width: `${levelInfo.progress}%` }"
            ></div>
          </div>
        </div>

        <div class="md:col-span-3 flex justify-end">
          <button 
            @click="showRewards = !showRewards"
            class="w-full md:w-auto text-xs font-bold px-3 py-1.5 rounded-full border flex items-center justify-center gap-1.5 transition cursor-pointer select-none"
            :class="showRewards 
              ? 'bg-slate-800 border-slate-800 text-white' 
              : 'bg-white border-slate-200 text-slate-705 hover:border-slate-350 hover:bg-slate-50'"
          >
            <Gift class="w-3.5 h-3.5 text-amber-500" />
            <span>{{ showRewards ? 'Đóng cửa hàng' : 'Cửa hàng phần thưởng' }}</span>
          </button>
        </div>
      </div>

      <div v-if="showRewards" class="bg-purple-50/20 border border-purple-100/40 rounded-xl p-4 mb-4 space-y-3">
        <div class="flex items-center gap-1.5">
          <Gift class="w-4 h-4 text-amber-500" />
          <h4 class="text-[10px] font-black text-[#8000ff] uppercase tracking-wider">Cửa hàng phần thưởng Aura Rewards</h4>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div 
            v-for="reward in rewardsList" 
            :key="reward.id"
            class="bg-white border border-slate-150 p-3 rounded-lg flex flex-col justify-between space-y-3 shadow-sm hover:shadow-md transition"
          >
            <div class="space-y-1 select-none">
              <span class="text-xs font-bold text-slate-800">{{ reward.name }}</span>
              <p class="text-[10px] text-slate-500 leading-normal">{{ reward.description }}</p>
            </div>
            
            <div class="flex justify-between items-center pt-2 border-t border-slate-50 select-none">
              <span class="text-[10px] font-bold text-slate-450 uppercase tracking-wider">{{ reward.cost }} Điểm</span>
              
              <button 
                @click="purchaseReward(reward)"
                class="text-[10px] font-bold px-2.5 py-1 rounded-full cursor-pointer select-none transition"
                :class="(reward.id === 'golden_badge' && unlockedGoldenBadge) || (reward.id === 'golden_theme' && unlockedGoldenTheme)
                  ? 'bg-slate-100 text-slate-450 cursor-not-allowed'
                  : 'bg-[#8000ff] hover:bg-[#6c00d9] text-white active:scale-95'"
                :disabled="(reward.id === 'golden_badge' && unlockedGoldenBadge) || (reward.id === 'golden_theme' && unlockedGoldenTheme)"
              >
                <span v-if="reward.id === 'golden_badge' && unlockedGoldenBadge">Đã sở hữu</span>
                <span v-else-if="reward.id === 'golden_theme' && unlockedGoldenTheme">Đã sở hữu</span>
                <span v-else>Đổi Quà</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div 
          v-for="(habit, idx) in financialHabits" 
          :key="idx"
          class="flex items-center gap-3.5 p-3 rounded-lg border border-slate-100 bg-slate-50/50 hover:bg-slate-50 transition"
        >
          <label class="lock-checkbox-container shrink-0">
            <input 
              type="checkbox" 
              v-model="habit.completed" 
              @change="onHabitChange(habit)"
            >
            <div class="lock-checkbox-checkmark"></div>
          </label>
          <div class="flex-1 min-w-0">
            <p 
              class="text-xs font-bold leading-tight transition-all"
              :class="habit.completed ? 'line-through text-slate-450' : 'text-slate-700'"
            >
              {{ habit.title }}
            </p>
            <p class="text-[9px] text-slate-450 mt-0.5 font-semibold uppercase tracking-wider">
              {{ habit.points }} điểm thói quen
            </p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showQuickAdd" class="fixed inset-0 bg-black/20 z-50 flex items-center justify-center p-4 select-none">
      <div class="w-full max-w-sm bg-white border border-slate-200 rounded-[30px] p-6 space-y-4 shadow-xl">
        <div class="flex justify-between items-center border-b border-slate-100 pb-2">
          <h3 class="font-bold text-sm text-slate-900 uppercase tracking-wider">Thêm giao dịch nhanh</h3>
          <button @click="showQuickAdd = false" class="p-1 rounded-sm text-slate-400 hover:text-slate-800 hover:bg-slate-100 transition cursor-pointer">
            <X class="w-4.5 h-4.5" />
          </button>
        </div>

        <form @submit.prevent="submitQuickAdd" class="space-y-3">
          <div class="grid grid-cols-2 gap-2 bg-slate-50 p-1 border border-slate-200 rounded-full">
            <button 
              type="button" 
              @click="quickForm.type = 'expense'"
              class="py-1.5 rounded-full font-bold text-xs cursor-pointer transition flex items-center justify-center gap-1"
              :class="quickForm.type === 'expense' ? 'bg-white text-red-655 shadow-sm border border-slate-200' : 'text-slate-500'"
            >
              <ArrowDownRight class="w-3.5 h-3.5" />
              <span>Chi tiêu</span>
            </button>
            <button 
              type="button" 
              @click="quickForm.type = 'income'"
              class="py-1.5 rounded-full font-bold text-xs cursor-pointer transition flex items-center justify-center gap-1"
              :class="quickForm.type === 'income' ? 'bg-white text-emerald-655 shadow-sm border border-slate-200' : 'text-slate-500'"
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
              <select v-model="quickForm.currency" class="w-full mt-1 glass-input text-xs bg-white cursor-pointer font-bold">
                <option value="VND">VND</option>
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
              </select>
            </div>
          </div>

          <div v-if="quickForm.currency !== authStore.user?.currency" class="text-[11px] text-purple-700 bg-purple-50/50 p-2 rounded-full border border-purple-100 flex justify-between items-center gap-1">
            <span>Tỷ giá quy đổi:</span>
            <input 
              v-model.number="quickForm.exchange_rate" 
              type="number" 
              step="0.0001"
              class="inline-block w-16 px-1 py-0.5 bg-white rounded-full border border-slate-200 text-center font-bold font-mono text-xs"
            />
          </div>

          <div>
            <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Danh mục</label>
            <select v-model="quickForm.category" class="w-full mt-1 glass-input text-xs bg-white cursor-pointer font-bold">
              <option v-for="cat in availableCategories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>

          <div>
            <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Mô tả chi tiết</label>
            <input 
              v-model="quickForm.description" 
              type="text" 
              placeholder="Ví dụ: Ăn trưa tại quán"
              class="w-full mt-1 glass-input"
            />
          </div>

          <button 
            type="submit" 
            :disabled="quickAdding"
            class="w-full btn-primary mt-2"
          >
            <Loader2 v-if="quickAdding" class="w-4 h-4 animate-spin" />
            <span>Thêm giao dịch</span>
          </button>
        </form>
      </div>
    </div>

    <div v-if="showComplimentModal" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4 select-none">
      <div class="w-full max-w-sm bg-white border border-slate-250 rounded-[30px] p-6 space-y-4 shadow-xl text-center flex flex-col items-center animate-in fade-in zoom-in duration-300">
        <div class="w-14 h-14 rounded-full bg-purple-50 flex items-center justify-center border border-purple-100 text-[#8000ff] mb-2 animate-bounce">
          <Sparkles class="w-7 h-7 text-[#8000ff]" />
        </div>
        <h3 class="font-bold text-sm text-slate-950 uppercase tracking-wider">Aura AI Tán Dương</h3>
        <p class="text-xs text-slate-600 leading-relaxed font-bold px-2">
          {{ aiComplimentText }}
        </p>
        <button 
          @click="showComplimentModal = false"
          class="btn-primary w-full text-xs font-bold py-2 mt-2 cursor-pointer"
        >
          Tuyệt vời
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useTransactionStore } from '../stores/transaction';
import { useNotificationStore } from '../stores/notification';
import LoadingSpinner from '../components/LoadingSpinner.vue';
import { 
  Download, Plus, Wallet, ArrowUpRight, ArrowDownRight, 
  Sparkles, PieChart, History, X, Loader2, CalendarClock,
  Trophy, Gift, Crown
} from 'lucide-vue-next';
import { formatCurrency, formatOriginalAmount, formatDate } from '../utils/format';
import { useAmountInput } from '../composables/useAmountInput';
import { categories, getCategoryClass } from '../utils/categories';
import { defaultExchangeRates } from '../utils/constants';
import apexchart from 'vue3-apexcharts';

const router = useRouter();
const authStore = useAuthStore();
const transactionStore = useTransactionStore();
const notificationStore = useNotificationStore();

const showQuickAdd = ref(false);
const quickAdding = ref(false);

const quickForm = reactive({
  amount: null,
  type: 'expense',
  category: 'Ăn uống',
  currency: 'VND',
  exchange_rate: 1.0,
  description: '',
});

watch(() => [quickForm.currency, authStore.user?.currency], () => {
  const userBase = authStore.user?.currency || 'VND';
  const inputCurr = quickForm.currency;
  
  if (defaultExchangeRates[inputCurr] && defaultExchangeRates[inputCurr][userBase]) {
    quickForm.exchange_rate = defaultExchangeRates[inputCurr][userBase];
  } else {
    quickForm.exchange_rate = 1.0;
  }
});

const availableCategories = computed(() => {
  return categories[quickForm.type];
});

watch(() => quickForm.type, (newType) => {
  quickForm.category = categories[newType][0];
});

const habitsPool = [
  // 💰 Tài chính & Tiết kiệm
  { id: 1, title: 'Ghi chép đầy đủ chi tiêu phát sinh trong ngày', points: 10 },
  { id: 2, title: 'Kiểm tra hạn mức ngân sách trước khi mua sắm', points: 15 },
  { id: 3, title: 'Tiết kiệm tối thiểu 50.000đ ngày hôm nay', points: 20 },
  { id: 4, title: 'Không mua đồ ăn nhanh hoặc trà sữa ngoài kế hoạch', points: 15 },
  { id: 5, title: 'Đọc và kiểm tra lịch trình giao dịch định kỳ', points: 10 },
  { id: 6, title: 'Xem báo cáo chi tiêu tháng trên ví AuraFinance', points: 10 },
  { id: 7, title: 'Từ chối một khoản mua sắm bốc đồng hôm nay', points: 20 },
  { id: 8, title: 'Tìm hiểu kiến thức về một kênh đầu tư an toàn', points: 15 },
  { id: 9, title: 'Kiểm tra số dư tài khoản ngân hàng và các ví', points: 10 },
  { id: 10, title: 'Không sử dụng thẻ tín dụng cho chi tiêu không thiết yếu', points: 15 },
  { id: 11, title: 'Trích tối thiểu 10% thu nhập hôm nay vào quỹ dự phòng', points: 20 },
  { id: 12, title: 'Tìm kiếm mã giảm giá hoặc ưu đãi trước khi thanh toán', points: 10 },
  { id: 13, title: 'Hủy các gói đăng ký dịch vụ tự gia hạn không dùng', points: 15 },
  { id: 14, title: 'Thực hiện quy tắc 24 giờ trước khi mua đồ đắt tiền', points: 15 },
  { id: 15, title: 'Phân chia thu nhập theo phương pháp 6 cái hũ hôm nay', points: 15 },
  { id: 16, title: 'Thiết lập khoản tiết kiệm tự động nhỏ trực tuyến', points: 20 },
  { id: 17, title: 'Lên danh sách đồ cần mua trước khi đi siêu thị', points: 10 },
  { id: 18, title: 'So sánh giá của một món đồ ở ít nhất 3 nơi khác nhau', points: 10 },
  { id: 19, title: 'Lập danh sách các khoản nợ và ưu tiên trả từng khoản', points: 15 },
  { id: 20, title: 'Gom đồ cũ không dùng để thanh lý hoặc quyên góp', points: 15 },
  { id: 21, title: 'Xem lại hạn mức chi tiêu tháng xem có bị vượt không', points: 10 },
  { id: 22, title: 'Đặt mục tiêu tài chính cụ thể và đo lường được cho tuần tới', points: 10 },
  { id: 23, title: 'Viết ra 3 điều rút ra từ sai lầm tài chính trong quá khứ', points: 15 },
  { id: 24, title: 'Kiểm tra thời hạn các chương trình điểm thưởng thành viên', points: 10 },
  { id: 25, title: 'Tìm hiểu và mở một loại tài khoản tiết kiệm lãi suất cao', points: 20 },
  { id: 26, title: 'Không tiêu tiền vào bất kỳ thứ gì không cần thiết hôm nay', points: 25 },
  { id: 27, title: 'Trao đổi với gia đình về kế hoạch chi tiêu trong tuần', points: 10 },
  { id: 28, title: 'Hạn chế lướt các ứng dụng mua sắm trực tuyến dưới 10 phút', points: 15 },
  { id: 29, title: 'Cập nhật hóa đơn điện nước internet vào ứng dụng', points: 10 },
  { id: 30, title: 'Mua nhu yếu phẩm theo số lượng lớn để tối ưu giá thành', points: 15 },
  // 🏃 Thể dục & Thể thao
  { id: 31, title: 'Đi bộ ít nhất 8.000 bước chân trong ngày', points: 20 },
  { id: 32, title: 'Tập cardio hoặc chạy bộ ít nhất 20 phút', points: 25 },
  { id: 33, title: 'Thực hiện 30 cái hít đất hoặc bài tập cơ thể', points: 20 },
  { id: 34, title: 'Tập yoga hoặc thiền định ít nhất 15 phút', points: 15 },
  { id: 35, title: 'Đi xe đạp hoặc đi bộ đến điểm đến thay vì xe máy', points: 15 },
  { id: 36, title: 'Thực hiện bài kéo giãn cơ toàn thân vào buổi sáng', points: 10 },
  { id: 37, title: 'Tập gym hoặc tập luyện cùng nhóm bạn ít nhất 45 phút', points: 25 },
  { id: 38, title: 'Không dùng thang máy, leo cầu thang bộ cả ngày', points: 15 },
  { id: 39, title: 'Tập 50 cái squat hoặc các bài tập chân trong ngày', points: 20 },
  { id: 40, title: 'Bơi lội hoặc các môn thể thao dưới nước ít nhất 30 phút', points: 25 },
  { id: 41, title: 'Chơi một môn thể thao yêu thích ít nhất 30 phút', points: 20 },
  { id: 42, title: 'Tập plank ít nhất 3 hiệp, mỗi hiệp 1 phút', points: 15 },
  { id: 43, title: 'Làm 100 cái nhảy dây hoặc jumping jack trong ngày', points: 15 },
  { id: 44, title: 'Đặt lịch tập thể dục định kỳ vào lịch tuần tới', points: 10 },
  { id: 45, title: 'Nhờ bạn bè hoặc đồng nghiệp cùng đi tập thể dục', points: 10 },
  // 🥗 Dinh dưỡng & Ăn uống lành mạnh
  { id: 46, title: 'Uống đủ 2 lít nước trong ngày, không uống nước ngọt', points: 15 },
  { id: 47, title: 'Tự nấu ăn tại nhà thay vì đi ăn tiệm hoặc đặt ship', points: 15 },
  { id: 48, title: 'Ăn ít nhất 5 loại rau củ hoặc trái cây khác nhau hôm nay', points: 20 },
  { id: 49, title: 'Không ăn đồ chiên rán hoặc thức ăn nhiều dầu mỡ hôm nay', points: 15 },
  { id: 50, title: 'Ăn sáng đầy đủ và đúng giờ thay vì bỏ bữa', points: 15 },
  { id: 51, title: 'Không uống cà phê tiệm, tự pha cà phê hoặc trà tại nhà', points: 15 },
  { id: 52, title: 'Chuẩn bị hộp cơm mang theo thay vì mua ăn ngoài', points: 20 },
  { id: 53, title: 'Không ăn vặt sau 8 giờ tối hôm nay', points: 15 },
  { id: 54, title: 'Thay thế một bữa ăn bằng salad rau củ hoặc trái cây', points: 15 },
  { id: 55, title: 'Giảm lượng muối và đường trong bữa ăn hôm nay', points: 10 },
  { id: 56, title: 'Uống một ly sinh tố rau củ hoặc nước ép trái cây tươi', points: 10 },
  { id: 57, title: 'Ăn chậm nhai kỹ, dành ít nhất 20 phút cho mỗi bữa', points: 10 },
  { id: 58, title: 'Không uống bia rượu hoặc đồ có cồn trong ngày hôm nay', points: 20 },
  { id: 59, title: 'Thêm protein vào bữa ăn: trứng, thịt gà, đậu hũ, cá', points: 10 },
  { id: 60, title: 'Nấu ăn theo công thức lành mạnh mới lạ chưa từng thử', points: 15 },
  // 🧠 Sức khỏe tinh thần & Tâm lý
  { id: 61, title: 'Thiền định ít nhất 10 phút vào buổi sáng sớm', points: 15 },
  { id: 62, title: 'Ghi nhận một điều bạn cảm thấy biết ơn trong ngày', points: 10 },
  { id: 63, title: 'Dành 15 phút viết nhật ký hoặc ghi chú suy nghĩ cá nhân', points: 10 },
  { id: 64, title: 'Ngủ đủ giấc từ 7-8 tiếng, không thức khuya quá 23h', points: 20 },
  { id: 65, title: 'Dành thời gian trò chuyện với người thân hoặc bạn bè', points: 10 },
  { id: 66, title: 'Không sử dụng điện thoại trong 1 tiếng trước khi ngủ', points: 15 },
  { id: 67, title: 'Thực hành hít thở sâu 4-7-8 khi căng thẳng hoặc lo lắng', points: 10 },
  { id: 68, title: 'Nghỉ ngơi 5-10 phút sau mỗi 50 phút làm việc liên tục', points: 10 },
  { id: 69, title: 'Xem một bộ phim hoặc đọc sách để thư giãn tâm trí', points: 10 },
  { id: 70, title: 'Tắt thông báo điện thoại trong 2 tiếng để tập trung', points: 15 },
  { id: 71, title: 'Tránh xa tin tức tiêu cực và mạng xã hội trước bữa sáng', points: 10 },
  { id: 72, title: 'Tham gia một buổi sinh hoạt cộng đồng hoặc câu lạc bộ', points: 15 },
  { id: 73, title: 'Viết ra 3 điều tích cực về bản thân và thành tích hôm nay', points: 10 },
  { id: 74, title: 'Thực hành nụ cười, chào hỏi và lời cảm ơn chân thành', points: 10 },
  { id: 75, title: 'Nghe podcast hoặc âm thanh thư giãn trước khi ngủ', points: 10 },
  // 📚 Học tập & Phát triển bản thân
  { id: 76, title: 'Đọc ít nhất 10 trang sách về tài chính hoặc phát triển bản thân', points: 15 },
  { id: 77, title: 'Học một từ mới hoặc khái niệm tài chính chưa biết', points: 10 },
  { id: 78, title: 'Xem một video bài học kỹ năng mới trên YouTube/Coursera', points: 15 },
  { id: 79, title: 'Hoàn thành một bài tập hoặc khóa học online đang dang dở', points: 20 },
  { id: 80, title: 'Luyện tập ngoại ngữ ít nhất 15 phút hôm nay', points: 15 },
  { id: 81, title: 'Viết một tóm tắt về điều đã học được trong ngày', points: 10 },
  { id: 82, title: 'Tham gia một hội thảo, webinar hoặc khóa đào tạo online', points: 20 },
  { id: 83, title: 'Cải thiện một kỹ năng nghề nghiệp trong 30 phút', points: 15 },
  { id: 84, title: 'Tìm hiểu cách hoạt động của thị trường chứng khoán', points: 15 },
  { id: 85, title: 'Chia sẻ kiến thức hoặc mẹo hay với người khác', points: 10 },
  // ⚡ Năng suất & Tổ chức
  { id: 86, title: 'Lập danh sách việc cần làm (to-do list) cho ngày hôm nay', points: 10 },
  { id: 87, title: 'Hoàn thành task quan trọng nhất trước 10 giờ sáng', points: 20 },
  { id: 88, title: 'Dọn dẹp và sắp xếp gọn gàng bàn làm việc hoặc phòng', points: 10 },
  { id: 89, title: 'Không trễ bất kỳ cuộc hẹn hoặc deadline nào hôm nay', points: 15 },
  { id: 90, title: 'Lên lịch và chuẩn bị kế hoạch chi tiết cho cả tuần tới', points: 15 },
  { id: 91, title: 'Trả lời tất cả email quan trọng còn tồn đọng', points: 10 },
  { id: 92, title: 'Sắp xếp và phân loại tài liệu điện tử trên máy tính', points: 10 },
  { id: 93, title: 'Hoàn thành một dự án nhỏ hoặc đề xuất cải tiến công việc', points: 20 },
  { id: 94, title: 'Dành 25 phút tập trung hoàn toàn theo kỹ thuật Pomodoro', points: 10 },
  { id: 95, title: 'Xem lại và đánh giá hiệu suất làm việc tuần này', points: 15 },
  // 🌿 Môi trường & Lối sống xanh
  { id: 96, title: 'Hạn chế túi nilon, tự mang túi vải khi đi chợ hoặc siêu thị', points: 10 },
  { id: 97, title: 'Tắt đèn và thiết bị điện không sử dụng để tiết kiệm điện', points: 10 },
  { id: 98, title: 'Phân loại rác thải đúng quy định tại nhà', points: 10 },
  { id: 99, title: 'Tự rửa xe máy tại nhà thay vì mang ra tiệm', points: 15 },
  { id: 100, title: 'Trồng hoặc chăm sóc một cây xanh tại nhà hoặc văn phòng', points: 15 },
  { id: 101, title: 'Sử dụng chai nước cá nhân thay vì mua nước đóng chai nhựa', points: 10 },
  { id: 102, title: 'Tìm hiểu một mẹo tái chế đồ dùng để tiết kiệm', points: 10 },
  { id: 103, title: 'Giảm thời gian tắm xuống còn 5 phút để tiết kiệm nước', points: 10 },
  { id: 104, title: 'Không sử dụng ống hút nhựa dùng một lần hôm nay', points: 10 },
  { id: 105, title: 'Đi đổ rác và dọn dẹp khu vực xung quanh nhà', points: 15 },
  // 👨‍👩‍👧 Gia đình & Quan hệ xã hội
  { id: 106, title: 'Gọi điện hoặc nhắn tin hỏi thăm cha mẹ hoặc người thân', points: 10 },
  { id: 107, title: 'Nấu một bữa ăn đặc biệt cho gia đình hoặc người thân yêu', points: 20 },
  { id: 108, title: 'Giúp đỡ một người trong cộng đồng một việc tốt hôm nay', points: 15 },
  { id: 109, title: 'Dành ít nhất 1 tiếng chất lượng chơi cùng con hoặc gia đình', points: 20 },
  { id: 110, title: 'Viết thư tay hoặc tin nhắn cảm ơn ai đó đã giúp bạn', points: 10 },
  { id: 111, title: 'Không cãi vã hay nói tiêu cực về bất kỳ ai trong ngày', points: 15 },
  { id: 112, title: 'Tình nguyện tham gia một hoạt động từ thiện hoặc cộng đồng', points: 20 },
  { id: 113, title: 'Chia sẻ một bữa ăn hoặc tặng thức ăn cho người cần hơn', points: 15 },
  // 🩺 Sức khỏe & Phòng bệnh
  { id: 114, title: 'Rửa tay đúng cách ít nhất 5 lần trong ngày', points: 10 },
  { id: 115, title: 'Kiểm tra sức khỏe định kỳ hoặc đặt lịch khám bác sĩ', points: 20 },
  { id: 116, title: 'Đánh răng và súc miệng đúng cách 2 lần trong ngày', points: 10 },
  { id: 117, title: 'Dùng kem chống nắng khi ra ngoài trời để bảo vệ da', points: 10 },
  { id: 118, title: 'Thực hiện bài tập mắt 20-20-20 khi nhìn màn hình lâu', points: 10 },
  { id: 119, title: 'Uống thuốc bổ hoặc vitamin theo chỉ định đúng giờ', points: 10 },
  { id: 120, title: 'Không hút thuốc lá hoặc khuyên ai đó bỏ thuốc hôm nay', points: 20 },
];

const rewardsList = [
  // 🌟 Phần thưởng xã hội & AI
  { id: 'ai_compliment', name: 'Lời khen từ AI', description: 'Aura AI sẽ lập tức tán dương và động viên kỷ luật của bạn.', cost: 15 },
  { id: 'golden_badge', name: '👑 Danh hiệu Hoàng Kim', description: 'Mở khóa vương miện kế bên tên bạn tại trang tổng quan.', cost: 80 },
  { id: 'golden_theme', name: '✨ Chủ đề Màu Hoàng Kim', description: 'Đổi giao diện điểm số & thanh tiến trình sang màu vàng lấp lánh.', cost: 50 },
  // 🏋️ Thể dục & Sức khỏe
  { id: 's_gym_day', name: '🏋️ Ngày Gym Tự Thưởng', description: 'Thưởng cho bản thân một buổi tập gym đỉnh cao không áy náy.', cost: 30 },
  { id: 's_yoga_class', name: '🧘 1 Buổi Yoga Thư Giãn', description: 'Đặt lịch tham gia 1 buổi yoga yêu thích không giới hạn.', cost: 25 },
  { id: 's_swim', name: '🏊 Vé Bể Bơi', description: 'Đổi điểm để tự thưởng một buổi bơi lội thư giãn.', cost: 20 },
  { id: 's_massage', name: '💆 Voucher Massage Thư Giãn', description: 'Tự thưởng một buổi massage thư giãn toàn thân.', cost: 60 },
  { id: 's_spa', name: '🛁 Trải Nghiệm Spa 1 Giờ', description: 'Một giờ spa tuyệt vời để xả stress sau tuần bận rộn.', cost: 80 },
  { id: 's_bike', name: '🚴 Buổi Đạp Xe Dã Ngoại', description: 'Tự thưởng một chuyến đạp xe ngoài trời thư thái.', cost: 20 },
  { id: 's_run', name: '🏅 Huy Chương Chạy Bộ', description: 'Ghi danh tham gia một giải chạy bộ phong trào địa phương.', cost: 40 },
  { id: 's_badminton', name: '🏸 Sân Cầu Lông 2 Tiếng', description: 'Thuê sân cầu lông chơi cùng bạn bè không áy náy.', cost: 25 },
  { id: 's_hiking', name: '🥾 Chuyến Đi Trekking', description: 'Lên kế hoạch một chuyến trekking cuối tuần đến núi gần nhà.', cost: 50 },
  { id: 's_boxing', name: '🥊 Buổi Tập Võ Kickboxing', description: 'Tự thưởng một buổi tập kickboxing xả stress năng lượng.', cost: 30 },
  { id: 's_vitamin', name: '💊 Hộp Vitamin Tổng Hợp', description: 'Mua một hộp vitamin C hoặc tổng hợp cho sức khỏe tốt hơn.', cost: 35 },
  { id: 's_fitband', name: '⌚ Vòng Tay Theo Dõi Sức Khỏe', description: 'Tự thưởng một vòng tay thể thao đo nhịp tim bước chân.', cost: 120 },
  { id: 's_gym_month', name: '🎟️ 1 Tháng Thẻ Gym', description: 'Đổi điểm để mua thẻ gym 1 tháng tập luyện không giới hạn.', cost: 200 },
  { id: 's_tennis', name: '🎾 Sân Tennis Cuối Tuần', description: 'Thuê sân tennis 2 tiếng để thi đấu cùng người thân.', cost: 35 },
  { id: 's_football', name: '⚽ Sân Bóng Đá Mini', description: 'Đặt sân bóng đá 5 người vui chơi cùng nhóm bạn.', cost: 30 },
  // 🍽️ Ẩm thực & Dinh dưỡng
  { id: 'f_smoothie', name: '🥤 Ly Sinh Tố Sức Khỏe', description: 'Tự thưởng một ly sinh tố trái cây tươi bổ dưỡng.', cost: 10 },
  { id: 'f_salad', name: '🥗 Hộp Salad Rau Củ Cao Cấp', description: 'Đặt một hộp salad rau củ tươi ngon và lành mạnh.', cost: 15 },
  { id: 'f_sushi', name: '🍱 Bữa Sushi Thưởng Thức', description: 'Thưởng bản thân một bữa sushi không áy náy về chi phí.', cost: 45 },
  { id: 'f_bbq', name: '🥩 Buổi BBQ Cùng Bạn Bè', description: 'Tổ chức một buổi nướng BBQ nhỏ vui vẻ cùng bạn thân.', cost: 55 },
  { id: 'f_cake', name: '🎂 Bánh Kem Mừng Thành Tích', description: 'Mua một chiếc bánh kem nhỏ ăn mừng thói quen tốt.', cost: 20 },
  { id: 'f_coffee', name: '☕ Cà Phê Đặc Sản Cao Cấp', description: 'Tự thưởng một ly cà phê đặc sản từ quán yêu thích.', cost: 15 },
  { id: 'f_hotpot', name: '🍲 Buổi Lẩu Gia Đình', description: 'Tổ chức một bữa lẩu ngon miệng với gia đình hoặc bạn bè.', cost: 60 },
  { id: 'f_dessert', name: '🍮 Tráng Miệng Cao Cấp', description: 'Thưởng một phần tráng miệng đặc biệt tại nhà hàng.', cost: 20 },
  { id: 'f_icecream', name: '🍦 Kem Tươi Thứ Bảy', description: 'Tự thưởng một cây kem tươi mát lạnh cuối tuần.', cost: 10 },
  { id: 'f_pizza', name: '🍕 Pizza Gia Đình Cuối Tuần', description: 'Đặt một chiếc pizza size lớn cho cả gia đình thưởng thức.', cost: 40 },
  { id: 'f_bento', name: '🍱 Hộp Cơm Bento Nhật Bản', description: 'Thưởng một hộp cơm Bento Nhật chuẩn vị làm bữa trưa.', cost: 25 },
  { id: 'f_brunch', name: '🥞 Brunch Cao Cấp Cuối Tuần', description: 'Tự thưởng một bữa brunch đặc biệt với pancake và trứng benedict.', cost: 35 },
  { id: 'f_organic', name: '🌾 Giỏ Thực Phẩm Organic', description: 'Mua một giỏ rau củ quả organic sạch cho cả tuần.', cost: 45 },
  { id: 'f_steak', name: '🥩 Bữa Tối Steak Cao Cấp', description: 'Thưởng một phần steak ngon tại nhà hàng sau tuần làm việc tốt.', cost: 70 },
  { id: 'f_seafood', name: '🦞 Bữa Hải Sản Tươi Sống', description: 'Thưởng một bữa hải sản tươi sống ngon miệng bên bờ biển.', cost: 80 },
  { id: 'f_ramen', name: '🍜 Tô Ramen Chuẩn Vị Nhật', description: 'Thưởng một tô ramen nóng hổi chuẩn vị Nhật Bản.', cost: 20 },
  // 📚 Học tập & Phát triển
  { id: 'l_book', name: '📖 Một Cuốn Sách Hay', description: 'Mua một cuốn sách về tài chính hoặc phát triển bản thân.', cost: 30 },
  { id: 'l_ebook', name: '📱 E-book Premium', description: 'Mua một e-book cao cấp về chủ đề bạn quan tâm nhất.', cost: 20 },
  { id: 'l_course', name: '🎓 Khóa Học Online 1 Tháng', description: 'Đăng ký một khóa học kỹ năng mới trên Udemy hoặc Coursera.', cost: 100 },
  { id: 'l_podcast', name: '🎧 Gói Premium Podcast', description: 'Nâng cấp ứng dụng podcast yêu thích để nghe không quảng cáo.', cost: 25 },
  { id: 'l_audiobook', name: '🎙️ Audiobook Bestseller', description: 'Mua một cuốn sách nói bestseller nghe trên đường đi.', cost: 30 },
  { id: 'l_workshop', name: '🏫 Vé Workshop Kỹ Năng', description: 'Đăng ký tham dự một workshop kỹ năng mềm hoặc tài chính.', cost: 80 },
  { id: 'l_journal', name: '📔 Sổ Tay Ghi Chép Đẹp', description: 'Mua một cuốn sổ tay cao cấp để ghi chép mục tiêu và kế hoạch.', cost: 20 },
  { id: 'l_pen', name: '🖊️ Bút Ký Cao Cấp', description: 'Tự thưởng một cây bút ký đẹp để ký cam kết mục tiêu tài chính.', cost: 25 },
  { id: 'l_planner', name: '🗓️ Planner Năm Mới', description: 'Mua một quyển planner lập kế hoạch năm tài chính hiệu quả.', cost: 35 },
  { id: 'l_language', name: '🌏 1 Tháng App Học Ngoại Ngữ', description: 'Đăng ký gói premium Duolingo hoặc app ngoại ngữ yêu thích.', cost: 30 },
  { id: 'l_invest_book', name: '💹 Sách Đầu Tư Cổ Phiếu', description: 'Mua sách kinh điển về đầu tư như Nhà đầu tư thông minh.', cost: 35 },
  { id: 'l_finance_mag', name: '📰 Tạp Chí Kinh Tế 1 Năm', description: 'Đăng ký 1 năm tạp chí kinh tế tài chính uy tín.', cost: 60 },
  // 🎮 Giải trí & Thư giãn
  { id: 'e_movie', name: '🎬 Vé Xem Phim Rạp', description: 'Mua 2 vé rạp xem phim mới nhất cùng người thân yêu.', cost: 35 },
  { id: 'e_netflix', name: '📺 1 Tháng Netflix Premium', description: 'Đổi điểm để trả phí Netflix Premium xem phim thoải mái.', cost: 60 },
  { id: 'e_spotify', name: '🎵 1 Tháng Spotify Premium', description: 'Nghe nhạc không quảng cáo với Spotify Premium 1 tháng.', cost: 30 },
  { id: 'e_game', name: '🎮 Một Tựa Game Yêu Thích', description: 'Mua một tựa game mobile hoặc PC mà bạn đã muốn từ lâu.', cost: 50 },
  { id: 'e_concert', name: '🎤 Vé Xem Nhạc Sống', description: 'Đặt vé xem một buổi hòa nhạc hoặc show ca nhạc yêu thích.', cost: 100 },
  { id: 'e_museum', name: '🏛️ Vé Tham Quan Bảo Tàng', description: 'Khám phá một bảo tàng nghệ thuật hoặc lịch sử địa phương.', cost: 20 },
  { id: 'e_karaoke', name: '🎤 Phòng Karaoke Cuối Tuần', description: 'Đặt phòng karaoke hát thỏa thích 2 tiếng cùng bạn bè.', cost: 30 },
  { id: 'e_vr', name: '🥽 Trải Nghiệm VR Gaming', description: 'Thử trải nghiệm thực tế ảo VR tại trung tâm giải trí.', cost: 40 },
  { id: 'e_boardgame', name: '🎲 Đêm Board Game Vui Vẻ', description: 'Tổ chức hoặc tham gia một đêm board game cùng nhóm bạn.', cost: 20 },
  { id: 'e_escape', name: '🗝️ Escape Room Trải Nghiệm', description: 'Thử thách trí não với một phòng escape room cùng đồng đội.', cost: 50 },
  { id: 'e_disney', name: '🏰 Ngày Công Viên Chủ Đề', description: 'Tự thưởng một ngày vui chơi tại công viên chủ đề.', cost: 90 },
  { id: 'e_aquarium', name: '🐠 Thủy Cung Kỳ Thú', description: 'Tham quan thủy cung và khám phá thế giới đại dương.', cost: 30 },
  { id: 'e_zoo', name: '🦁 Vé Sở Thú Cùng Gia Đình', description: 'Đưa gia đình đến sở thú hoặc vườn thực vật cuối tuần.', cost: 35 },
  // ✈️ Du lịch & Khám phá
  { id: 't_picnic', name: '🧺 Buổi Picnic Dã Ngoại', description: 'Lên kế hoạch một buổi picnic ngoài trời thư thái cuối tuần.', cost: 25 },
  { id: 't_daytrip', name: '🚌 Chuyến Đi Chơi Gần 1 Ngày', description: 'Tự thưởng một chuyến đi chơi thành phố gần nhất trong ngày.', cost: 60 },
  { id: 't_staycation', name: '🏨 Một Đêm Staycation Khách Sạn', description: 'Đặt 1 đêm tại khách sạn đẹp gần nhà để thư giãn trọn vẹn.', cost: 120 },
  { id: 't_camping', name: '⛺ Chuyến Cắm Trại Cuối Tuần', description: 'Tổ chức một chuyến cắm trại tại núi rừng hoặc bãi biển.', cost: 70 },
  { id: 't_photo', name: '📸 Buổi Chụp Ảnh Kỷ Niệm', description: 'Thuê nhiếp ảnh gia hoặc tự tổ chức buổi chụp ảnh đẹp.', cost: 80 },
  { id: 't_sunsetcafe', name: '🌅 Cà Phê Ngắm Hoàng Hôn', description: 'Tìm một quán cà phê view đẹp để ngắm hoàng hôn thư thái.', cost: 15 },
  { id: 't_boat', name: '⛵ Chuyến Du Thuyền Sông', description: 'Đặt vé du thuyền ngắm cảnh sông hoặc vịnh gần nhất.', cost: 45 },
  { id: 't_nightmarket', name: '🌙 Dạo Chợ Đêm', description: 'Khám phá chợ đêm địa phương và thưởng thức ẩm thực đường phố.', cost: 20 },
  // 🏠 Nhà cửa & Không gian sống
  { id: 'h_candle', name: '🕯️ Nến Thơm Thư Giãn', description: 'Mua một cây nến thơm cao cấp để thư giãn tại nhà.', cost: 20 },
  { id: 'h_plant', name: '🌱 Cây Xanh Mini Để Bàn', description: 'Mua một chậu cây xanh mini mang lại không khí trong lành.', cost: 15 },
  { id: 'h_diffuser', name: '🌸 Máy Khuếch Tán Tinh Dầu', description: 'Tự thưởng một máy khuếch tán tinh dầu thư giãn phòng ngủ.', cost: 50 },
  { id: 'h_fairy', name: '✨ Đèn LED Fairy Decor', description: 'Mua đèn LED fairy để trang trí góc học tập hoặc phòng ngủ.', cost: 20 },
  { id: 'h_towel', name: '🛁 Bộ Khăn Tắm Cao Cấp', description: 'Nâng cấp bộ khăn tắm mềm mại để mỗi ngày đều sang xịn.', cost: 30 },
  { id: 'h_pillow', name: '😴 Gối Ngủ Chống Đau Cổ', description: 'Đầu tư gối ngủ chất lượng để có giấc ngủ sâu hơn mỗi đêm.', cost: 60 },
  { id: 'h_mug', name: '☕ Ly Uống Nước Cá Nhân Đẹp', description: 'Tự thưởng một chiếc mug cà phê đặc biệt chỉ dành cho bạn.', cost: 15 },
  { id: 'h_organizer', name: '🗂️ Hộp Đựng Đồ Thông Minh', description: 'Mua hộp đựng đồ thông minh để tổ chức không gian gọn gàng.', cost: 25 },
  { id: 'h_mat', name: '🧘 Thảm Yoga Cao Cấp', description: 'Đầu tư thảm yoga chống trơn chất lượng tốt cho tập luyện tại nhà.', cost: 60 },
  { id: 'h_lamp', name: '💡 Đèn Đọc Sách Bảo Vệ Mắt', description: 'Mua đèn đọc sách chống mỏi mắt để học tập hiệu quả hơn.', cost: 40 },
  { id: 'h_airpurifier', name: '🌬️ Máy Lọc Không Khí Mini', description: 'Đầu tư máy lọc không khí nhỏ để phòng ngủ luôn trong lành.', cost: 150 },
  { id: 'h_blender', name: '🥤 Máy Xay Sinh Tố Mini', description: 'Mua máy xay sinh tố mini để tự làm đồ uống lành mạnh.', cost: 80 },
  // 👗 Thời trang & Chăm sóc bản thân
  { id: 'b_haircut', name: '💇 Cắt Tóc & Tạo Kiểu Mới', description: 'Tự thưởng một lần cắt tóc và tạo kiểu mới toanh tươi trẻ hơn.', cost: 30 },
  { id: 'b_skincare', name: '✨ Bộ Dưỡng Da Mini Cao Cấp', description: 'Thưởng bộ dưỡng da mini của thương hiệu yêu thích.', cost: 45 },
  { id: 'b_perfume', name: '🌺 Nước Hoa Mini Thơm Dịu', description: 'Tự thưởng một lọ nước hoa mini cho ngày đặc biệt.', cost: 35 },
  { id: 'b_shirt', name: '👔 Áo Thun Basic Cao Cấp', description: 'Mua một chiếc áo thun basic chất liệu tốt thưởng cho bản thân.', cost: 40 },
  { id: 'b_socks', name: '🧦 Bộ Tất Vui Vẻ Màu Sắc', description: 'Mua một bộ tất vui nhộn màu sắc để mood ngày nào cũng tốt.', cost: 10 },
  { id: 'b_lotion', name: '🧴 Kem Dưỡng Thể Thư Giãn', description: 'Tự thưởng một lọ kem dưỡng thể thơm mát cao cấp.', cost: 25 },
  { id: 'b_nail', name: '💅 Làm Nail Tự Thưởng', description: 'Đặt lịch làm nail đẹp để tự tin hơn trong tuần tới.', cost: 30 },
  { id: 'b_watch', name: '⌚ Dây Đeo Đồng Hồ Mới', description: 'Thay dây đồng hồ mới màu yêu thích để tươi mới hơn.', cost: 20 },
  { id: 'b_sunglasses', name: '🕶️ Kính Mát Thời Trang', description: 'Tự thưởng một chiếc kính mát thời trang cho mùa hè.', cost: 35 },
  { id: 'b_hat', name: '🧢 Mũ Lưỡi Trai Cá Tính', description: 'Mua một chiếc mũ lưỡi trai cá tính thể hiện phong cách.', cost: 20 },
  { id: 'b_bag', name: '👜 Túi Xách Mini Đẹp', description: 'Thưởng một chiếc túi xách mini tiện dụng và thời trang.', cost: 55 },
  // 🧩 Sở thích & Sáng tạo
  { id: 'c_paint', name: '🎨 Bộ Màu Vẽ Sáng Tạo', description: 'Mua bộ màu vẽ để thỏa sức sáng tạo và thư giãn cuối tuần.', cost: 35 },
  { id: 'c_lego', name: '🧱 Bộ Lego Mini', description: 'Tự thưởng một bộ Lego nhỏ để thư giãn và giải trí.', cost: 40 },
  { id: 'c_puzzle', name: '🧩 Tranh Xếp Hình 500 Mảnh', description: 'Mua tranh xếp hình để thử thách trí não và thư giãn.', cost: 25 },
  { id: 'c_origami', name: '🦋 Bộ Giấy Origami Đẹp', description: 'Mua bộ giấy origami màu sắc và học gấp các hình đẹp.', cost: 10 },
  { id: 'c_cooking', name: '👨‍🍳 Dụng Cụ Nấu Ăn Mới', description: 'Mua một dụng cụ nấu ăn nhỏ mới để thêm vui khi vào bếp.', cost: 30 },
  { id: 'c_music', name: '🎵 Phụ Kiện Nhạc Cụ Yêu Thích', description: 'Mua dây đàn mới hoặc phụ kiện nhạc cụ bạn đang chơi.', cost: 25 },
  { id: 'c_calligraphy', name: '✍️ Bộ Bút Calligraphy', description: 'Tự thưởng bộ bút thư pháp để học viết chữ đẹp nghệ thuật.', cost: 20 },
  { id: 'c_terrarium', name: '🌿 Bộ Làm Terrarium Mini', description: 'Tự tay làm một terrarium xanh mát để trang trí góc nhỏ.', cost: 30 },
  { id: 'c_photo_print', name: '🖼️ In Ảnh Kỷ Niệm Đẹp', description: 'In một bộ ảnh kỷ niệm đẹp và đóng khung trang trí nhà.', cost: 20 },
  // 💼 Công việc & Networking
  { id: 'w_coffee_meet', name: '☕ Coffee Chat Networking', description: 'Tổ chức buổi coffee networking để kết nối với người mới.', cost: 20 },
  { id: 'w_business_card', name: '💼 Danh Thiếp Cá Nhân Đẹp', description: 'In danh thiếp cá nhân thiết kế đẹp để tạo ấn tượng chuyên nghiệp.', cost: 20 },
  { id: 'w_linkedin', name: '🔗 LinkedIn Premium 1 Tháng', description: 'Nâng cấp LinkedIn Premium để mở rộng cơ hội nghề nghiệp.', cost: 80 },
  { id: 'w_headshot', name: '📸 Ảnh Chân Dung Chuyên Nghiệp', description: 'Thuê chụp ảnh chân dung chuyên nghiệp cho hồ sơ LinkedIn.', cost: 60 },
  { id: 'w_standing_desk', name: '🖥️ Phụ Kiện Bàn Làm Việc', description: 'Mua một phụ kiện bàn làm việc thông minh tăng năng suất.', cost: 50 },
];

const financialHabits = ref([]);

const totalHabitPoints = ref(0);
const showRewards = ref(false);
const unlockedGoldenBadge = ref(false);
const unlockedGoldenTheme = ref(false);
const activeTheme = ref('purple');
const aiComplimentText = ref('');
const showComplimentModal = ref(false);

const levelInfo = computed(() => {
  const pts = totalHabitPoints.value;
  if (pts < 50) {
    return {
      level: 1,
      title: 'Tập sự tài chính',
      max: 50,
      progress: (pts / 50) * 100
    };
  } else if (pts < 150) {
    return {
      level: 2,
      title: 'Người tiêu dùng thông thái',
      max: 150,
      progress: ((pts - 50) / 100) * 100
    };
  } else if (pts < 300) {
    return {
      level: 3,
      title: 'Chuyên gia ngân sách',
      max: 300,
      progress: ((pts - 150) / 150) * 100
    };
  } else {
    return {
      level: 4,
      title: 'Chiến thần tiết kiệm',
      max: 1000,
      progress: Math.min(100, ((pts - 300) / 700) * 100)
    };
  }
});



const saveHabits = () => {
  localStorage.setItem('financial_habits', JSON.stringify(financialHabits.value));
};

const onHabitChange = (habit) => {
  saveHabits();
  let currentPoints = parseInt(localStorage.getItem('total_habit_points') || '0', 10);
  if (habit.completed) {
    currentPoints += habit.points;
  } else {
    currentPoints = Math.max(0, currentPoints - habit.points);
  }
  totalHabitPoints.value = currentPoints;
  localStorage.setItem('total_habit_points', currentPoints.toString());
};

const generateDailyTasks = (dateStr) => {
  let hash = 0;
  for (let i = 0; i < dateStr.length; i++) {
    hash = dateStr.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  const seededRandom = () => {
    const x = Math.sin(hash++) * 10000;
    return x - Math.floor(x);
  };

  const pool = [...habitsPool];
  for (let i = pool.length - 1; i > 0; i--) {
    const j = Math.floor(seededRandom() * (i + 1));
    const temp = pool[i];
    pool[i] = pool[j];
    pool[j] = temp;
  }
  
  return pool.slice(0, 20).map(t => ({
    ...t,
    completed: false
  }));
};

const loadHabits = () => {
  const todayStr = new Date().toLocaleDateString('sv-SE'); // Định dạng YYYY-MM-DD
  const savedDate = localStorage.getItem('financial_habits_date');
  const savedHabits = localStorage.getItem('financial_habits');
  
  if (savedDate === todayStr && savedHabits) {
    try {
      financialHabits.value = JSON.parse(savedHabits);
    } catch (e) {
      const fresh = generateDailyTasks(todayStr);
      financialHabits.value = fresh;
      localStorage.setItem('financial_habits', JSON.stringify(fresh));
      localStorage.setItem('financial_habits_date', todayStr);
    }
  } else {
    // Ngày mới hoặc chưa từng có dữ liệu
    const fresh = generateDailyTasks(todayStr);
    financialHabits.value = fresh;
    localStorage.setItem('financial_habits', JSON.stringify(fresh));
    localStorage.setItem('financial_habits_date', todayStr);
  }

  totalHabitPoints.value = parseInt(localStorage.getItem('total_habit_points') || '0', 10);
  unlockedGoldenBadge.value = localStorage.getItem('unlocked_golden_badge') === 'true';
  unlockedGoldenTheme.value = localStorage.getItem('unlocked_golden_theme') === 'true';
  activeTheme.value = localStorage.getItem('active_theme') || 'purple';
};

const toggleTheme = () => {
  if (!unlockedGoldenTheme.value) return;
  activeTheme.value = activeTheme.value === 'purple' ? 'gold' : 'purple';
  localStorage.setItem('active_theme', activeTheme.value);
};

const purchaseReward = (reward) => {
  if (totalHabitPoints.value < reward.cost) {
    notificationStore.showAlert('Bạn không đủ điểm thói quen để đổi phần quà này!', 'Thiếu điểm');
    return;
  }
  
  if (reward.id === 'golden_badge' && unlockedGoldenBadge.value) {
    notificationStore.showAlert('Bạn đã sở hữu danh hiệu này rồi!', 'Đã sở hữu');
    return;
  }
  if (reward.id === 'golden_theme' && unlockedGoldenTheme.value) {
    notificationStore.showAlert('Bạn đã sở hữu chủ đề này rồi!', 'Đã sở hữu');
    return;
  }

  totalHabitPoints.value -= reward.cost;
  localStorage.setItem('total_habit_points', totalHabitPoints.value.toString());

  if (reward.id === 'ai_compliment') {
    const compliments = [
      "Xuất sắc! Bạn quản lý tiền nong đỉnh như thế này thì ngày trở thành triệu phú không còn xa đâu!",
      "Tôi ngả mũ thán phục trước kỷ luật thép của bạn. Tiết kiệm giỏi thế này quả là hiếm có!",
      "Đúng là thần tài giữ của! Sự cẩn thận của bạn thật đáng để học tập.",
      "Bạn hôm nay quá tuyệt vời! Cứ duy trì phong độ giữ ví này nhé, ví tiền của bạn đang cười rất tươi đấy!"
    ];
    const rand = compliments[Math.floor(Math.random() * compliments.length)];
    aiComplimentText.value = rand;
    showComplimentModal.value = true;
  } else if (reward.id === 'golden_badge') {
    unlockedGoldenBadge.value = true;
    localStorage.setItem('unlocked_golden_badge', 'true');
    notificationStore.showAlert('Chúc mừng! Bạn đã mở khóa Danh hiệu Hoàng Kim. Vương miện đã xuất hiện cạnh tên bạn.', 'Thành công');
  } else if (reward.id === 'golden_theme') {
    unlockedGoldenTheme.value = true;
    localStorage.setItem('unlocked_golden_theme', 'true');
    activeTheme.value = 'gold';
    localStorage.setItem('active_theme', 'gold');
    notificationStore.showAlert('Mở khóa thành công! Giao diện đã được nâng cấp lên Chủ đề Màu Hoàng Kim.', 'Thành công');
  }
};

onMounted(async () => {
  await transactionStore.fetchTransactions();
  await transactionStore.fetchSummary();
  await transactionStore.fetchInsights();
  loadHabits();
  
  const userBase = authStore.user?.currency || 'VND';
  quickForm.currency = userBase;
});

const recentTransactions = computed(() => {
  return transactionStore.transactions.slice(0, 5);
});

const hasExpenseData = computed(() => {
  return transactionStore.summary?.category_expenses?.length > 0;
});

const pieChartSeries = computed(() => {
  if (!hasExpenseData.value) return [];
  return transactionStore.summary.category_expenses.map(item => item.total);
});

const pieChartOptions = computed(() => {
  if (!hasExpenseData.value) return {};
  const labels = transactionStore.summary.category_expenses.map(item => item.category);
  return {
    labels: labels,
    chart: {
      foreColor: '#64748b',
      background: 'transparent',
    },
    stroke: {
      show: true,
      colors: ['#ffffff'],
      width: 2.0,
    },
    colors: ['#8000ff', '#4f46e5', '#0d9488', '#0284c7', '#059669', '#d97706', '#ea580c', '#e11d48'],
    legend: {
      position: 'bottom',
      fontSize: '11px',
      markers: { radius: 2 }
    },
    dataLabels: {
      enabled: false
    },
    tooltip: {
      theme: 'light',
      y: {
        formatter: (val) => formatCurrency(val)
      }
    }
  };
});

const handleQuickAddClick = () => {
  if (authStore.isGuest) {
    promptLogin();
    return;
  }
  showQuickAdd.value = true;
};

const promptLogin = async () => {
  await notificationStore.showAlert('Vui lòng đăng nhập để thực hiện tính năng này!', 'Yêu cầu Đăng nhập');
  router.push('/login');
};

const submitQuickAdd = async () => {
  quickAdding.value = true;
  try {
    await transactionStore.addTransaction({
      amount: quickForm.amount,
      type: quickForm.type,
      category: quickForm.category,
      currency: quickForm.currency,
      exchange_rate: quickForm.exchange_rate,
      description: quickForm.description || null,
      date: new Date().toISOString()
    });
    
    quickForm.amount = null;
    quickForm.description = '';
    showQuickAdd.value = false;
  } catch (err) {
    notificationStore.showAlert(err.response?.data?.detail || 'Lỗi thêm giao dịch', 'Lỗi');
  } finally {
    quickAdding.value = false;
  }
};

const { amountInputStr, onAmountInput } = useAmountInput(quickForm, 'amount');

</script>

<style scoped>
.lock-checkbox-container input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.lock-checkbox-container {
  display: block;
  position: relative;
  cursor: pointer;
  font-size: 15px;
  user-select: none;
  border-radius: 5px;
}

.lock-checkbox-checkmark {
  position: relative;
  top: 0;
  left: 0;
  height: 1.5em;
  width: 1.5em;
  background-color: #cbd5e1;
  border-radius: 5px;
  box-shadow: 1px 1px 0px #94a3b8;
  transition: all 0.2s;
}

.lock-checkbox-container input:checked ~ .lock-checkbox-checkmark {
  box-shadow: 2px 2px 0px #94a3b8;
  background-image: linear-gradient(45deg, rgb(128, 0, 255) 0%, rgb(232, 121, 249) 100%);
}

.lock-checkbox-checkmark:after {
  content: "";
  position: absolute;
  opacity: 0;
  transition: all 0.2s;
  left: 0.5em;
  top: 0.25em;
  width: 0.3em;
  height: 0.6em;
  border: solid white;
  border-width: 0 0.15em 0.15em 0;
  transform: rotate(45deg);
}

.lock-checkbox-container input:checked ~ .lock-checkbox-checkmark:after {
  opacity: 1;
}
</style>
