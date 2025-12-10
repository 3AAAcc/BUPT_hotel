<template>
  <div class="time-range-section">
    <h2>选择统计时间范围</h2>
    <div class="time-controls">
      <div class="time-input-group">
        <label>开始时间：</label>
        <input type="datetime-local" :value="startTime" @input="handleStartChange" />
      </div>
      <div class="time-input-group">
        <label>结束时间：</label>
        <input type="datetime-local" :value="endTime" @input="handleEndChange" />
      </div>
      <button class="btn-generate" @click="handleGenerate">
        生成报表
      </button>
    </div>

    <div class="quick-select">
      <button class="btn-quick" @click="emit('selectToday')">
        今天
      </button>
      <button class="btn-quick" @click="emit('selectWeek')">
        本周
      </button>
      <button class="btn-quick" @click="emit('selectMonth')">
        本月
      </button>
      <button class="btn-quick" @click="emit('selectAll')">
        全部
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
const { startTime, endTime } = defineProps<{
  startTime: string;
  endTime: string;
}>();

const emit = defineEmits<{
  'update:startTime': [value: string];
  'update:endTime': [value: string];
  generate: [];
  selectToday: [];
  selectWeek: [];
  selectMonth: [];
  selectAll: [];
}>();

const handleStartChange = (e: Event) => {
  emit('update:startTime', (e.target as HTMLInputElement).value);
};

const handleEndChange = (e: Event) => {
  emit('update:endTime', (e.target as HTMLInputElement).value);
};

const handleGenerate = () => {
  emit('generate');
};
</script>

<style scoped>
.time-range-section {
  margin-bottom: 24px;
  padding: 24px;
  background: white;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

h2 {
  margin: 0 0 24px 0;
  color: #1e293b;
  font-size: 17px;
  font-weight: 600;
  padding-bottom: 16px;
  border-bottom: 2px solid #e2e8f0;
}

.time-controls {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.time-input-group {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 280px;
}

.time-input-group label {
  font-weight: 600;
  color: #475569;
  font-size: 14px;
  white-space: nowrap;
}

.time-input-group input {
  flex: 1;
  padding: 11px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  background: #f8fafc;
  transition: all 0.2s;
  font-family: inherit;
}

.time-input-group input:focus {
  border-color: #067ef5;
  background: white;
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.1);
}

.btn-generate {
  padding: 11px 32px;
  background: linear-gradient(135deg, #067ef5 0%, #0369a1 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 8px rgba(6, 126, 245, 0.2);
  white-space: nowrap;
}

.btn-generate:hover {
  background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(6, 126, 245, 0.3);
}

.btn-generate:active {
  transform: translateY(0);
}

.quick-select {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-quick {
  padding: 10px 24px;
  background: #f8fafc;
  color: #475569;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.btn-quick:hover {
  background: #e0f2fe;
  border-color: #067ef5;
  color: #067ef5;
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(6, 126, 245, 0.15);
}

.btn-quick:active {
  transform: translateY(0);
}
</style>

