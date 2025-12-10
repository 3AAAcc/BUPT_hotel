<template>
  <div class="step-content">
    <div class="step-header">
      <h3>第一步：选择房间</h3>
      <p class="step-description">
        查询并选择可用房间
      </p>
    </div>

    <!-- 筛选条件 -->
    <div class="room-query">
      <div class="form-row">
        <div class="form-group">
          <label>房型偏好：</label>
          <select v-model="filters.roomType">
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
        <div class="form-group">
          <label>价格范围：</label>
          <select v-model="filters.priceRange">
            <option value="">
              不限
            </option>
            <option value="economy">
              经济型 (¥150-200)
            </option>
            <option value="comfort">
              舒适型 (¥201-400)
            </option>
            <option value="luxury">
              豪华型 (¥401-800)
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- 房间列表 -->
    <div class="available-rooms-grid">
      <div
        v-for="roomId in filteredRooms"
        :key="roomId"
        :class="['room-option', { selected: selectedRoomId === roomId }]"
        @click="selectRoom(roomId)"
      >
        <div class="room-icon">
          🏠
        </div>
        <div class="room-number">
          房间 {{ roomId }}
        </div>
        <div class="room-details">
          <span class="room-type">{{ formatRoomType(getRoomDetail(roomId).roomType) }}</span>
          <span class="room-price">¥{{ getRoomDetail(roomId).pricePerNight }}/晚</span>
        </div>
        <div v-if="selectedRoomId === roomId" class="selected-badge">
          ✓ 已选
        </div>
      </div>
    </div>

    <div v-if="availableRooms.length === 0" class="empty-state">
      <p>暂无可用房间</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

interface RoomDetail {
  roomType: string;
  pricePerNight: number;
}

interface CheckInRecord {
  roomId: string;
  guestName?: string;
  checkInTime: number;
  [key: string]: unknown;
}

const props = defineProps<{
  availableRooms: string[];
  checkInRecords: CheckInRecord[];
  selectedRoomId?: string;
}>();

const emit = defineEmits<{
  'update:selectedRoomId': [value: string];
  'next': [];
}>();

const filters = ref({
  roomType: '',
  priceRange: ''
});

// 获取房间详情
const getRoomDetail = (roomId: string): RoomDetail => {
  const roomNum = parseInt(roomId);
  if (roomNum >= 101 && roomNum <= 104) {
    return { roomType: 'STANDARD_SINGLE', pricePerNight: 150 };
  } else if (roomNum >= 105 && roomNum <= 108) {
    return { roomType: 'STANDARD_DOUBLE', pricePerNight: 200 };
  } else if (roomNum >= 201 && roomNum <= 206) {
    return { roomType: 'DELUXE', pricePerNight: 400 };
  } else if (roomNum >= 301 && roomNum <= 306) {
    return { roomType: 'SUITE', pricePerNight: 800 };
  }
  return { roomType: 'UNKNOWN', pricePerNight: 0 };
};

// 格式化房间类型
const formatRoomType = (type: string): string => {
  const typeMap: Record<string, string> = {
    'STANDARD_SINGLE': '标准单人间',
    'STANDARD_DOUBLE': '标准双人间',
    'DELUXE': '豪华间',
    'SUITE': '套间',
    'UNKNOWN': '未知'
  };
  return typeMap[type] || '未知';
};

// 筛选后的房间列表
const filteredRooms = computed(() => {
  return props.availableRooms.filter(roomId => {
    const detail = getRoomDetail(roomId);

    // 按房型筛选
    if (filters.value.roomType && detail.roomType !== filters.value.roomType) {
      return false;
    }

    // 按价格筛选
    if (filters.value.priceRange) {
      const price = detail.pricePerNight;
      switch (filters.value.priceRange) {
        case 'economy':
          if (price > 200) return false;
          break;
        case 'comfort':
          if (price <= 200 || price > 400) return false;
          break;
        case 'luxury':
          if (price <= 400) return false;
          break;
      }
    }

    return true;
  });
});

// 选择房间
const selectRoom = (roomId: string) => {
  emit('update:selectedRoomId', roomId);
  emit('next');
};
</script>

<style scoped>
.step-content {
  padding: 20px;
}

.step-header {
  margin-bottom: 24px;
}

.step-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.step-description {
  font-size: 14px;
  color: #64748b;
}

.room-query {
  margin-bottom: 24px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-group {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #475569;
  white-space: nowrap;
}

.form-group select {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 14px;
  color: #334155;
  background: white;
  cursor: pointer;
}

.available-rooms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.room-option {
  position: relative;
  padding: 16px;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-height: 140px;
}

.room-option:hover {
  border-color: #3b82f6;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.room-option.selected {
  border-color: #10b981;
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
}

.room-icon {
  font-size: 32px;
  margin-bottom: 4px;
}

.room-number {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.room-details {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.room-type {
  color: #64748b;
}

.room-price {
  color: #ef4444;
  font-weight: 600;
}

.selected-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #10b981;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #94a3b8;
}
</style>
