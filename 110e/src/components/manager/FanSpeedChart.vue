<template>
  <div class="distribution-section">
    <h3>风速使用分布</h3>
    <div class="distribution-chart">
      <div class="chart-bar">
        <div class="bar-label">
          高风
        </div>
        <div class="bar-container">
          <div class="bar-fill high" :style="{ width: getPercentage(high) + '%' }">
            {{ high }}
          </div>
        </div>
      </div>
      <div class="chart-bar">
        <div class="bar-label">
          中风
        </div>
        <div class="bar-container">
          <div class="bar-fill medium" :style="{ width: getPercentage(medium) + '%' }">
            {{ medium }}
          </div>
        </div>
      </div>
      <div class="chart-bar">
        <div class="bar-label">
          低风
        </div>
        <div class="bar-container">
          <div class="bar-fill low" :style="{ width: getPercentage(low) + '%' }">
            {{ low }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  high: number;
  medium: number;
  low: number;
}>();

const total = computed(() => props.high + props.medium + props.low);

const getPercentage = (value: number): number => {
  return total.value > 0 ? (value / total.value) * 100 : 0;
};
</script>

<style scoped>
.distribution-section {
  padding: 0;
  background: white;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  margin-bottom: 24px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

h3 {
  margin: 0;
  padding: 20px 24px;
  background: linear-gradient(135deg, #067ef5 0%, #0369a1 100%);
  color: white;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 3px solid #0284c7;
}

.distribution-chart {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 24px;
}

.chart-bar {
  display: flex;
  align-items: center;
  gap: 20px;
}

.bar-label {
  width: 80px;
  font-weight: 700;
  color: #475569;
  font-size: 15px;
  text-align: right;
}

.bar-container {
  flex: 1;
  height: 36px;
  background: #f1f5f9;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
}

.bar-fill {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 13px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 36px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.bar-fill.high {
  background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
}

.bar-fill.medium {
  background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
}

.bar-fill.low {
  background: linear-gradient(90deg, #067ef5 0%, #0369a1 100%);
}
</style>

