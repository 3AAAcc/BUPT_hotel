<template>
  <div class="system-overview">
    <div class="overview-card">
      <div class="card-label">
        总房间数
      </div>
      <div class="card-value">
        {{ totalRooms }}
      </div>
    </div>
    <div class="overview-card active">
      <div class="card-label">
        正在送风
      </div>
      <div class="card-value">
        {{ servingRooms }}
      </div>
    </div>
    <div class="overview-card waiting">
      <div class="card-label">
        等待队列
      </div>
      <div class="card-value">
        {{ waitingRooms }}
      </div>
    </div>
    <div class="overview-card cost">
      <div class="card-label">
        总费用
      </div>
      <div class="card-value">
        ¥{{ totalCost.toFixed(2) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  totalRooms: number;
  servingRooms: number;
  waitingRooms: number;
  totalCost: number;
}>();
</script>

<style scoped>
.system-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.overview-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  border: 2px solid #f0f4f8;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: all 0.2s;
}

.overview-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.overview-card.active {
  border-color: #a7f3d0;
  background: #f0fdf4;
}

.overview-card.waiting {
  border-color: #fde68a;
  background: #fef3c7;
}

.overview-card.cost {
  border-color: #bfdbfe;
  background: #eff6ff;
}

.card-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  margin-bottom: 8px;
}

.card-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}
</style>

