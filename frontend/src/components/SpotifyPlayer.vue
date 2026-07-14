<template>
  <div 
    ref="playerContainer"
    class="fixed z-50 select-none animate-in fade-in duration-200"
    :style="containerStyle"
    @mousedown="initDrag"
    @touchstart="initDrag"
  >
    <!-- Collapsed State: A gorgeous floating music button -->
    <div 
      v-if="isCollapsed"
      @click.stop="handleCircleClick"
      class="w-14 h-14 bg-white border-2 border-purple-200 text-[#8000ff] shadow-2xl flex items-center justify-center rounded-full hover:scale-110 active:scale-95 transition-all cursor-pointer relative group"
    >
      <!-- Equalizer animation when playing -->
      <div v-if="isPlaying && playlist.length > 0" class="playing scale-75">
        <div class="purpleline line-1"></div>
        <div class="purpleline line-2"></div>
        <div class="purpleline line-3"></div>
        <div class="purpleline line-4"></div>
      </div>
      <Music v-else class="w-6 h-6 animate-pulse" />
      
      <!-- Hover Tooltip -->
      <span class="absolute right-16 top-1/2 -translate-y-1/2 bg-slate-900 text-white text-[10px] px-2.5 py-1 rounded-md opacity-0 group-hover:opacity-100 transition duration-150 whitespace-nowrap pointer-events-none font-bold shadow-lg">
        {{ playlist.length > 0 ? (isPlaying ? 'Đang phát nhạc' : 'Nhấp để mở nhạc') : 'Chưa có nhạc - Nhấp để thêm' }}
      </span>
    </div>

    <!-- Expanded State: The redesigned Spotify-style Glass Player (LIGHT THEME) -->
    <div 
      v-else
      class="w-72 bg-white backdrop-blur-md text-slate-800 border-2 border-slate-200/90 shadow-2xl rounded-[24px] p-4 flex flex-col justify-between relative transition-all duration-200"
      @mousedown.stop
      @touchstart.stop
    >
      <!-- Drag handle header -->
      <div 
        class="h-6 w-full cursor-move absolute top-0 left-0 rounded-t-[24px] flex items-center justify-center text-[9px] text-slate-400 font-bold tracking-wider"
        @mousedown="initDrag"
        @touchstart="initDrag"
      >
        ••• KÉO ĐỂ DI CHUYỂN •••
      </div>

      <!-- Import form overlay (inside card - SOLID bg-white to hide elements underneath) -->
      <div 
        v-if="showImportForm" 
        class="absolute inset-0 bg-white rounded-[24px] p-4 flex flex-col justify-between z-20 border border-slate-200 animate-in fade-in zoom-in-95 duration-150"
        @mousedown.stop
        @touchstart.stop
      >
        <div class="space-y-3">
          <div class="flex justify-between items-center pb-1 border-b border-slate-200">
            <h4 class="text-xs font-bold text-[#8000ff] uppercase tracking-wider">Thêm nhạc mới</h4>
            <button 
              @click.stop="showImportForm = false" 
              @mousedown.stop 
              @touchstart.stop
              class="text-slate-400 hover:text-slate-800 transition cursor-pointer p-1"
            >
              <X class="w-4 h-4" />
            </button>
          </div>
          
          <div class="space-y-2.5 text-left text-slate-700">
            <!-- Tabs to choose between File Upload and URL -->
            <div class="flex gap-2 border-b border-slate-100 pb-1.5">
              <button 
                @click.stop="importMode = 'file'"
                @mousedown.stop @touchstart.stop
                class="text-[10px] font-bold px-2 py-0.5 rounded-sm transition cursor-pointer"
                :class="importMode === 'file' ? 'bg-purple-50 text-[#8000ff]' : 'text-slate-400 hover:text-slate-600'"
              >
                Tải file nhạc
              </button>
              <button 
                @click.stop="importMode = 'url'"
                @mousedown.stop @touchstart.stop
                class="text-[10px] font-bold px-2 py-0.5 rounded-sm transition cursor-pointer"
                :class="importMode === 'url' ? 'bg-purple-50 text-[#8000ff]' : 'text-slate-400 hover:text-slate-600'"
              >
                Nhập link URL
              </button>
            </div>

            <!-- Mode 1: File Upload Selector -->
            <div v-if="importMode === 'file'" class="space-y-2">
              <label class="block text-[10px] text-slate-500 font-bold">Chọn file nhạc từ thiết bị của bạn:</label>
              <input 
                type="file" 
                accept="audio/*" 
                @change="handleFileChange"
                @mousedown.stop
                @touchstart.stop
                class="w-full text-slate-800 text-[11px] file:mr-2 file:py-1 file:px-3 file:rounded-full file:border-0 file:text-[10px] file:font-semibold file:bg-purple-100 file:text-purple-700 hover:file:bg-purple-200 cursor-pointer"
              />
              <!-- Optional metadata fields for file -->
              <input 
                v-model="importForm.title" 
                type="text" 
                placeholder="Tên bài hát (tự động điền theo file)..." 
                @mousedown.stop @touchstart.stop
                class="w-full bg-slate-50 border border-slate-200 text-[11px] px-3 py-1 rounded-full text-slate-800 focus:outline-none focus:border-purple-500 focus:bg-white"
              />
              <input 
                v-model="importForm.artist" 
                type="text" 
                placeholder="Tên ca sĩ / Tác giả..." 
                @mousedown.stop @touchstart.stop
                class="w-full bg-slate-50 border border-slate-200 text-[11px] px-3 py-1 rounded-full text-slate-800 focus:outline-none focus:border-purple-500 focus:bg-white"
              />
            </div>

            <!-- Mode 2: Link URL input -->
            <div v-else class="space-y-2">
              <input 
                v-model="importForm.title" 
                type="text" 
                placeholder="Tên bài hát..." 
                @mousedown.stop @touchstart.stop
                class="w-full bg-slate-50 border border-slate-200 text-[11px] px-3 py-1.5 rounded-full text-slate-800 focus:outline-none focus:border-purple-500 focus:bg-white"
              />
              <input 
                v-model="importForm.artist" 
                type="text" 
                placeholder="Ca sĩ / Tác giả..." 
                @mousedown.stop @touchstart.stop
                class="w-full bg-slate-50 border border-slate-200 text-[11px] px-3 py-1.5 rounded-full text-slate-800 focus:outline-none focus:border-purple-500 focus:bg-white"
              />
              <input 
                v-model="importForm.url" 
                type="text" 
                placeholder="Link MP3 trực tiếp (.mp3 / .wav / .ogg)..." 
                @mousedown.stop @touchstart.stop
                class="w-full bg-slate-50 border border-slate-200 text-[11px] px-3 py-1.5 rounded-full text-slate-800 focus:outline-none focus:border-purple-500 focus:bg-white"
              />
              <p class="text-[9px] text-amber-600 font-semibold px-1">
                ⚠️ Chỉ hỗ trợ link âm thanh trực tiếp (.mp3, .wav, .ogg...). Link YouTube, Spotify, SoundCloud không phát được.
              </p>
            </div>
          </div>
        </div>
        <button 
          @click.stop="submitImport" 
          @mousedown.stop
          @touchstart.stop
          class="w-full bg-[#8000ff] hover:bg-purple-700 text-white text-xs font-bold py-1.5 rounded-full transition active:scale-95 cursor-pointer mt-2"
        >
          Thêm vào danh sách
        </button>
      </div>

      <!-- Case 1: Empty Playlist Placeholder (As requested: "chưa có bài nào thì báo là chưa có hãy thêm để nghe") -->
      <div 
        v-if="playlist.length === 0" 
        class="flex flex-col items-center justify-center py-6 text-center space-y-3 mt-3 w-full"
      >
        <div class="w-12 h-12 bg-purple-50 rounded-full flex items-center justify-center text-[#8000ff]">
          <Music class="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <p class="text-xs font-bold text-slate-800">Chưa có bài hát nào</p>
          <p class="text-[10px] text-slate-400 mt-1 max-w-[200px]">Hãy thêm hoặc tải lên file nhạc từ máy tính của bạn để bắt đầu nghe nhạc!</p>
        </div>
        <div class="flex gap-2">
          <button 
            @click.stop="showImportForm = true"
            @mousedown.stop @touchstart.stop
            class="px-4 py-1.5 bg-[#8000ff] hover:bg-purple-700 text-white text-[11px] font-bold rounded-full transition active:scale-95 cursor-pointer"
          >
            Thêm nhạc ngay
          </button>
          
          <button 
            @click.stop="toggleCollapse"
            @mousedown.stop @touchstart.stop
            class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-600 text-[11px] font-bold rounded-full transition active:scale-95 cursor-pointer"
          >
            Đóng
          </button>
        </div>
      </div>

      <!-- Case 2: Player with playlist tracks loaded -->
      <div v-else class="w-full flex flex-col justify-between h-full">
        <!-- Main player contents -->
        <div class="top mt-3 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <!-- Album thumbnail wrapper -->
            <div class="pfp shadow-sm">
              <!-- Animated equalizer when playing -->
              <div class="playing scale-90">
                <div class="purpleline line-1" :class="{ 'paused': !isPlaying }"></div>
                <div class="purpleline line-2" :class="{ 'paused': !isPlaying }"></div>
                <div class="purpleline line-3" :class="{ 'paused': !isPlaying }"></div>
                <div class="purpleline line-4" :class="{ 'paused': !isPlaying }"></div>
                <div class="purpleline line-5" :class="{ 'paused': !isPlaying }"></div>
              </div>
            </div>
            <!-- Track Titles -->
            <div class="texts overflow-hidden max-w-[130px]">
              <p class="title-1 truncate text-sm font-bold text-slate-900" :title="currentTrack.title">{{ currentTrack.title }}</p>
              <p class="title-2 truncate text-[10px] text-slate-500 font-semibold" :title="currentTrack.artist">{{ currentTrack.artist }}</p>
            </div>
          </div>

          <div class="flex gap-2">
            <!-- Import button -->
            <button 
              @click.stop="showImportForm = true" 
              @mousedown.stop
              @touchstart.stop
              class="p-1.5 rounded-full bg-slate-100 hover:bg-purple-50 hover:text-purple-600 border border-slate-200 transition cursor-pointer"
              title="Thêm nhạc khác"
            >
              <Plus class="w-3.5 h-3.5" />
            </button>
            
            <!-- Collapse button -->
            <button 
              @click.stop="toggleCollapse" 
              @mousedown.stop
              @touchstart.stop
              class="p-1.5 rounded-full bg-slate-100 hover:bg-slate-200 border border-slate-200 transition cursor-pointer"
              title="Thu nhỏ"
            >
              <Minus class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        <!-- Controls area -->
        <div class="controls-container flex flex-col items-center mt-3.5 gap-2">
          <div class="flex items-center justify-center gap-4">
            <!-- Previous Track button -->
            <button 
              @click.stop="prevTrack" 
              @mousedown.stop
              @touchstart.stop
              class="text-slate-500 hover:text-purple-600 transition active:scale-90 cursor-pointer p-1"
            >
              <SkipBack class="w-4 h-4 fill-currentColor" />
            </button>

            <!-- Play / Pause button -->
            <button 
              @click.stop="togglePlay" 
              @mousedown.stop
              @touchstart.stop
              class="p-2 bg-[#8000ff] rounded-full text-white hover:bg-purple-700 hover:scale-105 transition active:scale-95 cursor-pointer shadow-lg shadow-purple-600/20"
            >
              <Pause class="w-5 h-5 fill-currentColor" v-if="isPlaying" />
              <Play class="w-5 h-5 fill-currentColor ml-0.5" v-else />
            </button>

            <!-- Next Track button -->
            <button 
              @click.stop="nextTrack" 
              @mousedown.stop
              @touchstart.stop
              class="text-slate-500 hover:text-purple-600 transition active:scale-90 cursor-pointer p-1"
            >
              <SkipForward class="w-4 h-4 fill-currentColor" />
            </button>
          </div>

          <!-- Volume Slider bar -->
          <div class="volume-container flex items-center gap-1.5 w-full justify-center text-slate-500 hover:text-slate-800 transition">
            <Volume2 class="w-3.5 h-3.5" />
            <input 
              v-model="volume" 
              type="range" 
              min="0" 
              max="1" 
              step="0.05" 
              @input="adjustVolume"
              @mousedown.stop
              @touchstart.stop
              class="w-24 h-1 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
          </div>
        </div>

        <!-- Progress timeline -->
        <div class="mt-3.5">
          <div 
            class="time-bar bg-slate-100 border border-slate-200/50 h-1.5 rounded-full relative cursor-pointer"
            @click="seekProgress"
            @mousedown.stop
            @touchstart.stop
            ref="progressBar"
          >
            <div 
              class="elapsed-bar bg-purple-600 h-full rounded-full transition-all duration-75 relative"
              :style="{ width: progressPercentage + '%' }"
            >
              <div class="w-2.5 h-2.5 bg-white rounded-full absolute right-0 top-1/2 -translate-y-1/2 shadow-md hidden group-hover:block"></div>
            </div>
          </div>

          <!-- Time texts -->
          <div class="flex justify-between text-[8px] text-slate-500 font-mono font-bold mt-1.5">
            <span>{{ formatTime(currentTime) }}</span>
            <span>{{ formatTime(duration) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Hidden HTML5 Audio Element - only set src when there is a valid track -->
    <audio 
      ref="audioElement"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoadedMetadata"
      @ended="nextTrack"
      @error="onAudioError"
    ></audio>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue';
import { 
  Music, Play, Pause, SkipForward, SkipBack, 
  Volume2, Plus, X, Minus 
} from 'lucide-vue-next';
import { useNotificationStore } from '../stores/notification';

const notificationStore = useNotificationStore();

const isCollapsed = ref(true);

const position = reactive({
  x: window.innerWidth - 80,
  y: window.innerHeight - 150
});
const containerStyle = computed(() => ({
  left: `${position.x}px`,
  top: `${position.y}px`,
}));

watch(isCollapsed, (newVal) => {
  if (!newVal) {
    if (position.x + 300 > window.innerWidth) {
      position.x = Math.max(10, window.innerWidth - 300);
    }
    if (position.y + 200 > window.innerHeight) {
      position.y = Math.max(10, window.innerHeight - 200);
    }
  } else {
    if (position.x > window.innerWidth - 80) {
      position.x = window.innerWidth - 80;
    }
    if (position.y > window.innerHeight - 150) {
      position.y = window.innerHeight - 150;
    }
  }
});

const playlist = ref([]);
const currentTrackIndex = ref(0);
const currentTrack = computed(() => {
  if (playlist.value.length === 0) return null;
  return playlist.value[currentTrackIndex.value];
});

const isPlaying = ref(false);
const currentTime = ref(0);
const duration = ref(0);
const volume = ref(0.7);

const audioElement = ref(null);
const progressBar = ref(null);
const playerContainer = ref(null);

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
};

const togglePlay = () => {
  if (playlist.value.length === 0) return;
  if (isPlaying.value) {
    audioElement.value.pause();
    isPlaying.value = false;
  } else {
    isPlaying.value = true;
    audioElement.value.play().catch(() => {
      isPlaying.value = false;
    });
  }
};

const playTrack = () => {
  if (playlist.value.length === 0) return;
  if (!audioElement.value) return;
  const track = currentTrack.value;
  if (!track) return;

  isPlaying.value = false;
  audioElement.value.pause();
  audioElement.value.src = track.url;
  audioElement.value.load();

  setTimeout(() => {
    if (audioElement.value) {
      isPlaying.value = true;
      audioElement.value.play().catch(() => {
        isPlaying.value = false;
      });
    }
  }, 100);
};

const onAudioError = () => {
  if (!currentTrack.value) return;

  const mediaErr = audioElement.value?.error;
  isPlaying.value = false;

  let msg = '';
  if (mediaErr) {
    switch (mediaErr.code) {
      case 1:
        return;
      case 2:
        msg = 'Lỗi mạng khi tải nhạc. Kiểm tra kết nối Internet hoặc thử link khác.';
        break;
      case 3:
        msg = 'File nhạc bị hỏng hoặc định dạng trình duyệt không hỗ trợ (hãy dùng .mp3 / .ogg / .wav).';
        break;
      case 4:
        msg = 'Link nhạc không hỗ trợ phát trực tiếp. Nguyên nhân thường gặp: link YouTube/Spotify (không hỗ trợ), link hết hạn, hoặc bị chặn CORS. Hãy dùng link MP3 trực tiếp hoặc tải file từ máy!';
        break;
      default:
        msg = 'Không thể phát bài nhạc này. Vui lòng thử bài khác hoặc dùng file tải lên.';
    }
  } else {
    msg = 'Không thể phát bài nhạc này. Vui lòng kiểm tra link hoặc dùng file tải lên.';
  }

  notificationStore.showAlert(msg, '🎵 Lỗi phát nhạc');
};

const nextTrack = () => {
  if (playlist.value.length === 0) return;
  currentTrackIndex.value = (currentTrackIndex.value + 1) % playlist.value.length;
  playTrack();
};

const prevTrack = () => {
  if (playlist.value.length === 0) return;
  currentTrackIndex.value = (currentTrackIndex.value - 1 + playlist.value.length) % playlist.value.length;
  playTrack();
};

const adjustVolume = () => {
  if (audioElement.value) {
    audioElement.value.volume = volume.value;
  }
};

const onTimeUpdate = () => {
  if (audioElement.value) {
    currentTime.value = audioElement.value.currentTime;
  }
};

const onLoadedMetadata = () => {
  if (audioElement.value) {
    duration.value = audioElement.value.duration || 0;
  }
};

const progressPercentage = computed(() => {
  if (duration.value === 0) return 0;
  return (currentTime.value / duration.value) * 100;
});

const seekProgress = (event) => {
  if (!progressBar.value || !audioElement.value || playlist.value.length === 0) return;
  const rect = progressBar.value.getBoundingClientRect();
  const clickX = event.clientX - rect.left;
  const width = rect.width;
  const percentage = Math.max(0, Math.min(1, clickX / width));
  audioElement.value.currentTime = percentage * duration.value;
  currentTime.value = audioElement.value.currentTime;
};

const formatTime = (timeInSecs) => {
  if (isNaN(timeInSecs)) return '0:00';
  const mins = Math.floor(timeInSecs / 60);
  const secs = Math.floor(timeInSecs % 60);
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
};

const showImportForm = ref(false);
const importMode = ref('file');
const importForm = reactive({
  title: '',
  artist: '',
  url: ''
});
const uploadedFileObject = ref(null);

const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  uploadedFileObject.value = file;
  
  const cleanName = file.name.replace(/\.[^/.]+$/, "");
  
  const parts = cleanName.split('-');
  if (parts.length > 1) {
    importForm.title = parts[1].trim();
    importForm.artist = parts[0].trim();
  } else {
    importForm.title = cleanName;
    importForm.artist = 'Nghệ sĩ ẩn danh';
  }
};

const submitImport = () => {
  let songUrl = '';
  let songTitle = importForm.title.trim();
  let songArtist = importForm.artist.trim();

  if (importMode.value === 'file') {
    if (!uploadedFileObject.value) return;
    songUrl = URL.createObjectURL(uploadedFileObject.value);
    if (!songTitle) {
      songTitle = uploadedFileObject.value.name.replace(/\.[^/.]+$/, "");
    }
    if (!songArtist) {
      songArtist = 'Tệp âm thanh cục bộ';
    }
  } else {
    if (!importForm.url.trim() || !songTitle) {
      notificationStore.showAlert('Vui lòng nhập đầy đủ tên bài hát và đường dẫn nhạc!', 'Thiếu thông tin');
      return;
    }
    const rawUrl = importForm.url.trim();
    const urlLower = rawUrl.toLowerCase();

    if (urlLower.includes('youtube.com') || urlLower.includes('youtu.be')) {
      notificationStore.showAlert(
        '🎬 Link YouTube không phát được trực tiếp vì bản quyền.\n\n💡 Cách thêm nhạc từ YouTube:\n• Tải file MP3 về máy qua yt-dlp hoặc các trang chuyển đổi\n• Sau đó dùng nút "Tải file nhạc" để thêm vào danh sách',
        'Link YouTube không hỗ trợ'
      );
      return;
    }
    if (urlLower.includes('spotify.com')) {
      notificationStore.showAlert(
        '🎵 Link Spotify không phát được trực tiếp do DRM bảo vệ bản quyền.\n\n💡 Gợi ý: Tải file nhạc MP3 từ thiết bị hoặc dùng link MP3 công khai.',
        'Link Spotify không hỗ trợ'
      );
      return;
    }
    if (urlLower.includes('soundcloud.com')) {
      notificationStore.showAlert(
        '🎼 Link SoundCloud không phát trực tiếp được.\n\n💡 Gợi ý: Dùng link MP3 trực tiếp (kết thúc bằng .mp3) hoặc tải file về máy.',
        'Link SoundCloud không hỗ trợ'
      );
      return;
    }

    const looksLikeAudio = /\.(mp3|ogg|wav|flac|aac|m4a|opus)(\?.*)?$/i.test(rawUrl);
    if (!looksLikeAudio && !urlLower.includes('blob:') && !urlLower.startsWith('data:audio')) {
      notificationStore.showAlert(
        '⚠️ Đường dẫn không kết thúc bằng .mp3 / .wav / .ogg.\n\nNếu đây không phải link nhạc trực tiếp, trình duyệt có thể không phát được. Bạn vẫn có thể thử!',
        'Cảnh báo URL'
      );
    }

    songUrl = rawUrl;
    if (!songArtist) songArtist = 'Liên kết trực tuyến';
  }

  playlist.value.push({
    title: songTitle,
    artist: songArtist,
    url: songUrl,
    isLocal: importMode.value === 'file'
  });

  currentTrackIndex.value = playlist.value.length - 1;
  playTrack();
  
  importForm.title = '';
  importForm.artist = '';
  importForm.url = '';
  uploadedFileObject.value = null;
  showImportForm.value = false;
};

let isDragging = false;
let hasMoved = false;
let startX = 0;
let startY = 0;
let dragStartX = 0;
let dragStartY = 0;

const initDrag = (event) => {
  if (event.target.closest('button') || event.target.closest('input') || event.target.closest('select') || event.target.closest('a')) {
    return;
  }
  isDragging = true;
  hasMoved = false;
  const clientX = event.touches ? event.touches[0].clientX : event.clientX;
  const clientY = event.touches ? event.touches[0].clientY : event.clientY;
  startX = clientX - position.x;
  startY = clientY - position.y;
  dragStartX = clientX;
  dragStartY = clientY;
  
  document.addEventListener('mousemove', doDrag);
  document.addEventListener('mouseup', stopDrag);
  document.addEventListener('touchmove', doDrag);
  document.addEventListener('touchend', stopDrag);
};

const doDrag = (event) => {
  if (!isDragging) return;
  const clientX = event.touches ? event.touches[0].clientX : event.clientX;
  const clientY = event.touches ? event.touches[0].clientY : event.clientY;
  
  const dist = Math.sqrt(Math.pow(clientX - dragStartX, 2) + Math.pow(clientY - dragStartY, 2));
  if (dist > 5) {
    hasMoved = true;
  }

  let newX = clientX - startX;
  let newY = clientY - startY;
  
  const limitX = window.innerWidth - (isCollapsed.value ? 70 : 300);
  const limitY = window.innerHeight - (isCollapsed.value ? 70 : 200);
  
  position.x = Math.max(10, Math.min(limitX, newX));
  position.y = Math.max(10, Math.min(limitY, newY));
};

const stopDrag = () => {
  isDragging = false;
  document.removeEventListener('mousemove', doDrag);
  document.removeEventListener('mouseup', stopDrag);
  document.removeEventListener('touchmove', doDrag);
  document.removeEventListener('touchend', stopDrag);
};

const handleCircleClick = (event) => {
  if (hasMoved) {
    event.preventDefault();
    event.stopPropagation();
    return;
  }
  toggleCollapse();
};

onMounted(() => {
  if (audioElement.value) {
    audioElement.value.volume = volume.value;
  }
  window.addEventListener('resize', () => {
    if (position.x > window.innerWidth - 80) position.x = window.innerWidth - 80;
    if (position.y > window.innerHeight - 150) position.y = window.innerHeight - 150;
  });
});

onUnmounted(() => {
  if (audioElement.value) {
    audioElement.value.pause();
  }
  playlist.value.forEach(track => {
    if (track.isLocal && track.url.startsWith('blob:')) {
      URL.revokeObjectURL(track.url);
    }
  });
});
</script>

<style scoped>
.pfp {
  height: 48px;
  width: 48px;
  background-color: #f3e8ff;
  border: 1px solid #e9d5ff;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.playing {
  display: flex;
  position: relative;
  justify-content: center;
  gap: 2px;
  width: 32px;
  height: 20px;
}

.purpleline {
  background-color: #8000ff;
  height: 20px;
  width: 2.5px;
  position: relative;
  transform-origin: bottom;
  border-radius: 2px;
}

.line-1 {
  animation: playing 1s ease-in-out infinite;
  animation-delay: 0.2s;
}

.line-2 {
  animation: playing 1s ease-in-out infinite;
  animation-delay: 0.5s;
}

.line-3 {
  animation: playing 1s ease-in-out infinite;
  animation-delay: 0.6s;
}

.line-4 {
  animation: playing 1s ease-in-out infinite;
  animation-delay: 0s;
}

.line-5 {
  animation: playing 1s ease-in-out infinite;
  animation-delay: 0.4s;
}

.purpleline.paused {
  animation-play-state: paused;
  transform: scaleY(0.15) !important;
}

@keyframes playing {
  0% {
    transform: scaleY(0.15);
  }
  33% {
    transform: scaleY(0.65);
  }
  66% {
    transform: scaleY(0.95);
  }
  100% {
    transform: scaleY(0.15);
  }
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #8000ff;
  cursor: pointer;
  box-shadow: 0 0 4px rgba(128,0,255,0.3);
}

input[type="range"]::-moz-range-thumb {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #8000ff;
  cursor: pointer;
  box-shadow: 0 0 4px rgba(128,0,255,0.3);
}
</style>
