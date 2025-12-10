<template>
  <div class="history-section">
    <h2>历史账单</h2>
    <div v-if="bills.length > 0" class="history-list">
      <div
        v-for="bill in bills"
        :key="bill.roomId + '-' + bill.checkOutTime"
        class="history-item"
        @click="handleViewBill(bill)"
      >
        <div class="history-room">
          房间 {{ bill.roomId }}
        </div>
        <div class="history-time">
          {{ formatDateTime(bill.checkOutTime) }}
        </div>
        <div class="history-cost">
          ¥{{ bill.totalCost.toFixed(2) }}
        </div>
      </div>
    </div>
    <div v-else class="empty-message">
      暂无历史账单
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Bill } from '../../types/index';

const props = defineProps<{
  bills: Bill[];
}>();

const emit = defineEmits<{
  viewBill: [bill: Bill];
}>();

const handleViewBill = (bill: Bill) => {
  emit('viewBill', bill);
};

const formatDateTime = (timestamp: number): string => {
  return new Date(timestamp).toLocaleString('zh-CN');
};
</script>

<style scoped>
.history-section {
  margin-bottom: 24px;
  padding: 24px;
  background: white;
  border-radius: 12px;
  border: 2px solid #f0f4f8;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

h2 {
  margin: 0 0 20px 0;
  color: #1e293b;
  font-size: 18px;
  font-weight: 600;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f9fafb;
  border-radius: 8px;
  border: 2px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.3s;
}

.history-item:hover {
  border-color: #667eea;
  transform: translateX(5px);
}

.history-room {
  font-weight: bold;
  color: #333;
  font-size: 16px;
}

.history-time {
  color: #666;
  font-size: 14px;
}

.history-cost {
  font-weight: bold;
  color: #667eea;
  font-size: 18px;
}

.empty-message {
  text-align: center;
  padding: 40px;
  color: #999;
  font-size: 16px;
}
</style>

