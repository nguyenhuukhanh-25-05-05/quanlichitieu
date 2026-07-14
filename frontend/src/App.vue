<template>
  <div v-if="isAuthPage || !authStore.isAuthenticated" class="min-h-screen bg-slate-50">
    <router-view></router-view>
  </div>

  <div v-else class="min-h-screen text-slate-800 flex flex-col relative select-none os-workspace">
    <header class="fixed top-0 left-0 right-0 h-8 px-4 sm:px-6 bg-white/75 backdrop-blur-md border-b border-slate-200/30 z-40 flex items-center justify-between text-xs text-slate-650 font-semibold select-none shadow-sm flex-nowrap overflow-hidden">
      <div class="flex items-center gap-2 shrink-0">
        <div class="flex items-center gap-1.5 font-extrabold text-slate-900">
          <Wallet class="w-4 h-4 text-[#8000ff]" />
          <span class="hidden sm:inline">AuraFinance</span>
        </div>
      </div>

      <div class="absolute left-1/2 -translate-x-1/2 hidden md:block text-[11px] font-bold text-slate-500 tracking-wider whitespace-nowrap">
        {{ currentWindowTitle }}
      </div>

      <div class="flex items-center gap-2.5 sm:gap-4 ml-auto shrink-0 flex-nowrap">
        <div class="flex items-center gap-1 font-bold" title="Thời tiết TP.HCM">
          <component :is="weatherIconComponent" class="w-3.5 h-3.5 text-slate-500" />
          <span>{{ weatherText }}</span>
        </div>
        
        <span class="text-slate-200/80 text-[10px] sm:text-xs">|</span>

        <div class="relative hidden sm:block">
          <button 
            @click.stop="showCalendarDropdown = !showCalendarDropdown"
            class="flex items-center gap-1 font-bold text-slate-500 hover:text-[#8000ff] transition cursor-pointer select-none"
            title="Xem lịch chi tiết"
          >
            <Calendar class="w-3.5 h-3.5 text-purple-500" />
            <span>{{ solarDateText }} ({{ lunarDateText }})</span>
          </button>

          <div 
            v-if="showCalendarDropdown"
            @click.stop
            class="absolute right-0 mt-2 w-72 bg-white border border-slate-200 rounded-[20px] p-4 shadow-xl z-50 select-none"
          >
            <div class="flex justify-between items-center mb-3">
              <button @click.stop="prevMonth" class="p-1 rounded-full hover:bg-slate-100 transition cursor-pointer">
                <ChevronLeft class="w-4 h-4 text-slate-600" />
              </button>
              <span class="font-bold text-[10px] text-slate-800 uppercase tracking-wider">{{ calendarMonthName }}</span>
              <button @click.stop="nextMonth" class="p-1 rounded-full hover:bg-slate-100 transition cursor-pointer">
                <ChevronRight class="w-4 h-4 text-slate-600" />
              </button>
            </div>

            <div class="grid grid-cols-7 gap-1 text-center text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
              <span>T2</span><span>T3</span><span>T4</span><span>T5</span><span>T6</span><span>T7</span><span>CN</span>
            </div>

            <div class="grid grid-cols-7 gap-1">
              <div 
                v-for="(day, idx) in calendarWeeks.flat()" 
                :key="idx"
                class="relative h-9 flex flex-col items-center justify-center rounded-lg text-xs transition-all font-mono"
                :class="[
                  day.isCurrentMonth ? 'text-slate-800' : 'text-slate-200',
                  day.isToday ? 'bg-[#8000ff] text-white font-black shadow-md shadow-purple-100' : 'hover:bg-slate-50 cursor-pointer'
                ]"
              >
                <span class="font-bold text-[11px]">{{ day.solarDay }}</span>
                <span 
                  class="absolute bottom-0.5 right-0.5 text-[7px]" 
                  :class="day.isToday ? 'text-purple-200' : 'text-slate-400'"
                >
                  {{ day.lunarDay }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <span class="text-slate-200/80 text-[10px] sm:text-xs hidden sm:inline">|</span>

        <button 
          @click.stop="isLocked = true"
          class="flex items-center gap-1 hover:text-[#8000ff] active:scale-95 transition cursor-pointer font-bold text-slate-500"
          title="Khóa màn hình"
        >
          <Lock class="w-3.5 h-3.5 hover:text-[#8000ff]" />
          <span class="hidden sm:inline">Khóa</span>
        </button>

        <span class="text-slate-200/80 text-[10px] sm:text-xs">|</span>

        <div class="flex items-center gap-1.5 font-mono font-bold text-slate-600">
          <Clock class="w-3.5 h-3.5 text-slate-450" />
          <span class="hidden xs:inline">{{ currentTimeString }}</span>
          <span class="xs:hidden">{{ currentTimeStringMobile }}</span>
        </div>
      </div>
    </header>

    <main class="flex-1 w-full max-w-[97%] mx-auto px-4 pt-12 pb-24 flex flex-col justify-start z-10 select-text">
      <router-view></router-view>
    </main>

    <div 
      v-if="!isAuthPage"
      class="fixed bottom-6 left-1/2 -translate-x-1/2 z-40 bg-white border-2 border-slate-300/80 px-3 sm:px-5 py-1.5 sm:py-2.5 rounded-[24px] flex items-center gap-2.5 sm:gap-5 shadow-[0_20px_40px_rgba(0,0,0,0.12)] transition-all duration-500 ease-out select-none max-w-[95vw] sm:max-w-none justify-around sm:justify-start"
      :class="isDockHidden ? 'translate-y-[150%] opacity-0 pointer-events-none' : 'translate-y-0 opacity-100'"
    >
      <button 
        @click.stop="isDockHidden = true" 
        class="absolute -top-2.5 left-1/2 -translate-x-1/2 bg-white border border-slate-300/60 w-12 h-2.5 rounded-full shadow-sm cursor-pointer flex items-center justify-center hover:border-purple-300 group transition-all"
        title="Thu ẩn thanh Dock"
      >
        <span class="w-6 h-1 bg-slate-300 rounded-full group-hover:bg-[#8000ff] transition-colors"></span>
      </button>

      <router-link 
        v-for="item in dockItems"
        :key="item.path"
        :to="item.path" 
        class="group relative p-2 sm:p-2.5 rounded-xl sm:rounded-2xl transition-all duration-200 hover:scale-110 sm:hover:scale-125 hover:-translate-y-1 sm:hover:-translate-y-2 flex items-center justify-center text-slate-500 hover:text-[#8000ff] hover:bg-purple-50"
        :class="{ 'text-[#8000ff] bg-purple-50 border border-purple-100/50 shadow-sm': isActive(item.path) }"
      >
        <component :is="item.icon" class="w-5.5 h-5.5 sm:w-6.5 sm:h-6.5" />
        <span class="absolute -top-10 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-[10px] px-2.5 py-1 rounded-md opacity-0 group-hover:opacity-100 transition duration-150 whitespace-nowrap pointer-events-none font-bold shadow-lg">{{ item.label }}</span>
        <div v-if="isActive(item.path)" class="w-1.5 h-1.5 bg-[#8000ff] rounded-full absolute -bottom-1 left-1/2 -translate-x-1/2 shadow-[0_0_8px_#8000ff]"></div>
      </router-link>

      <span class="w-[1px] h-6 bg-slate-200/80"></span>

      <!-- Logout Action Icon -->
      <button 
        @click="handleLogout"
        class="group relative p-2 sm:p-2.5 rounded-xl sm:rounded-2xl transition-all duration-200 hover:scale-110 sm:hover:scale-125 hover:-translate-y-1 sm:hover:-translate-y-2 flex items-center justify-center text-slate-400 hover:text-red-500 hover:bg-red-50 cursor-pointer"
      >
        <LogOut class="w-5.5 h-5.5 sm:w-6.5 sm:h-6.5" />
        <span class="absolute -top-10 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-[10px] px-2.5 py-1 rounded-md opacity-0 group-hover:opacity-100 transition duration-150 whitespace-nowrap pointer-events-none font-bold shadow-lg">Đăng xuất</span>
      </button>
    </div>

    <transition name="toast-slide">
      <div 
        v-if="isDockHidden && !isAuthPage"
        @click="isDockHidden = false"
        @mouseenter="isDockHidden = false"
        class="fixed bottom-2 left-1/2 -translate-x-1/2 z-40 px-5 py-1.5 bg-white/90 backdrop-blur-md border-2 border-slate-350/80 rounded-full shadow-[0_10px_25px_rgba(0,0,0,0.08)] cursor-pointer hover:shadow-[0_10px_30px_rgba(128,0,255,0.18)] hover:border-purple-300 transition-all duration-300 flex items-center gap-2 group"
      >
        <div class="w-1.5 h-1.5 rounded-full bg-[#8000ff] group-hover:scale-125 transition-transform duration-200"></div>
        <span class="text-[9px] font-black tracking-widest text-[#8000ff] uppercase select-none">Hiển thị Dock</span>
      </div>
    </transition>

    <transition name="toast-slide">
      <div 
        v-if="notificationStore.activeToast"
        class="fixed bottom-6 right-6 max-w-sm w-full p-4 rounded-[20px] bg-white border border-slate-200 border-l-4 shadow-lg z-50 flex gap-3 pointer-events-auto"
        :class="notificationStore.activeToast.level === 'CRITICAL' ? 'border-l-red-500' : 'border-l-blue-500'"
      >
        <div class="p-2 rounded-sm bg-blue-500/10 text-blue-600 shrink-0 self-start">
          <Sparkles class="w-5 h-5 text-blue-600" v-if="notificationStore.activeToast.level !== 'CRITICAL'" />
          <AlertOctagon class="w-5 h-5 text-red-500" v-else />
        </div>
        <div class="flex-1 space-y-1">
          <h5 class="font-bold text-sm text-slate-800">
            {{ notificationStore.activeToast.level === 'CRITICAL' ? 'Cảnh báo Nguy cấp' : 'Cảnh báo Ngân sách' }}
          </h5>
          <p class="text-xs text-slate-655 leading-relaxed">
            {{ notificationStore.activeToast.message }}
          </p>
        </div>
        <div class="flex flex-col gap-2 shrink-0 self-start">
          <button 
            @click="notificationStore.removeToast"
            class="text-slate-455 hover:text-slate-800 cursor-pointer"
          >
            <X class="w-4 h-4" />
          </button>
        </div>
      </div>
    </transition>

    <transition name="lock-fade">
      <div 
        v-if="isLocked && !isAuthPage"
        class="fixed inset-0 z-50 flex flex-col items-center justify-center gap-12 sm:gap-16 py-10 sm:py-16 px-4 sm:px-6 bg-white/45 backdrop-blur-2xl text-slate-800 overflow-hidden h-screen"
      >
        <div class="flex flex-col items-center text-center space-y-2 sm:space-y-4 mt-4 sm:mt-8 animate-in fade-in slide-in-from-top duration-700">
          <div class="text-5xl sm:text-7xl font-black font-sans tracking-wider drop-shadow-sm select-none text-slate-900">
            {{ lockScreenTime }}
          </div>
          <div class="text-[11px] sm:text-sm font-bold tracking-wide drop-shadow-sm select-none text-slate-500 max-w-[280px] sm:max-w-none">
            {{ lockScreenDate }}
          </div>
        </div>

        <div class="flex flex-col items-center space-y-4 sm:space-y-6 animate-in fade-in zoom-in duration-500 delay-200">
          <div class="w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-purple-50 backdrop-blur-md border-2 border-purple-200 flex items-center justify-center shadow-xl relative group overflow-hidden">
            <span class="text-2xl sm:text-3xl font-extrabold text-[#8000ff] select-none">
              {{ userInitial }}
            </span>
          </div>
          <div class="text-center space-y-1">
            <h3 class="text-base sm:text-lg font-black tracking-wide text-slate-900">Chào mừng trở lại!</h3>
            <p class="text-[11px] sm:text-xs text-slate-500 font-semibold truncate max-w-[180px] sm:max-w-[240px]" :title="authStore.user?.fullname || authStore.user?.email">
              {{ authStore.user?.fullname || authStore.user?.email || 'Khách truy cập' }}
            </p>
          </div>
          <button class="lock-btn scale-90 sm:scale-100" @click.stop="unlock">
            <div class="lock-btn-wrapper">
              <p class="lock-btn-text">MỞ KHÓA</p>

              <div class="lock-btn-flower lock-btn-flower1">
                <div class="lock-btn-petal lock-btn-one"></div>
                <div class="lock-btn-petal lock-btn-two"></div>
                <div class="lock-btn-petal lock-btn-three"></div>
                <div class="lock-btn-petal lock-btn-four"></div>
              </div>
              <div class="lock-btn-flower lock-btn-flower2">
                <div class="lock-btn-petal lock-btn-one"></div>
                <div class="lock-btn-petal lock-btn-two"></div>
                <div class="lock-btn-petal lock-btn-three"></div>
                <div class="lock-btn-petal lock-btn-four"></div>
              </div>
              <div class="lock-btn-flower lock-btn-flower3">
                <div class="lock-btn-petal lock-btn-one"></div>
                <div class="lock-btn-petal lock-btn-two"></div>
                <div class="lock-btn-petal lock-btn-three"></div>
                <div class="lock-btn-petal lock-btn-four"></div>
              </div>
              <div class="lock-btn-flower lock-btn-flower4">
                <div class="lock-btn-petal lock-btn-one"></div>
                <div class="lock-btn-petal lock-btn-two"></div>
                <div class="lock-btn-petal lock-btn-three"></div>
                <div class="lock-btn-petal lock-btn-four"></div>
              </div>
              <div class="lock-btn-flower lock-btn-flower5">
                <div class="lock-btn-petal lock-btn-one"></div>
                <div class="lock-btn-petal lock-btn-two"></div>
                <div class="lock-btn-petal lock-btn-three"></div>
                <div class="lock-btn-petal lock-btn-four"></div>
              </div>
              <div class="lock-btn-flower lock-btn-flower6">
                <div class="lock-btn-petal lock-btn-one"></div>
                <div class="lock-btn-petal lock-btn-two"></div>
                <div class="lock-btn-petal lock-btn-three"></div>
                <div class="lock-btn-petal lock-btn-four"></div>
              </div>
            </div>
          </button>
        </div>
      </div>
    </transition>

    <SpotifyPlayer v-if="!isAuthPage" />
  </div>

  <transition name="toast-slide">
    <div 
      v-if="notificationStore.dialog.show" 
      class="fixed inset-0 bg-black/40 z-[100] flex items-center justify-center p-4 select-none"
    >
      <div 
        class="w-full max-w-sm bg-white border border-slate-200 rounded-[30px] p-6 space-y-4 shadow-2xl animate-in zoom-in-95 duration-150"
      >
        <div class="flex items-center gap-3 pb-2 border-b border-slate-100">
          <div 
            class="p-2 rounded-full text-white flex items-center justify-center" 
            :class="notificationStore.dialog.type === 'confirm' ? 'bg-amber-500' : 'bg-[#8000ff]'"
          >
            <HelpCircle class="w-5 h-5" v-if="notificationStore.dialog.type === 'confirm'" />
            <Info class="w-5 h-5" v-else />
          </div>
          <h3 class="font-bold text-sm text-slate-900 uppercase tracking-wider">
            {{ notificationStore.dialog.title }}
          </h3>
        </div>

        <p class="text-xs text-slate-655 leading-relaxed py-2 font-medium">
          {{ notificationStore.dialog.message }}
        </p>

        <div class="flex justify-end gap-2 pt-2 border-t border-slate-100">
          <button 
            v-if="notificationStore.dialog.type === 'confirm'"
            @click="notificationStore.closeDialog(false)"
            class="btn-secondary px-4 py-1.5 text-xs font-bold"
          >
            Hủy bỏ
          </button>
          <button 
            @click="notificationStore.closeDialog(true)"
            class="btn-primary px-4 py-1.5 text-xs font-bold"
          >
            Xác nhận
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, markRaw } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from './stores/auth';
import { useNotificationStore } from './stores/notification';
import SpotifyPlayer from './components/SpotifyPlayer.vue';
import axios from 'axios';
import { getLunarDate } from '@dqcai/vn-lunar';
import { 
  Wallet, LayoutDashboard, History, ShieldAlert, 
  CalendarClock, LogOut, X, Sparkles, AlertOctagon,
  Clock, Sun, Cloud, CloudRain, CloudLightning, Info, HelpCircle, Lock, Bot,
  Calendar, ChevronLeft, ChevronRight, BarChart3
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const isDockHidden = ref(false);

const dockItems = [
  { path: '/', icon: markRaw(LayoutDashboard), label: 'Tổng quan' },
  { path: '/transactions', icon: markRaw(History), label: 'Nhật ký' },
  { path: '/budgets', icon: markRaw(ShieldAlert), label: 'Ngân sách' },
  { path: '/recurring', icon: markRaw(CalendarClock), label: 'Định kỳ' },
  { path: '/toxic-ai', icon: markRaw(Bot), label: 'Tâm sự với AI' },
  { path: '/yearly-summary', icon: markRaw(BarChart3), label: 'Tổng kết năm' },
];

const isAuthPage = computed(() => {
  const path = route.path;
  if (path === '/' && typeof window !== 'undefined') {
    const rawPath = window.location.pathname;
    if (rawPath === '/login' || rawPath === '/register') {
      return true;
    }
  }
  return path === '/login' || path === '/register';
});

const currentWindowTitle = computed(() => {
  const dictionary = {
    '/': 'AuraFinance - Tổng quan Hệ thống',
    '/transactions': 'AuraFinance - Nhật ký thu chi',
    '/budgets': 'AuraFinance - Kiểm soát hạn mức ngân sách',
    '/recurring': 'AuraFinance - Lịch trình giao dịch định kỳ',
    '/yearly-summary': 'AuraFinance - Tổng kết Năm',
  };
  return dictionary[route.path] || 'AuraFinance';
});

const userInitial = computed(() => {
  if (authStore.user?.fullname) {
    return authStore.user.fullname.trim().charAt(0).toUpperCase();
  }
  if (authStore.user?.email) {
    return authStore.user.email.trim().charAt(0).toUpperCase();
  }
  return 'A';
});

const isLocked = ref(false);
const lockScreenTime = ref('');
const lockScreenDate = ref('');

const unlock = () => {
  isLocked.value = false;
};

const currentTimeString = ref('');
const currentTimeStringMobile = ref('');
const updateClock = () => {
  const now = new Date();
  const days = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];
  const dayName = days[now.getDay()];
  const dateStr = now.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });
  const timeStr = now.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  currentTimeString.value = `${dayName} ${dateStr} - ${timeStr}`;
  
  // Mobile Clock: just HH:MM
  currentTimeStringMobile.value = now.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', hour12: false });
  
  // Lock Screen clock formats
  lockScreenTime.value = now.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', hour12: false });
  
  const weekday = now.toLocaleDateString('vi-VN', { weekday: 'long' });
  const day = now.getDate();
  const month = now.getMonth() + 1;
  const year = now.getFullYear();
  const capitalizedWeekday = weekday.charAt(0).toUpperCase() + weekday.slice(1);
  lockScreenDate.value = `${capitalizedWeekday}, ngày ${day < 10 ? '0' : ''}${day} tháng ${month < 10 ? '0' : ''}${month} năm ${year}`;
};

const weatherCode = ref(0);
const weatherText = ref('--°C');

const weatherIconComponent = computed(() => {
  const code = weatherCode.value;
  if (code === 0) return Sun;
  if (code >= 1 && code <= 3) return Cloud;
  if (code >= 51 && code <= 65) return CloudRain;
  if (code >= 80 && code <= 82) return CloudRain;
  if (code >= 95 && code <= 99) return CloudLightning;
  return Cloud;
});

const fetchWeather = async () => {
  const doFetch = async (lat, lon) => {
    try {
      const weatherApiUrl = import.meta.env.VITE_WEATHER_API_URL || 'https://api.open-meteo.com/v1/forecast';
      const res = await axios.get(`${weatherApiUrl}?latitude=${lat}&longitude=${lon}&current_weather=true`, { timeout: 5000 });
      if (res.data && res.data.current_weather) {
        weatherCode.value = res.data.current_weather.weathercode;
        const temp = Math.round(res.data.current_weather.temperature);
        weatherText.value = `${temp}°C`;
      }
    } catch (e) {
      weatherText.value = '31°C';
      weatherCode.value = 1;
    }
  };

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => doFetch(pos.coords.latitude, pos.coords.longitude),
      async () => {
        try {
          const ipapiUrl = import.meta.env.VITE_IPAPI_URL || 'https://ip-api.com/json/';
          const ipRes = await axios.get(ipapiUrl, { timeout: 5000 });
          const lat = ipRes.data.lat ?? ipRes.data.latitude;
          const lon = ipRes.data.lon ?? ipRes.data.longitude;
          await doFetch(lat, lon);
        } catch {
          const lat = import.meta.env.VITE_DEFAULT_LAT || '10.8231';
          const lng = import.meta.env.VITE_DEFAULT_LNG || '106.6297';
          await doFetch(lat, lng);
        }
      },
      { timeout: 5000 }
    );
  } else {
    const lat = import.meta.env.VITE_DEFAULT_LAT || '10.8231';
    const lng = import.meta.env.VITE_DEFAULT_LNG || '106.6297';
    await doFetch(lat, lng);
  }
};

const solarDateText = ref('');
const lunarDateText = ref('');
const showCalendarDropdown = ref(false);
const currentCalendarDate = ref(new Date());

const calendarMonthName = computed(() => {
  const months = [
    'Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6',
    'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'
  ];
  return `${months[currentCalendarDate.value.getMonth()]}, ${currentCalendarDate.value.getFullYear()}`;
});

const prevMonth = () => {
  const d = currentCalendarDate.value;
  currentCalendarDate.value = new Date(d.getFullYear(), d.getMonth() - 1, 1);
};

const nextMonth = () => {
  const d = currentCalendarDate.value;
  currentCalendarDate.value = new Date(d.getFullYear(), d.getMonth() + 1, 1);
};

const calendarWeeks = computed(() => {
  const date = currentCalendarDate.value;
  const year = date.getFullYear();
  const month = date.getMonth();
  
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  
  let startDay = firstDay.getDay() - 1;
  if (startDay < 0) startDay = 6;
  
  const totalDays = lastDay.getDate();
  const weeks = [];
  let currentWeek = Array(7).fill(null);
  
  const prevLastDay = new Date(year, month, 0).getDate();
  for (let i = 0; i < startDay; i++) {
    const dayVal = prevLastDay - startDay + 1 + i;
    const prevMonthIdx = month === 0 ? 11 : month - 1;
    const prevYearVal = month === 0 ? year - 1 : year;
    const lunar = getLunarDate(dayVal, prevMonthIdx + 1, prevYearVal);
    currentWeek[i] = {
      solarDay: dayVal,
      lunarDay: lunar.day === 1 ? `1/${lunar.month}` : lunar.day,
      isCurrentMonth: false,
      isToday: false,
    };
  }
  
  const today = new Date();
  let dayOfWeek = startDay;
  for (let day = 1; day <= totalDays; day++) {
    if (dayOfWeek === 7) {
      weeks.push(currentWeek);
      currentWeek = Array(7).fill(null);
      dayOfWeek = 0;
    }
    
    const lunar = getLunarDate(day, month + 1, year);
    const isToday = today.getDate() === day && today.getMonth() === month && today.getFullYear() === year;
    
    currentWeek[dayOfWeek] = {
      solarDay: day,
      lunarDay: lunar.day === 1 ? `1/${lunar.month}` : lunar.day,
      isCurrentMonth: true,
      isToday,
    };
    dayOfWeek++;
  }
  
  let nextMonthDay = 1;
  while (dayOfWeek < 7) {
    const nextMonthIdx = month === 11 ? 0 : month + 1;
    const nextYearVal = month === 11 ? year + 1 : year;
    const lunar = getLunarDate(nextMonthDay, nextMonthIdx + 1, nextYearVal);
    currentWeek[dayOfWeek] = {
      solarDay: nextMonthDay,
      lunarDay: lunar.day === 1 ? `1/${lunar.month}` : lunar.day,
      isCurrentMonth: false,
      isToday: false,
    };
    nextMonthDay++;
    dayOfWeek++;
  }
  weeks.push(currentWeek);
  return weeks;
});

const fetchLunarCalendar = () => {
  try {
    const today = new Date();
    const dd = today.getDate();
    const mm = today.getMonth() + 1;
    const yyyy = today.getFullYear();
    
    solarDateText.value = `${dd}/${mm}`;
    const lunar = getLunarDate(dd, mm, yyyy);
    if (lunar && lunar.day && lunar.month) {
      lunarDateText.value = `Âm: ${lunar.day}/${lunar.month}`;
    }
  } catch {
  }
};

const closeCalendarDropdown = () => {
  showCalendarDropdown.value = false;
};

const isActive = (path) => {
  return route.path === path;
};

const handleLogout = async () => {
  const confirmed = await notificationStore.showConfirm('Bạn có chắc chắn muốn đăng xuất khỏi hệ thống không?', 'Đăng xuất');
  if (confirmed) {
    notificationStore.disconnectWebSocket();
    isLocked.value = true; // Reset lock state on logout
    authStore.logout();
    router.push('/login');
  }
};

watch(() => authStore.isAuthenticated, (newVal) => {
  if (newVal) {
    notificationStore.connectWebSocket();
  } else {
    notificationStore.disconnectWebSocket();
  }
});

watch(isLocked, (newVal) => {
  sessionStorage.setItem('aura_session_locked', newVal ? 'true' : 'false');
});

let clockInterval = null;

onMounted(() => {
  if (authStore.isAuthenticated) {
    notificationStore.connectWebSocket();
  }
  
  const sessionLocked = sessionStorage.getItem('aura_session_locked');
  if (sessionLocked === 'true') {
    isLocked.value = true;
  } else if (sessionLocked === 'false') {
    isLocked.value = false;
  } else {
    if (sessionStorage.getItem('showLockScreen') === 'true') {
      isLocked.value = true;
      sessionStorage.removeItem('showLockScreen');
    }
  }

  updateClock();
  fetchWeather();
  fetchLunarCalendar();
  clockInterval = setInterval(updateClock, 1000);
  window.addEventListener('click', closeCalendarDropdown);
});

onUnmounted(() => {
  notificationStore.disconnectWebSocket();
  if (clockInterval) clearInterval(clockInterval);
  window.removeEventListener('click', closeCalendarDropdown);
});
</script>

<style>
.os-workspace {
  background: radial-gradient(circle at 15% 15%, rgba(128, 0, 255, 0.08) 0%, transparent 40%),
              radial-gradient(circle at 85% 85%, rgba(199, 210, 254, 0.12) 0%, transparent 45%),
              #f8fafc;
}

.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.drawer-slide-enter-from,
.drawer-slide-leave-to {
  transform: translateX(-100%);
}

.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-slide-enter-from {
  transform: translateY(20px);
  opacity: 0;
}

.toast-slide-leave-to {
  transform: translateY(20px);
  opacity: 0;
}

.lock-fade-enter-active,
.lock-fade-leave-active {
  transition: all 0.75s cubic-bezier(0.16, 1, 0.3, 1);
}

.lock-fade-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}

.lock-btn {
  height: 4em;
  width: 12em;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 0px solid black;
  cursor: pointer;
  outline: none !important;
}

.lock-btn-wrapper {
  height: 2em;
  width: 8em;
  position: relative;
  background: transparent;
  display: flex;
  justify-content: center;
  align-items: center;
}

.lock-btn-text {
  font-size: 11px;
  font-weight: 900;
  z-index: 1;
  color: #000;
  padding: 6px 16px;
  border-radius: 99px;
  background: rgba(255, 255, 255, 0.85);
  transition: all 0.5s ease;
  letter-spacing: 0.1em;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.lock-btn-flower {
  display: grid;
  grid-template-columns: 1em 1em;
  position: absolute;
  transition: grid-template-columns 0.8s ease;
}

.lock-btn-flower1 {
  top: -12px;
  left: -13px;
  transform: rotate(5deg);
}

.lock-btn-flower2 {
  bottom: -5px;
  left: 8px;
  transform: rotate(35deg);
}

.lock-btn-flower3 {
  bottom: -15px;
  transform: rotate(0deg);
}

.lock-btn-flower4 {
  top: -14px;
  transform: rotate(15deg);
}

.lock-btn-flower5 {
  right: 11px;
  top: -3px;
  transform: rotate(25deg);
}

.lock-btn-flower6 {
  right: -15px;
  bottom: -15px;
  transform: rotate(30deg);
}

.lock-btn-petal {
  height: 1em;
  width: 1em;
  border-radius: 40% 70% / 7% 90%;
  background: linear-gradient(#c084fc, #e879f9);
  border: 0.5px solid #d8b4fe;
  z-index: 0;
  transition: width 0.8s ease, height 0.8s ease;
}

.lock-btn-two {
  transform: rotate(90deg);
}

.lock-btn-three {
  transform: rotate(270deg);
}

.lock-btn-four {
  transform: rotate(180deg);
}

.lock-btn:hover .lock-btn-petal {
  background: linear-gradient(#8000ff, #c084fc);
  border: 0.5px solid #a855f7;
}

.lock-btn:hover .lock-btn-flower {
  grid-template-columns: 1.5em 1.5em;
}

.lock-btn:hover .lock-btn-flower .lock-btn-petal {
  width: 1.5em;
  height: 1.5em;
}

.lock-btn:hover .lock-btn-text {
  background: rgba(255, 255, 255, 0.4);
  color: #fff;
  text-shadow: 0 1px 3px rgba(0,0,0,0.5);
  box-shadow: 0 10px 25px rgba(128, 0, 255, 0.25);
  border: 1px solid rgba(128, 0, 255, 0.2);
}

.lock-btn:hover div.lock-btn-flower1 {
  animation: 15s linear 0s normal none infinite running lock-flower1;
}

@keyframes lock-flower1 {
  0% {
    transform: rotate(5deg);
  }
  100% {
    transform: rotate(365deg);
  }
}

.lock-btn:hover div.lock-btn-flower2 {
  animation: 13s linear 1s normal none infinite running lock-flower2;
}

@keyframes lock-flower2 {
  0% {
    transform: rotate(35deg);
  }
  100% {
    transform: rotate(-325deg);
  }
}

.lock-btn:hover div.lock-btn-flower3 {
  animation: 16s linear 1s normal none infinite running lock-flower3;
}

@keyframes lock-flower3 {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.lock-btn:hover div.lock-btn-flower4 {
  animation: 17s linear 1s normal none infinite running lock-flower4;
}

@keyframes lock-flower4 {
  0% {
    transform: rotate(15deg);
  }
  100% {
    transform: rotate(375deg);
  }
}

.lock-btn:hover div.lock-btn-flower5 {
  animation: 20s linear 1s normal none infinite running lock-flower5;
}

@keyframes lock-flower5 {
  0% {
    transform: rotate(25deg);
  }
  100% {
    transform: rotate(-335deg);
  }
}

.lock-btn:hover div.lock-btn-flower6 {
  animation: 15s linear 1s normal none infinite running lock-flower6;
}

@keyframes lock-flower6 {
  0% {
    transform: rotate(30deg);
  }
  100% {
    transform: rotate(390deg);
  }
}
</style>
