<template>
  <div class="detail-records">
    <div class="detail-header">
      <h3>📋 空调使用详单</h3>
      <div class="record-summary">
        <span class="record-count">共 {{ records.length }} 条记录</span>
        <span class="record-total">详单合计：¥{{ totalCost.toFixed(2) }}</span>
      </div>
    </div>
    <div class="records-table">
      <div class="table-header">
        <span>时间</span>
        <span>风速</span>
        <span>目标温度</span>
        <span>时长</span>
        <span>耗电 (度)</span>
        <span>费用 (元)</span>
      </div>
      <div v-for="(record, index) in records" :key="index" class="table-row">
        <span class="time">{{ formatTime(record.timestamp) }}</span>
        <span class="fan-speed" :class="getFanSpeedClass(record.fanSpeed || '')">
          {{ getFanSpeedText(record.fanSpeed || '') }}
        </span>
        <span class="temp">{{ record.targetTemp ? record.targetTemp.toFixed(1) : '-' }}°C</span>
        <span class="duration">{{ formatDuration(record.duration) }}</span>
        <span class="power">{{ record.powerConsumption.toFixed(3) }}</span>
        <span class="cost">¥{{ record.cost.toFixed(2) }}</span>
      </div>
      <div v-if="records.length === 0" class="empty-records">
        <span>暂无使用记录</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface DetailRecord {
  timestamp: number;
  fanSpeed?: string;
  targetTemp?: number;
  duration: number;
  powerConsumption: number;
  cost: number;
}

const props = defineProps<{
  records: DetailRecord[];
}>();

const totalCost = computed(() => {
  return props.records.reduce((sum, record) => sum + record.cost, 0);
});

const formatTime = (timestamp: number): string => {
  return new Date(timestamp).toLocaleTimeString('zh-CN');
};

const formatDuration = (seconds: number): string => {
  if (seconds === 0) return '-';
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  const parts = [];
  if (hours > 0) parts.push(`${hours}小时`);
  if (minutes > 0) parts.push(`${minutes}分钟`);
  if (secs > 0) parts.push(`${secs}秒`);

  return parts.join('') || '-';
};

const getFanSpeedText = (fanSpeed: string): string => {
  const speedMap: Record<string, string> = {
    'LOW': '低速',
    'MEDIUM': '中速',
    'HIGH': '高速'
  };
  return speedMap[fanSpeed] || fanSpeed || '-';
};

const getFanSpeedClass = (fanSpeed: string): string => {
  const classMap: Record<string, string> = {
    'LOW': 'speed-low',
    'MEDIUM': 'speed-medium',
    'HIGH': 'speed-high'
  };
  return classMap[fanSpeed] || '';
};
</script>

<style scoped>
.detail-records {
  padding: 20px 24px;
  background: white;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f1f5f9;
}

.detail-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.record-summary {
  display: flex;
  gap: 16px;
  font-size: 13px;
}

.record-count {
  color: #64748b;
  font-weight: 500;
}

.record-total {
  color: #ef4444;
  font-weight: 700;
}

.records-table {
  overflow-x: auto;
}

.table-header {
  display: grid;
  grid-template-columns: 120px 80px 100px 100px 100px 100px;
  gap: 12px;
  padding: 12px;
  background: #f1f5f9;
  border-radius: 8px 8px 0 0;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  text-align: center;
}

.table-row {
  display: grid;
  grid-template-columns: 120px 80px 100px 100px 100px 100px;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 13px;
  align-items: center;
  transition: all 0.2s;
}

.table-row:hover {
  background: #f8fafc;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row span {
  text-align: center;
}

.time {
  font-size: 12px;
  color: #64748b;
  font-family: monospace;
}

.fan-speed {
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 12px;
  display: inline-block;
}

.speed-low {
  background: #dbeafe;
  color: #1e40af;
}

.speed-medium {
  background: #fef3c7;
  color: #92400e;
}

.speed-high {
  background: #fee2e2;
  color: #991b1b;
}

.temp {
  color: #1e293b;
  font-weight: 500;
}

.duration {
  color: #64748b;
}

.power {
  color: #0891b2;
  font-weight: 500;
  font-family: monospace;
}

.cost {
  color: #dc2626;
  font-weight: 700;
}

.empty-records {
  padding: 40px;
  text-align: center;
  color: #94a3b8;
  font-size: 14px;
}
</style>
