<template>
  <div class="space-y-6">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Tổng kết Năm {{ selectedYear }}</h1>
        <p class="text-slate-500 text-sm mt-0.5">Nhìn lại hành trình tài chính của bạn trong cả năm.</p>
      </div>
      <div class="flex items-center gap-2 shrink-0">
        <button @click="changeYear(-1)" class="p-2 rounded-xl bg-white border border-slate-200 hover:border-purple-300 hover:text-purple-600 transition cursor-pointer">
          <ChevronLeft class="w-4 h-4" />
        </button>
        <span class="px-4 py-2 bg-white border border-slate-200 rounded-xl font-black text-slate-800 text-sm select-none min-w-[70px] text-center">{{ selectedYear }}</span>
        <button @click="changeYear(1)" :disabled="selectedYear >= currentYear" class="p-2 rounded-xl bg-white border border-slate-200 hover:border-purple-300 hover:text-purple-600 transition cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed">
          <ChevronRight class="w-4 h-4" />
        </button>
      </div>
    </div>

    <div v-if="loading" class="min-h-[60vh] flex items-center justify-center">
      <div class="flex flex-col items-center gap-3 text-slate-400">
        <div class="w-10 h-10 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
        <span class="text-sm font-semibold">Đang tải dữ liệu năm {{ selectedYear }}...</span>
      </div>
    </div>

    <div v-else-if="!data" class="min-h-[60vh] flex items-center justify-center">
      <div class="flex flex-col items-center gap-3 text-slate-400">
        <BarChart3 class="w-14 h-14 stroke-[1.2]" />
        <p class="text-sm font-semibold text-slate-500">Không có dữ liệu cho năm {{ selectedYear }}</p>
      </div>
    </div>

    <template v-else>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-white border border-slate-200 rounded-[20px] p-4 shadow-sm">
          <p class="text-[10px] text-slate-400 font-black uppercase tracking-wider mb-1">Tổng Thu Nhập</p>
          <p class="text-lg font-black text-emerald-600 font-mono">+{{ fmt(data.total_income) }}</p>
          <p class="text-[10px] text-slate-400 mt-0.5">{{ authStore.user?.currency }}</p>
        </div>
        <div class="bg-white border border-slate-200 rounded-[20px] p-4 shadow-sm">
          <p class="text-[10px] text-slate-400 font-black uppercase tracking-wider mb-1">Tổng Chi Tiêu</p>
          <p class="text-lg font-black text-red-655 font-mono">-{{ fmt(data.total_expense) }}</p>
          <p class="text-[10px] text-slate-400 mt-0.5">{{ authStore.user?.currency }}</p>
        </div>
        <div class="bg-white border border-slate-200 rounded-[20px] p-4 shadow-sm">
          <p class="text-[10px] text-slate-400 font-black uppercase tracking-wider mb-1">Tiết Kiệm Ròng</p>
          <p class="text-lg font-black font-mono" :class="data.net_savings >= 0 ? 'text-emerald-600' : 'text-red-655'">
            {{ data.net_savings >= 0 ? '+' : '' }}{{ fmt(data.net_savings) }}
          </p>
          <p class="text-[10px] text-slate-400 mt-0.5">{{ authStore.user?.currency }}</p>
        </div>
        <div class="bg-white border border-slate-200 rounded-[20px] p-4 shadow-sm">
          <p class="text-[10px] text-slate-400 font-black uppercase tracking-wider mb-1">Tổng Giao Dịch</p>
          <p class="text-lg font-black text-slate-800">{{ data.total_transactions }}</p>
          <p class="text-[10px] text-slate-400 mt-0.5">lần trong năm</p>
        </div>
      </div>

      <div class="bg-white border border-slate-200 rounded-[24px] p-5 shadow-sm">
        <h2 class="font-bold text-sm text-slate-800 uppercase tracking-wider mb-4">Thu / Chi theo từng tháng</h2>
        <div class="overflow-x-auto">
          <div class="min-w-[640px]">
            <div class="flex items-end gap-1.5 h-48 px-2">
              <div
                v-for="m in data.monthly"
                :key="m.month"
                class="flex-1 flex flex-col items-center gap-0.5 h-full justify-end"
              >
                <div class="w-full flex items-end gap-0.5 justify-center h-40">
                  <div
                    class="flex-1 bg-emerald-400/80 hover:bg-emerald-500 rounded-t-md transition-all duration-300 cursor-pointer relative group"
                    :style="{ height: barHeight(m.income, maxBarValue) + '%' }"
                    :title="`Thu: ${fmt(m.income)}`"
                  >
                    <div class="absolute -top-7 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-[8px] px-1.5 py-0.5 rounded-md whitespace-nowrap opacity-0 group-hover:opacity-100 transition pointer-events-none font-mono">
                      +{{ fmtShort(m.income) }}
                    </div>
                  </div>
                  <div
                    class="flex-1 bg-red-400/80 hover:bg-red-500 rounded-t-md transition-all duration-300 cursor-pointer relative group"
                    :style="{ height: barHeight(m.expense, maxBarValue) + '%' }"
                    :title="`Chi: ${fmt(m.expense)}`"
                  >
                    <div class="absolute -top-7 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-[8px] px-1.5 py-0.5 rounded-md whitespace-nowrap opacity-0 group-hover:opacity-100 transition pointer-events-none font-mono">
                      -{{ fmtShort(m.expense) }}
                    </div>
                  </div>
                </div>
                <span class="text-[9px] font-bold text-slate-400">T{{ m.month }}</span>
              </div>
            </div>
            <div class="flex gap-4 mt-3 justify-center">
              <div class="flex items-center gap-1.5"><div class="w-3 h-3 rounded-sm bg-emerald-400/80"></div><span class="text-[10px] text-slate-500 font-semibold">Thu nhập</span></div>
              <div class="flex items-center gap-1.5"><div class="w-3 h-3 rounded-sm bg-red-400/80"></div><span class="text-[10px] text-slate-500 font-semibold">Chi tiêu</span></div>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-white border border-slate-200 rounded-[24px] p-5 shadow-sm space-y-3">
          <h2 class="font-bold text-sm text-slate-800 uppercase tracking-wider">Điểm nổi bật</h2>
          <div class="space-y-2.5">
            <div class="flex items-center justify-between p-3 bg-emerald-50/60 border border-emerald-100 rounded-xl">
              <div class="flex items-center gap-2.5">
                <div class="w-8 h-8 bg-emerald-100 rounded-full flex items-center justify-center">
                  <TrendingUp class="w-4 h-4 text-emerald-600" />
                </div>
                <div>
                  <p class="text-[10px] text-emerald-700 font-black uppercase tracking-wider">Thu nhập cao nhất</p>
                  <p class="text-xs font-bold text-slate-800">Tháng {{ data.best_income_month.month }}</p>
                </div>
              </div>
              <span class="text-sm font-black text-emerald-600 font-mono">+{{ fmtShort(data.best_income_month.income) }}</span>
            </div>

            <div class="flex items-center justify-between p-3 bg-red-50/60 border border-red-100 rounded-xl">
              <div class="flex items-center gap-2.5">
                <div class="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                  <TrendingDown class="w-4 h-4 text-red-600" />
                </div>
                <div>
                  <p class="text-[10px] text-red-700 font-black uppercase tracking-wider">Chi tiêu cao nhất</p>
                  <p class="text-xs font-bold text-slate-800">Tháng {{ data.worst_expense_month.month }}</p>
                </div>
              </div>
              <span class="text-sm font-black text-red-600 font-mono">-{{ fmtShort(data.worst_expense_month.expense) }}</span>
            </div>

            <div class="flex items-center justify-between p-3 bg-purple-50/60 border border-purple-100 rounded-xl">
              <div class="flex items-center gap-2.5">
                <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                  <Sparkles class="w-4 h-4 text-purple-600" />
                </div>
                <div>
                  <p class="text-[10px] text-purple-700 font-black uppercase tracking-wider">Tiết kiệm ròng tốt nhất</p>
                  <p class="text-xs font-bold text-slate-800">Tháng {{ data.best_net_month.month }}</p>
                </div>
              </div>
              <span class="text-sm font-black font-mono" :class="data.best_net_month.net >= 0 ? 'text-purple-600' : 'text-red-600'">
                {{ data.best_net_month.net >= 0 ? '+' : '' }}{{ fmtShort(data.best_net_month.net) }}
              </span>
            </div>
          </div>
        </div>

        <div class="space-y-4">
          <div class="bg-white border border-slate-200 rounded-[24px] p-5 shadow-sm">
            <h2 class="font-bold text-xs text-slate-800 uppercase tracking-wider mb-3">Top chi tiêu</h2>
            <div class="space-y-2">
              <div v-if="data.top_expense_categories.length === 0" class="text-[11px] text-slate-400 italic">Chưa có dữ liệu</div>
              <div v-for="(cat, idx) in data.top_expense_categories" :key="cat.category" class="flex items-center gap-2">
                <span class="text-[10px] font-black text-slate-400 w-4">{{ idx + 1 }}</span>
                <div class="flex-1">
                  <div class="flex justify-between mb-0.5">
                    <span class="text-[11px] font-bold text-slate-700">{{ cat.category }}</span>
                    <span class="text-[11px] font-black text-red-655 font-mono">{{ fmtShort(cat.total) }}</span>
                  </div>
                  <div class="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                    <div class="h-full bg-red-400 rounded-full transition-all duration-500"
                      :style="{ width: pctOf(cat.total, data.total_expense) + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white border border-slate-200 rounded-[24px] p-5 shadow-sm">
            <h2 class="font-bold text-xs text-slate-800 uppercase tracking-wider mb-3">Top thu nhập</h2>
            <div class="space-y-2">
              <div v-if="data.top_income_categories.length === 0" class="text-[11px] text-slate-400 italic">Chưa có dữ liệu</div>
              <div v-for="(cat, idx) in data.top_income_categories" :key="cat.category" class="flex items-center gap-2">
                <span class="text-[10px] font-black text-slate-400 w-4">{{ idx + 1 }}</span>
                <div class="flex-1">
                  <div class="flex justify-between mb-0.5">
                    <span class="text-[11px] font-bold text-slate-700">{{ cat.category }}</span>
                    <span class="text-[11px] font-black text-emerald-600 font-mono">{{ fmtShort(cat.total) }}</span>
                  </div>
                  <div class="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                    <div class="h-full bg-emerald-400 rounded-full transition-all duration-500"
                      :style="{ width: pctOf(cat.total, data.total_income) + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white border border-slate-200 rounded-[24px] p-5 shadow-sm">
        <h2 class="font-bold text-sm text-slate-800 uppercase tracking-wider mb-4">Chi tiết từng tháng</h2>
        <div class="hidden sm:block overflow-x-auto">
          <table class="w-full text-center border-collapse text-xs">
            <thead>
              <tr class="text-slate-400 border-b border-slate-200 uppercase text-[9px] tracking-wider font-bold">
                <th class="py-2.5 px-4 border-r border-slate-200/60 text-center">Tháng</th>
                <th class="py-2.5 px-4 border-r border-slate-200/60 text-center">Thu nhập</th>
                <th class="py-2.5 px-4 border-r border-slate-200/60 text-center">Chi tiêu</th>
                <th class="py-2.5 px-4 text-center">Tiết kiệm ròng</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in data.monthly" :key="m.month"
                class="border-b border-slate-100 hover:bg-slate-50 transition"
                :class="{ 'bg-purple-50/50': m.month === new Date().getMonth() + 1 && selectedYear === currentYear }"
              >
                <td class="py-2.5 px-4 border-r border-slate-100 font-bold text-slate-700 text-center">
                  Tháng {{ m.month }}
                  <span v-if="m.month === new Date().getMonth() + 1 && selectedYear === currentYear" class="ml-1 text-[8px] text-purple-600 font-black bg-purple-100 px-1 py-0.5 rounded-full">Hiện tại</span>
                </td>
                <td class="py-2.5 px-4 border-r border-slate-100 font-bold text-emerald-600 font-mono text-center">
                  {{ m.income > 0 ? '+' + fmt(m.income) : '—' }}
                </td>
                <td class="py-2.5 px-4 border-r border-slate-100 font-bold text-red-655 font-mono text-center">
                  {{ m.expense > 0 ? '-' + fmt(m.expense) : '—' }}
                </td>
                <td class="py-2.5 px-4 font-black font-mono text-center" :class="m.net > 0 ? 'text-emerald-600' : m.net < 0 ? 'text-red-655' : 'text-slate-400'">
                  {{ m.income === 0 && m.expense === 0 ? '—' : (m.net >= 0 ? '+' : '') + fmt(m.net) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="block sm:hidden space-y-2.5">
          <div v-for="m in data.monthly" :key="m.month"
            class="border border-slate-100 rounded-xl p-3 space-y-2"
            :class="m.income === 0 && m.expense === 0 ? 'opacity-40' : ''"
          >
            <div class="flex justify-between items-center">
              <span class="text-xs font-black text-slate-800">Tháng {{ m.month }}</span>
              <span v-if="m.month === new Date().getMonth() + 1 && selectedYear === currentYear" class="text-[8px] text-purple-600 font-black bg-purple-100 px-1.5 py-0.5 rounded-full">Hiện tại</span>
            </div>
            <div class="flex justify-between text-[11px]">
              <span class="text-emerald-600 font-mono font-bold">{{ m.income > 0 ? '+' + fmt(m.income) : '—' }}</span>
              <span class="text-red-655 font-mono font-bold">{{ m.expense > 0 ? '-' + fmt(m.expense) : '—' }}</span>
              <span class="font-black font-mono" :class="m.net > 0 ? 'text-purple-600' : m.net < 0 ? 'text-red-655' : 'text-slate-300'">
                {{ m.income === 0 && m.expense === 0 ? '—' : (m.net >= 0 ? '+' : '') + fmt(m.net) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import api from '../services/api';
import { useAuthStore } from '../stores/auth';
import { ChevronLeft, ChevronRight, BarChart3, TrendingUp, TrendingDown, Sparkles } from 'lucide-vue-next';

const authStore = useAuthStore();

const currentYear = new Date().getFullYear();
const selectedYear = ref(currentYear);
const data = ref(null);
const loading = ref(false);

const fetchData = async () => {
  loading.value = true;
  data.value = null;
  try {
    const res = await api.get(`/reports/yearly-summary?year=${selectedYear.value}`);
    data.value = res.data;
  } catch (err) {
    console.error('Failed to fetch yearly summary:', err);
  } finally {
    loading.value = false;
  }
};

const changeYear = (delta) => {
  if (selectedYear.value + delta > currentYear) return;
  selectedYear.value += delta;
};

const maxBarValue = computed(() => {
  if (!data.value) return 1;
  return Math.max(
    ...data.value.monthly.map(m => Math.max(m.income, m.expense)),
    1
  );
});

const barHeight = (val, max) => {
  if (!max || max === 0) return 0;
  return Math.max((val / max) * 100, val > 0 ? 2 : 0);
};

const fmt = (val) => {
  return Math.abs(val).toLocaleString('vi-VN') + ' đ';
};

const fmtShort = (val) => {
  const abs = Math.abs(val);
  if (abs >= 1_000_000_000) return (abs / 1_000_000_000).toFixed(1) + ' Tỷ';
  if (abs >= 1_000_000) return (abs / 1_000_000).toFixed(1) + ' Tr';
  if (abs >= 1_000) return (abs / 1_000).toFixed(0) + 'K';
  return abs.toLocaleString('vi-VN') + ' đ';
};

const pctOf = (val, total) => {
  if (!total || total === 0) return 0;
  return Math.max((val / total) * 100, 2);
};

watch(selectedYear, fetchData);
onMounted(fetchData);
</script>
