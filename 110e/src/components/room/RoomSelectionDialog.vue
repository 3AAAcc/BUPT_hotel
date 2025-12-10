<template>
  <div class="room-selection-dialog-overlay" @click.self="$emit('close')">
    <div class="room-selection-dialog">
      <div class="dialog-header">
        <h2>选择房间</h2>
        <button class="close-btn" @click="$emit('close')">
          ×
        </button>
      </div>

      <!-- 筛选器 -->
      <div class="filters">
        <div class="filter-item">
          <label>房型：</label>
          <select v-model="filter.roomType" @change="loadRooms">
            <option value="">
              全部房型
            </option>
            <option value="STANDARD_SINGLE">
              标准单人间 ¥150
            </option>
            <option value="STANDARD_DOUBLE">
              标准双人间 ¥200
            </option>
            <option value="DELUXE">
              豪华间 ¥400
            </option>
            <option value="SUITE">
              套间 ¥800
            </option>
          </select>
        </div>

        <div class="filter-item">
          <label>价格档次：</label>
          <select v-model="priceRange" @change="onPriceRangeChange">
            <option value="">
              全部价格
            </option>
            <option value="economic">
              经济型 (&lt;¥200)
            </option>
            <option value="comfort">
              舒适型 (¥300-500)
            </option>
            <option value="luxury">
              豪华型 (&gt;¥500)
            </option>
          </select>
        </div>

        <div class="filter-item">
          <label>楼层：</label>
          <select v-model="filter.floor" @change="loadRooms">
            <option :value="undefined">
              全部楼层
            </option>
            <option :value="1">
              1楼
            </option>
            <option :value="2">
              2楼
            </option>
            <option :value="3">
              3楼
            </option>
          </select>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading">
        加载中...
      </div>

      <!-- 房间列表 -->
      <div v-else-if="availableRooms.length > 0" class="room-grid">
        <div
          v-for="room in availableRooms"
          :key="room.roomId"
          class="room-card"
          :class="{ selected: selectedRoom?.roomId === room.roomId }"
          @click="selectRoom(room)"
        >
          <div class="room-number">
            {{ room.roomId }}
          </div>
          <div class="room-type">
            {{ getRoomTypeName(room.roomType) }}
          </div>
          <div class="room-price">
            ¥{{ room.pricePerNight }}/晚
          </div>
          <div class="room-floor">
            {{ room.floor }}楼
          </div>
          <div class="room-features">
            {{ room.roomFeatures }}
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <p>😔 暂无符合条件的房间</p>
        <p class="hint">
          试试调整筛选条件
        </p>
      </div>

      <!-- 底部操作按钮 -->
      <div class="dialog-footer">
        <button class="btn-cancel" @click="$emit('close')">
          取消
        </button>
        <button
          class="btn-confirm"
          :disabled="!selectedRoom"
          @click="confirmSelection"
        >
          确认选择
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { frontDeskApi } from '../../api/hvac';

interface Room {
  roomId: string;
  roomType: string;
  pricePerNight: number;
  floor: number;
  roomFeatures?: string;
  isAvailable: boolean;
}

const filter = ref({
  roomType: '',
  minPrice: undefined as number | undefined,
  maxPrice: undefined as number | undefined,
  floor: undefined as number | undefined
});

const availableRooms = ref<Room[]>([]);
const selectedRoom = ref<Room | null>(null);
const priceRange = ref('');
const loading = ref(false);

const emit = defineEmits<{
  select: [room: Room];
  close: [];
}>();

const loadRooms = async () => {
  loading.value = true;
  try {
    const rooms = await frontDeskApi.getAvailableRooms(filter.value);
    availableRooms.value = rooms;
  } catch (error) {
    console.error('加载可入住房间失败:', error);
    alert('加载房间失败，请重试');
  } finally {
    loading.value = false;
  }
};

const onPriceRangeChange = () => {
  switch (priceRange.value) {
    case 'economic':
      filter.value.minPrice = undefined;
      filter.value.maxPrice = 200;
      break;
    case 'comfort':
      filter.value.minPrice = 300;
      filter.value.maxPrice = 500;
      break;
    case 'luxury':
      filter.value.minPrice = 500;
      filter.value.maxPrice = undefined;
      break;
    default:
      filter.value.minPrice = undefined;
      filter.value.maxPrice = undefined;
  }
  loadRooms();
};

const selectRoom = (room: Room) => {
  selectedRoom.value = room;
};

const confirmSelection = () => {
  if (selectedRoom.value) {
    emit('select', selectedRoom.value);
  }
};

const getRoomTypeName = (type: string) => {
  const names: Record<string, string> = {
    'STANDARD_SINGLE': '标准单人间',
    'STANDARD_DOUBLE': '标准双人间',
    'DELUXE': '豪华间',
    'SUITE': '套间'
  };
  return names[type] || type;
};

onMounted(() => {
  loadRooms();
});
</script>

<style scoped>
.room-selection-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.room-selection-dialog {
  background: white;
  border-radius: 16px;
  padding: 24px;
  max-width: 900px;
  max-height: 85vh;
  overflow-y: auto;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e5e7eb;
}

.dialog-header h2 {
  margin: 0;
  font-size: 24px;
  color: #1f2937;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 32px;
  cursor: pointer;
  color: #9ca3af;
  padding: 0;
  width: 32px;
  height: 32px;
  line-height: 1;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #1f2937;
}

.filters {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-item label {
  font-weight: 500;
  color: #374151;
  min-width: 60px;
}

.filter-item select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  min-width: 150px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.filter-item select:hover {
  border-color: #3b82f6;
}

.filter-item select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.loading {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
  font-size: 16px;
}

.room-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.room-card {
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.room-card:hover {
  border-color: #3b82f6;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.room-card.selected {
  border-color: #3b82f6;
  background-color: #eff6ff;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

.room-number {
  font-size: 24px;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 8px;
}

.room-type {
  color: #6b7280;
  margin-bottom: 4px;
  font-size: 14px;
}

.room-price {
  font-size: 20px;
  font-weight: 600;
  color: #3b82f6;
  margin: 8px 0;
}

.room-floor {
  color: #9ca3af;
  font-size: 14px;
  margin-bottom: 8px;
}

.room-features {
  font-size: 13px;
  color: #9ca3af;
  line-height: 1.5;
  margin-top: 8px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #9ca3af;
}

.empty-state p {
  margin: 8px 0;
  font-size: 16px;
}

.empty-state .hint {
  font-size: 14px;
  color: #d1d5db;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.btn-cancel,
.btn-confirm {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: white;
  border: 1px solid #d1d5db;
  color: #374151;
}

.btn-cancel:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.btn-confirm {
  background: #3b82f6;
  border: none;
  color: white;
}

.btn-confirm:hover:not(:disabled) {
  background: #2563eb;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.btn-confirm:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  opacity: 0.5;
}
</style>
