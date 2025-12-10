<template>
  <div class="view-container">
    <!-- 房间选择 -->
    <div class="room-selector">
      <label>选择房间：</label>
      <select v-if="occupiedRooms.length > 0" v-model="selectedRoomId">
        <option v-for="roomId in occupiedRooms" :key="roomId" :value="roomId">
          房间 {{ roomId }}
        </option>
      </select>
      <div v-else class="no-rooms-message">
        暂无已入住房间，请先到前台办理入住
      </div>
    </div>

    <!-- 房间客户端 -->
    <RoomClient
      v-if="selectedRoom && selectedRoomId && occupiedRooms.includes(selectedRoomId)"
      :key="selectedRoomId"
      :room-id="selectedRoomId"
      :room-state="selectedRoom"
      :is-loading="isLoading"
      :on-turn-on="handleTurnOn"
      :on-turn-off="handleTurnOff"
      :on-update-settings="handleUpdateSettings"
      :on-set-mode="handleSetMode"
    />
    <div v-else-if="occupiedRooms.length === 0" class="no-rooms-placeholder">
      <div class="placeholder-icon">
        🏨
      </div>
      <h3>欢迎使用中央温控系统</h3>
      <p>当前没有已入住的房间</p>
      <p class="hint">
        请先到"前台结账"页面办理入住手续
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import RoomClient from '../room/RoomClient.vue';
import type { IHvacService } from '../../services/ApiAdapter';
import type { RoomState } from '../../types/index';
import { ACMode, FanSpeed } from '../../types/index';

const props = defineProps<{
  hvacService: IHvacService;
  occupiedRooms: string[];
  allRooms: RoomState[];
  refreshKey: number;
}>();

const emit = defineEmits<{
  refresh: [];
}>();

const selectedRoomId = ref<string>('');
const isLoading = ref(false);
const errorMessage = ref('');

// 选中的房间状态（依赖 refreshKey 以确保响应式更新）
const selectedRoom = computed(() => {
  // 强制依赖 refreshKey，确保每次变化都重新获取
  void props.refreshKey;
  const roomId = selectedRoomId.value;
  if (!roomId) return null;

  // 每次都重新获取房间状态，确保获取最新数据
  const room = props.hvacService.getRoomState(roomId);
  // 返回一个新对象，避免引用缓存
  return room ? { ...room } : null;
});

// 监听已入住房间列表变化，自动选择第一个房间
watch(() => props.occupiedRooms, (newOccupiedRooms) => {
  if (newOccupiedRooms.length > 0) {
    if (!newOccupiedRooms.includes(selectedRoomId.value)) {
      const firstRoom = newOccupiedRooms[0];
      if (firstRoom) {
        selectedRoomId.value = firstRoom;
      }
    }
  } else {
    selectedRoomId.value = '';
  }
}, { immediate: true });

// 页面加载时的初始化
onMounted(async () => {
  // 进入时刷新房间状态和入住记录
  if (props.hvacService.refreshRoomStates) {
    await props.hvacService.refreshRoomStates();
  }
  if (props.hvacService.refreshCheckInRecords) {
    await props.hvacService.refreshCheckInRecords();
  }
  emit('refresh');
});

// 房间操作
const handleTurnOn = async () => {
  const roomId = selectedRoomId.value;
  if (!roomId) return;

  try {
    isLoading.value = true;
    errorMessage.value = '';
    await props.hvacService.turnOn(roomId);
    // 开机成功后触发刷新
    emit('refresh');
  } catch (error: unknown) {
    console.error('开机失败:', error);
    const err = error as { message?: string };
    errorMessage.value = err.message || '开机失败，请重试';
    alert(`开机失败: ${err.message || '未知错误'}`);
  } finally {
    isLoading.value = false;
  }
};

const handleTurnOff = async () => {
  const roomId = selectedRoomId.value;
  if (!roomId) return;

  try {
    isLoading.value = true;
    errorMessage.value = '';
    await props.hvacService.turnOff(roomId);
    // 关机成功后触发刷新
    emit('refresh');
  } catch (error: unknown) {
    console.error('关机失败:', error);
    const err = error as { message?: string };
    errorMessage.value = err.message || '关机失败，请重试';
    alert(`关机失败: ${err.message || '未知错误'}`);
  } finally {
    isLoading.value = false;
  }
};

const handleUpdateSettings = async (targetTemp: number, fanSpeed: FanSpeed) => {
  const roomId = selectedRoomId.value;
  if (roomId) {
    const room = props.hvacService.getRoomState(roomId);
    const mode = room?.mode || ACMode.COOLING; // 默认制冷模式
    await props.hvacService.sendRequest(roomId, targetTemp, fanSpeed, mode);
    // 更新设置后触发刷新
    emit('refresh');
  }
};

const handleSetMode = async (mode: ACMode) => {
  const roomId = selectedRoomId.value;
  if (roomId) {
    await props.hvacService.setMode(roomId, mode);
    // 模式切换后触发刷新
    emit('refresh');
  }
};
</script>

<style scoped>
.view-container {
  width: 100%;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.room-selector {
  max-width: 700px;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.room-selector label {
  font-weight: 500;
  color: #111827;
  font-size: 14px;
}

.room-selector select {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  cursor: pointer;
  color: #374151;
  background: #ffffff;
}

.room-selector select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.no-rooms-message {
  flex: 1;
  padding: 12px 16px;
  background: #fef3c7;
  border: 2px solid #fbbf24;
  border-radius: 8px;
  color: #92400e;
  font-size: 14px;
  font-weight: 500;
  text-align: center;
}

.no-rooms-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 40px;
  min-height: 500px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 16px;
  border: 2px solid #e2e8f0;
  max-width: 700px;
  margin: 0 auto;
}

.placeholder-icon {
  font-size: 72px;
  margin-bottom: 24px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.no-rooms-placeholder h3 {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
}

.no-rooms-placeholder p {
  font-size: 15px;
  color: #64748b;
  margin-bottom: 8px;
}

.no-rooms-placeholder .hint {
  font-size: 14px;
  color: #067ef5;
  font-weight: 500;
  margin-top: 8px;
}
</style>

