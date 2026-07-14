<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
        <Bot class="w-7 h-7 text-[#8000ff]" />
        <span>Tâm sự với AI</span>
      </h1>
      <p class="text-slate-500 text-xs mt-0.5">Trò chuyện cùng trợ lý AI thông minh của AuraFinance.</p>
    </div>

    <div class="glass-panel p-4 rounded-sm bg-white border border-slate-200">
      <div v-if="apiKeySaved && !showConfig" class="flex items-center justify-between gap-3 flex-wrap">
        <div class="flex items-center gap-2 text-xs">
          <div class="w-2 h-2 rounded-full bg-emerald-500 shrink-0"></div>
          <span class="font-bold text-slate-700">{{ currentProvider.name }}</span>
          <span class="text-slate-400">|</span>
          <span class="font-semibold text-slate-500">Model: {{ activeModel }}</span>
          <span class="text-slate-400">|</span>
          <span class="font-mono text-slate-500">{{ maskedKey }}</span>
        </div>
        <button 
          @click="showConfig = true"
          class="text-[11px] text-[#8000ff] hover:underline font-bold cursor-pointer"
        >
          Đổi Key / Nhà cung cấp
        </button>
      </div>

      <div v-else class="space-y-3">
        <div class="grid grid-cols-1 sm:grid-cols-12 gap-3 items-center">
          <div class="sm:col-span-4">
            <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider block mb-1">Nhà cung cấp</label>
            <select 
              v-model="provider"
              @change="onProviderChange"
              class="w-full text-xs font-bold h-[38px] bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:border-[#8000ff] transition cursor-pointer"
            >
              <option v-for="p in providers" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
          </div>

          <div class="sm:col-span-8">
            <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider block mb-1">API Key</label>
            <div class="relative">
              <input 
                v-model="apiKey"
                :type="showKey ? 'text' : 'password'"
                :placeholder="currentProvider.placeholder"
                class="w-full text-xs font-mono font-bold pr-8 h-[38px] bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:border-[#8000ff] transition"
              />
              <button 
                @click="showKey = !showKey"
                class="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-655 cursor-pointer"
              >
                <EyeOff v-if="showKey" class="w-3.5 h-3.5" />
                <Eye v-else class="w-3.5 h-3.5" />
              </button>
            </div>
            <p class="text-[9px] text-amber-600 font-semibold mt-1 px-1">
              API Key được lưu trong trình duyệt và có thể bị đánh cắp nếu trang bị tấn công XSS. Không chia sẻ key cho người khác.
            </p>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-12 gap-3 items-center pt-1">
          <div :class="selectedModel === 'custom' ? 'sm:col-span-4' : 'sm:col-span-7'">
            <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider block mb-1">Phiên bản Model</label>
            <select 
              v-model="selectedModel"
              class="w-full text-xs font-bold h-[38px] bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:border-[#8000ff] transition cursor-pointer"
            >
              <option v-for="m in currentProvider.models" :key="m.value" :value="m.value">{{ m.label }}</option>
            </select>
          </div>

          <div v-if="selectedModel === 'custom'" class="sm:col-span-3">
            <label class="text-[10px] text-slate-400 font-bold uppercase tracking-wider block mb-1">Tên Model tùy chỉnh</label>
            <input 
              v-model="customModel"
              type="text"
              placeholder="Nhập code model..."
              class="w-full text-xs font-bold h-[38px] bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:border-[#8000ff] transition"
            />
          </div>

          <div class="sm:col-span-5 flex items-center justify-end gap-3 pt-4 sm:pt-0 ml-auto">
            <a :href="currentProvider.link" target="_blank" class="text-[10px] text-[#8000ff] hover:underline font-bold whitespace-nowrap">Lấy Key miễn phí →</a>
            <button 
              @click="saveKey"
              class="btn-primary text-xs font-bold px-4 py-2 cursor-pointer h-[38px]"
            >
              Lưu cấu hình
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="glass-panel rounded-sm bg-white flex flex-col" style="min-height: calc(100vh - 300px);">
      <div ref="chatContainer" class="flex-1 overflow-y-auto p-5 space-y-4">
        <div v-if="messages.length === 0 && !loading" class="h-full flex flex-col items-center justify-center text-center text-slate-400 space-y-3 py-16">
          <div class="w-16 h-16 rounded-full bg-purple-50 flex items-center justify-center border border-purple-100 text-[#8000ff]">
            <Bot class="w-8 h-8" />
          </div>
          <div class="space-y-1">
            <p class="text-sm font-bold text-slate-600">Xin chào!</p>
            <p class="text-xs max-w-sm leading-normal" v-if="apiKeySaved">
              Hãy kể cho mình nghe bất kỳ điều gì bạn muốn chia sẻ nhé.
            </p>
            <p class="text-xs max-w-sm leading-normal" v-else>
              Vui lòng nhập và lưu API Key ở phía trên để bắt đầu trò chuyện.
            </p>
          </div>
        </div>

        <template v-for="(msg, idx) in displayedMessages" :key="idx">
          <div v-if="msg.role === 'user'" class="flex justify-end">
            <div class="max-w-[75%] bg-[#8000ff] text-white px-4 py-2.5 rounded-2xl rounded-br-md shadow-sm">
              <p class="text-xs font-semibold leading-relaxed whitespace-pre-wrap">{{ msg.text }}</p>
            </div>
          </div>

          <div v-else class="flex items-start gap-3">
            <div class="w-8 h-8 rounded-full bg-purple-100 border border-purple-200 flex items-center justify-center shrink-0">
              <Bot class="w-4 h-4 text-[#8000ff]" />
            </div>
            <div class="max-w-[75%] bg-slate-50 border border-slate-100 px-4 py-2.5 rounded-2xl rounded-bl-md shadow-sm">
              <p class="text-xs font-semibold text-slate-700 leading-relaxed whitespace-pre-wrap">{{ msg.text }}</p>
            </div>
          </div>
        </template>

        <div v-if="loading" class="flex items-start gap-3">
          <div class="w-8 h-8 rounded-full bg-purple-100 border border-purple-200 flex items-center justify-center shrink-0 animate-pulse">
            <Bot class="w-4 h-4 text-[#8000ff]" />
          </div>
          <div class="bg-slate-50 border border-slate-100 px-4 py-3 rounded-2xl rounded-bl-md shadow-sm">
            <div class="flex items-center gap-1.5">
              <div class="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
              <div class="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
              <div class="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="border-t border-slate-100 p-4">
        <form @submit.prevent="sendMessage" class="flex items-center gap-3">
          <input 
            v-model="userInput"
            type="text"
            placeholder="Nhập tin nhắn..."
            class="flex-1 text-xs font-semibold h-[38px] bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 focus:outline-none focus:border-[#8000ff] transition"
            :disabled="!apiKeySaved || loading"
          />
          <button 
            type="submit"
            :disabled="!apiKeySaved || !userInput.trim() || loading"
            class="btn-primary text-xs font-bold shrink-0 cursor-pointer flex items-center gap-1.5 disabled:opacity-50"
          >
            <Send class="w-3.5 h-3.5" />
            <span>Gửi</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import axios from 'axios';
import { useNotificationStore } from '../stores/notification';
import { useAuthStore } from '../stores/auth';
import { Bot, Eye, EyeOff, Send } from 'lucide-vue-next';

const notificationStore = useNotificationStore();
const authStore = useAuthStore();

const storagePrefix = computed(() => {
  const email = authStore.user?.email || 'guest';
  return `aura_${email}_`;
});

const providers = [
  { 
    id: 'gemini', 
    name: 'Google Gemini', 
    placeholder: 'AIzaSy...', 
    link: 'https://aistudio.google.com/apikey',
    defaultModel: 'gemini-2.0-flash',
    models: [
      { value: 'gemini-2.0-flash', label: 'gemini-2.0-flash (Mặc định)' },
      { value: 'gemini-2.5-flash', label: 'gemini-2.5-flash (Mới)' },
      { value: 'gemini-2.5-pro', label: 'gemini-2.5-pro' },
      { value: 'gemini-1.5-flash', label: 'gemini-1.5-flash' },
      { value: 'custom', label: 'Nhập model khác...' }
    ]
  },
  { 
    id: 'openai', 
    name: 'OpenAI (ChatGPT)', 
    placeholder: 'sk-...', 
    link: 'https://platform.openai.com/api-keys',
    defaultModel: 'gpt-4o-mini',
    models: [
      { value: 'gpt-4o-mini', label: 'gpt-4o-mini (Mặc định)' },
      { value: 'gpt-4o', label: 'gpt-4o' },
      { value: 'o3-mini', label: 'o3-mini' },
      { value: 'custom', label: 'Nhập model khác...' }
    ]
  },
  { 
    id: 'groq', 
    name: 'Groq (Llama)', 
    placeholder: 'gsk_...', 
    link: 'https://console.groq.com/keys',
    defaultModel: 'llama-3.3-70b-versatile',
    models: [
      { value: 'llama-3.3-70b-versatile', label: 'llama-3.3-70b-versatile (Mặc định)' },
      { value: 'llama-3.1-8b-instant', label: 'llama-3.1-8b-instant' },
      { value: 'mixtral-8x7b-32768', label: 'mixtral-8x7b-32768' },
      { value: 'custom', label: 'Nhập model khác...' }
    ]
  },
  { 
    id: 'openrouter', 
    name: 'OpenRouter', 
    placeholder: 'sk-or-...', 
    link: 'https://openrouter.ai/keys',
    defaultModel: 'google/gemini-2.5-flash:free',
    models: [
      { value: 'google/gemini-2.5-flash:free', label: 'gemini-2.5-flash:free (Mặc định)' },
      { value: 'google/gemini-2.0-flash-exp:free', label: 'gemini-2.0-flash-exp:free' },
      { value: 'meta-llama/llama-3.3-70b-instruct:free', label: 'llama-3.3-70b-instruct:free' },
      { value: 'deepseek/deepseek-r1:free', label: 'deepseek-r1:free' },
      { value: 'custom', label: 'Nhập model khác...' }
    ]
  },
  { 
    id: 'deepseek', 
    name: 'DeepSeek', 
    placeholder: 'sk-...', 
    link: 'https://platform.deepseek.com/api_keys',
    defaultModel: 'deepseek-chat',
    models: [
      { value: 'deepseek-chat', label: 'deepseek-chat (Mặc định)' },
      { value: 'deepseek-reasoner', label: 'deepseek-reasoner (R1)' },
      { value: 'custom', label: 'Nhập model khác...' }
    ]
  },
  { 
    id: 'claude', 
    name: 'Claude (Anthropic)', 
    placeholder: 'sk-ant-...', 
    link: 'https://console.anthropic.com/settings/keys',
    defaultModel: 'claude-3-7-sonnet-latest',
    models: [
      { value: 'claude-3-7-sonnet-latest', label: 'claude-3-7-sonnet-latest (Mới nhất)' },
      { value: 'claude-3-5-sonnet-latest', label: 'claude-3-5-sonnet-latest' },
      { value: 'claude-3-5-haiku-latest', label: 'claude-3-5-haiku-latest' },
      { value: 'custom', label: 'Nhập model khác...' }
    ]
  },
];

const provider = ref('gemini');
const apiKey = ref('');
const apiKeySaved = ref(false);
const showKey = ref(false);
const showConfig = ref(false);

const selectedModel = ref('gemini-2.0-flash');
const customModel = ref('');

const activeModel = computed(() => {
  return selectedModel.value === 'custom' ? customModel.value : selectedModel.value;
});

const userInput = ref('');
const messages = ref([]);
const displayedMessages = computed(() => {
  return messages.value.slice(-60);
});
const loading = ref(false);
const chatContainer = ref(null);

const currentProvider = computed(() => {
  return providers.find(p => p.id === provider.value) || providers[0];
});

const maskedKey = computed(() => {
  const k = apiKey.value;
  if (!k || k.length < 8) return '****';
  return k.substring(0, 6) + '...' + k.substring(k.length - 4);
});

const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

const onProviderChange = () => {
  const savedKey = localStorage.getItem(`${storagePrefix.value}ai_key_${provider.value}`);
  apiKey.value = savedKey || '';
  apiKeySaved.value = !!savedKey;

  const savedModel = localStorage.getItem(`${storagePrefix.value}ai_model_${provider.value}`);
  if (savedModel) {
    const isStandard = currentProvider.value.models.some(m => m.value === savedModel);
    if (isStandard && savedModel !== 'custom') {
      selectedModel.value = savedModel;
      customModel.value = '';
    } else {
      selectedModel.value = 'custom';
      customModel.value = savedModel;
    }
  } else {
    selectedModel.value = currentProvider.value.defaultModel;
    customModel.value = '';
  }
};

const saveKey = () => {
  if (!apiKey.value.trim()) {
    notificationStore.showAlert('Vui lòng nhập API Key hợp lệ!', 'Cảnh báo');
    return;
  }
  sessionStorage.setItem(`${storagePrefix.value}ai_key_${provider.value}`, apiKey.value.trim());
  sessionStorage.setItem(`${storagePrefix.value}ai_provider`, provider.value);
  sessionStorage.setItem(`${storagePrefix.value}ai_model_${provider.value}`, activeModel.value);
  apiKeySaved.value = true;
  showConfig.value = false;
  notificationStore.showAlert(`Đã lưu API Key và cấu hình Model cho ${currentProvider.value.name} thành công!`, 'Thành công');
};

const loadKey = () => {
  const savedProvider = sessionStorage.getItem(`${storagePrefix.value}ai_provider`);
  if (savedProvider) {
    provider.value = savedProvider;
  }
  const savedKey = sessionStorage.getItem(`${storagePrefix.value}ai_key_${provider.value}`);
  if (savedKey) {
    apiKey.value = savedKey;
    apiKeySaved.value = true;
  }
  const savedModel = sessionStorage.getItem(`${storagePrefix.value}ai_model_${provider.value}`);
  if (savedModel) {
    const isStandard = currentProvider.value.models.some(m => m.value === savedModel);
    if (isStandard && savedModel !== 'custom') {
      selectedModel.value = savedModel;
      customModel.value = '';
    } else {
      selectedModel.value = 'custom';
      customModel.value = savedModel;
    }
  } else {
    selectedModel.value = currentProvider.value.defaultModel;
    customModel.value = '';
  }
};

const systemPrompt = `Bạn là một trợ lý ảo tên là "Aura AI" thuộc hệ thống quản lý tài chính AuraFinance.
Bạn có tính cách siêu châm biếm, hài hước, đanh đá và nghịch ngợm.
Người dùng sẽ gửi tin nhắn chia sẻ câu chuyện chi tiêu, sinh hoạt hoặc cuộc sống.
Nhiệm vụ của bạn là trả lời bằng giọng điệu châm chọc xéo sắc, sử dụng ngôn từ giới trẻ Việt Nam hài hước nhưng cực thấm (ví dụ: chê họ "phế", "ngố", "quá khờ", "tổng tài phá của", "vua chốt đơn", "tấm chiếu mới", "não cá vàng"...).
Giọng điệu phải đùa vui châm biếm chứ không thô tục hay xúc phạm nặng nề. Luôn trả lời bằng tiếng Việt.
Nếu người dùng hỏi các chủ đề ngoài tài chính, vẫn trả lời bình thường nhưng giữ giọng hài hước, dí dỏm.`;

const callGemini = async (key, history) => {
  const contents = history.map(msg => ({
    role: msg.role === 'user' ? 'user' : 'model',
    parts: [{ text: msg.text }]
  }));

  const res = await axios.post(
    `https://generativelanguage.googleapis.com/v1beta/models/${activeModel.value}:generateContent?key=${key}`,
    {
      contents,
      systemInstruction: { parts: [{ text: systemPrompt }] }
    }
  );

  return res.data?.candidates?.[0]?.content?.parts?.[0]?.text?.trim() || null;
};

const callOpenAICompatible = async (key, history, baseUrl) => {
  const chatMessages = [
    { role: 'system', content: systemPrompt },
    ...history.map(msg => ({
      role: msg.role === 'user' ? 'user' : 'assistant',
      content: msg.text
    }))
  ];

  const headers = {
    'Authorization': `Bearer ${key}`,
    'Content-Type': 'application/json'
  };

  // OpenRouter requires extra headers
  if (provider.value === 'openrouter') {
    headers['HTTP-Referer'] = window.location.origin;
    headers['X-Title'] = 'AuraFinance';
  }

  const res = await axios.post(
    `${baseUrl}/chat/completions`,
    {
      model: activeModel.value,
      messages: chatMessages,
    },
    { headers }
  );

  return res.data?.choices?.[0]?.message?.content?.trim() || null;
};

const callClaude = async (key, history) => {
  const chatMessages = history.map(msg => ({
    role: msg.role === 'user' ? 'user' : 'assistant',
    content: msg.text
  }));

  const res = await axios.post(
    'https://api.anthropic.com/v1/messages',
    {
      model: activeModel.value,
      max_tokens: 1024,
      system: systemPrompt,
      messages: chatMessages,
    },
    {
      headers: {
        'x-api-key': key,
        'anthropic-version': '2023-06-01',
        'anthropic-dangerous-direct-browser-access': 'true',
        'Content-Type': 'application/json'
      }
    }
  );

  return res.data?.content?.[0]?.text?.trim() || null;
};

const parseError = (err, provName) => {
  const status = err.response?.status;
  const rawMsg = err.response?.data?.error?.message || err.response?.data?.error?.err?.message || err.message || '';
  
  let friendlyMsg = 'Không thể kết nối đến máy chủ AI. Vui lòng kiểm tra lại kết nối mạng của bạn.';

  if (status === 401 || status === 403 || rawMsg.includes('API key not valid') || rawMsg.includes('invalid_api_key') || rawMsg.includes('API_KEY_INVALID')) {
    friendlyMsg = `API Key của ${provName} không hợp lệ hoặc đã hết hạn. Vui lòng kiểm tra và cấu hình lại Key chính xác.`;
  } else if (status === 429 || rawMsg.includes('quota') || rawMsg.includes('Quota exceeded') || rawMsg.includes('rate_limit') || rawMsg.includes('insufficient_quota')) {
    friendlyMsg = `Tài khoản ${provName} của bạn đã hết hạn mức sử dụng (Quota) hoặc vượt quá giới hạn lượt gọi mỗi phút (Rate Limit). Vui lòng thử lại sau vài giây hoặc đổi nhà cung cấp khác.`;
  } else if (rawMsg.includes('model_not_found') || rawMsg.includes('not found') || status === 404) {
    friendlyMsg = `Phiên bản Model bạn chọn không được hỗ trợ bởi ${provName}. Hãy thử đổi sang phiên bản mặc định khác trong danh sách.`;
  } else if (rawMsg.includes('safety') || rawMsg.includes('SAFETY') || rawMsg.includes('blocked')) {
    friendlyMsg = 'Yêu cầu bị từ chối do vi phạm quy tắc an toàn hoặc bộ lọc nội dung của nhà cung cấp AI.';
  } else if (rawMsg) {
    friendlyMsg = `Lỗi từ ${provName}: ${rawMsg.length > 150 ? rawMsg.substring(0, 150) + '...' : rawMsg}`;
  }

  return friendlyMsg;
};

const sendMessage = async () => {
  const text = userInput.value.trim();
  if (!text || !apiKey.value.trim()) return;

  messages.value.push({ role: 'user', text });
  userInput.value = '';
  scrollToBottom();

  loading.value = true;

  try {
    const key = apiKey.value.trim();
    let aiText = null;

    switch (provider.value) {
      case 'gemini':
        aiText = await callGemini(key, messages.value);
        break;
      case 'openai':
        aiText = await callOpenAICompatible(key, messages.value, 'https://api.openai.com/v1');
        break;
      case 'groq':
        aiText = await callOpenAICompatible(key, messages.value, 'https://api.groq.com/openai/v1');
        break;
      case 'openrouter':
        aiText = await callOpenAICompatible(key, messages.value, 'https://openrouter.ai/api/v1');
        break;
      case 'deepseek':
        aiText = await callOpenAICompatible(key, messages.value, 'https://api.deepseek.com');
        break;
      case 'claude':
        aiText = await callClaude(key, messages.value);
        break;
    }

    messages.value.push({ role: 'ai', text: aiText || 'Hmm, mình không hiểu lắm. Thử kể lại rõ hơn xem nào.' });
  } catch (err) {
    const friendlyError = parseError(err, currentProvider.value.name);
    notificationStore.showAlert(friendlyError, 'Lỗi kết nối AI');
    messages.value.push({ role: 'ai', text: 'Kết nối thất bại. Hãy kiểm tra lại API Key hoặc đổi nhà cung cấp nhé.' });
  } finally {
    loading.value = false;
    scrollToBottom();
  }
};

onMounted(() => {
  loadKey();
});
</script>
