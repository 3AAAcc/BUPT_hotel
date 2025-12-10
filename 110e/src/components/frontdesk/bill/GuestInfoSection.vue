<template>
  <div v-if="guestName || guestPhone" class="guest-info">
    <h3>👤 客户信息</h3>
    <div class="info-grid">
      <div v-if="guestName" class="info-item">
        <span class="label">客户姓名：</span>
        <span class="value">{{ guestName }}</span>
      </div>
      <div v-if="guestPhone" class="info-item">
        <span class="label">联系电话：</span>
        <span class="value">{{ guestPhone }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  guestName?: string;
  guestPhone?: string;
}>();
</script>

<style scoped>
.guest-info {
  padding: 20px 24px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 12px;
  border: 2px solid #bae6fd;
  margin-bottom: 20px;
}

.guest-info h3 {
  font-size: 18px;
  font-weight: 600;
  color: #0c4a6e;
  margin: 0 0 16px 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-item .label {
  font-size: 14px;
  color: #0369a1;
  font-weight: 500;
}

.info-item .value {
  font-size: 14px;
  color: #0c4a6e;
  font-weight: 600;
}
</style>
