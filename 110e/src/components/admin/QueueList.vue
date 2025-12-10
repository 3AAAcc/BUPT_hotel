<template>
  <div class="queue-section">
    <h2>{{ title }} ({{ items.length }}{{ maxCount ? `/${maxCount}` : '' }})</h2>
    <div v-if="items.length > 0" class="queue-list">
      <div v-for="item in items" :key="item.roomId" :class="['queue-item', queueType]">
        <div class="item-header">
          <span class="room-id">房间 {{ item.roomId }}</span>
          <span class="fan-speed" :class="'speed-' + item.fanSpeed">
            {{ getFanSpeedText(item.fanSpeed) }}
          </span>
        </div>
        <div class="item-details">
          <div class="detail-row">
            <span>目标温度：{{ item.targetTemp }}°C</span>
            <span>当前温度：{{ item.currentTemp.toFixed(1) }}°C</span>
          </div>
          <div class="detail-row">
            <span>{{ leftLabel }}：{{ leftValue(item) }}</span>
            <span>{{ rightLabel }}：{{ rightValue(item) }}</span>
          </div>
          <div class="progress-bar">
            <div :class="['progress-fill', queueType]" :style="{ width: getProgress(item) + '%' }"></div>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="empty-message">
      {{ emptyMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
import type { RoomState } from '../../types/index';
import { FanSpeed } from '../../types/index';

interface QueueItem extends RoomState {
  serviceDuration?: number;
  waitDuration?: number;
  assignedWaitTime?: number;
}

const props = defineProps<{
  title: string;
  items: QueueItem[];
  queueType: 'serving' | 'waiting';
  maxCount?: number;
  emptyMessage: string;
  leftLabel: string;
  rightLabel: string;
  leftValue: (item: QueueItem) => string;
  rightValue: (item: QueueItem) => string;
  getProgress: (item: QueueItem) => number;
}>();

const getFanSpeedText = (speed: FanSpeed): string => {
  const speedMap = {
    [FanSpeed.LOW]: '低风',
    [FanSpeed.MEDIUM]: '中风',
    [FanSpeed.HIGH]: '高风'
  };
  return speedMap[speed] || '未知';
};
</script>

<style scoped>
.queue-section {
  margin-bottom: 24px;
  background: white;
  padding: 20px 24px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

h2 {
  margin: 0 0 16px 0;
  color: #111827;
  font-size: 16px;
  font-weight: 600;
}

.queue-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.queue-item {
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #ccc;
}

.queue-item.serving {
  background: #ecfdf5;
  border-left-color: #4ade80;
}

.queue-item.waiting {
  background: #fef3c7;
  border-left-color: #fbbf24;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.room-id {
  font-weight: bold;
  font-size: 16px;
  color: #333;
}

.fan-speed {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.speed-low {
  background: #dbeafe;
  color: #2563eb;
}

.speed-medium {
  background: #fef3c7;
  color: #d97706;
}

.speed-high {
  background: #fee2e2;
  color: #dc2626;
}

.item-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #666;
}

.progress-bar {
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
  margin-top: 5px;
}

.progress-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.progress-fill.serving {
  background: #4ade80;
}

.progress-fill.waiting {
  background: #fbbf24;
}

.empty-message {
  text-align: center;
  padding: 40px;
  color: #999;
  font-size: 16px;
}
</style>

