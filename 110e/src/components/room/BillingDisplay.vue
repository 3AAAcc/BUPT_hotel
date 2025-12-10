<template>
  <div class="billing-section">
    <div class="billing-card">
      <div class="billing-label">
        累计耗电
      </div>
      <div class="billing-value">
        {{ displayPower }}
      </div>
    </div>
    <div class="billing-card">
      <div class="billing-label">
        累计费用
      </div>
      <div class="billing-value primary">
        {{ displayCost }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  totalPower: number;
  totalCost: number;
}>();

const displayPower = computed(() => {
  const power = props.totalPower || 0;
  return `${power.toFixed(3)} 度`;
});

const displayCost = computed(() => {
  const cost = props.totalCost || 0;
  return `¥${cost.toFixed(2)}`;
});
</script>

<style scoped>
.billing-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.billing-display {
  padding: 28px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 16px;
  border: 2px solid #e2e8f0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.billing-display:hover {
  border-color: #067ef5;
  box-shadow: 0 6px 16px rgba(6, 126, 245, 0.15);
  transform: translateY(-2px);
}

.billing-card {
  background: #f9fafb;
  padding: 20px;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  text-align: center;
  transition: all 0.2s;
}

.billing-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.billing-label {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 8px;
  font-weight: 500;
}

.bill-value {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #067ef5 0%, #0369a1 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.billing-value {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.billing-value.primary {
  color: #10b981;
}

@media (max-width: 768px) {
  .billing-section {
    grid-template-columns: 1fr;
  }
}
</style>

