<template>
  <div class="wind-speed-section">
    <h3 class="section-title">
      风速设置
    </h3>
    <div class="wind-buttons">
      <button
        :class="['btn-wind', { 'active': currentSpeed === FanSpeed.LOW }]"
        @click="emit('change', FanSpeed.LOW)"
      >
        <span class="wind-label">低风速</span>
        <span class="wind-rate">1度/3分钟</span>
      </button>
      <button
        :class="['btn-wind', { 'active': currentSpeed === FanSpeed.MEDIUM }]"
        @click="emit('change', FanSpeed.MEDIUM)"
      >
        <span class="wind-label">中风速</span>
        <span class="wind-rate">1度/2分钟</span>
      </button>
      <button
        :class="['btn-wind', { 'active': currentSpeed === FanSpeed.HIGH }]"
        @click="emit('change', FanSpeed.HIGH)"
      >
        <span class="wind-label">高风速</span>
        <span class="wind-rate">1度/分钟</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FanSpeed } from '../../types/index';

const { currentSpeed } = defineProps<{
  currentSpeed: FanSpeed;
}>();

const emit = defineEmits<{
  change: [speed: FanSpeed];
}>();
</script>

<style scoped>
.wind-speed-section {
  background: #f9fafb;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 15px;
  font-weight: 600;
  color: #334155;
  text-align: center;
}

.wind-buttons {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.btn-wind {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 18px 16px;
  border: 2px solid #e0f2fe;
  border-radius: 10px;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.2s;
}

.wind-label {
  font-size: 15px;
  font-weight: 600;
  color: #475569;
}

.wind-rate {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
}

.btn-wind:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.btn-wind.active {
  border-color: #3b82f6;
  background: #3b82f6;
}

.btn-wind.active .wind-label,
.btn-wind.active .wind-rate {
  color: white;
}

@media (max-width: 768px) {
  .wind-buttons {
    grid-template-columns: 1fr;
  }
}
</style>

