<template>
  <div class="bill-summary">
    <h3>🏠 入住信息</h3>
    <div class="summary-row">
      <span>房间号：</span>
      <span class="value-bold">{{ roomId }}</span>
    </div>
    <div class="summary-row">
      <span>入住时间：</span>
      <span>{{ formatDateTime(checkInTime) }}</span>
    </div>
    <div class="summary-row">
      <span>退房时间：</span>
      <span>{{ formatDateTime(checkOutTime) }}</span>
    </div>
    <div class="summary-row">
      <span>入住天数：</span>
      <span class="value-bold">{{ stayDays }} 天</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  roomId: string;
  checkInTime: number;
  checkOutTime: number;
  stayDays?: number;
}>();

const formatDateTime = (timestamp: number): string => {
  return new Date(timestamp).toLocaleString('zh-CN');
};

const stayDays = computed(() => {
  if (props.stayDays) return props.stayDays;
  const days = Math.ceil((props.checkOutTime - props.checkInTime) / (1000 * 60 * 60 * 24));
  return days > 0 ? days : 1;
});
</script>

<style scoped>
.bill-summary {
  padding: 20px 24px;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 12px;
  border: 2px solid #fbbf24;
  margin-bottom: 20px;
}

.bill-summary h3 {
  font-size: 18px;
  font-weight: 600;
  color: #78350f;
  margin: 0 0 16px 0;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  font-size: 14px;
  border-bottom: 1px solid rgba(251, 191, 36, 0.3);
}

.summary-row:last-child {
  border-bottom: none;
}

.summary-row span:first-child {
  color: #92400e;
  font-weight: 500;
}

.summary-row span:last-child {
  color: #78350f;
}

.value-bold {
  font-weight: 700 !important;
  font-size: 15px !important;
}
</style>
