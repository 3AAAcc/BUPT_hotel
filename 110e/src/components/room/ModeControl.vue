<template>
  <div class="control-section">
    <h3 class="section-title">
      工作模式
    </h3>
    <div class="mode-buttons">
      <button
        :class="['mode-btn', { active: currentMode === ACMode.COOLING }]"
        @click="emit('switch', ACMode.COOLING)"
      >
        <span class="text">制冷模式</span>
        <span class="range">18-25°C</span>
      </button>
      <button
        :class="['mode-btn', { active: currentMode === ACMode.HEATING }]"
        @click="emit('switch', ACMode.HEATING)"
      >
        <span class="text">制热模式</span>
        <span class="range">25-30°C</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ACMode } from '../../types/index';

const { currentMode } = defineProps<{
  currentMode: ACMode;
}>();

const emit = defineEmits<{
  switch: [mode: ACMode];
}>();
</script>

<style scoped>
.control-section {
  background: #ffffff;
  padding: 24px;
  border-radius: 12px;
  border: 2px solid #f0f9ff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 15px;
  font-weight: 600;
  color: #334155;
  text-align: center;
}

.mode-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mode-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px;
  border: 2px solid #e0f2fe;
  border-radius: 10px;
  background: #f0f9ff;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-btn .text {
  font-size: 15px;
  font-weight: 600;
  color: #475569;
}

.mode-btn .range {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
}

.mode-btn:hover {
  border-color: #067ef5;
  background: #e0f2fe;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(2, 132, 199, 0.15);
}

.mode-btn.active {
  border-color: #067ef5;
  background: #067ef5;
}

.mode-btn.active .text,
.mode-btn.active .range {
  color: white;
}
</style>

