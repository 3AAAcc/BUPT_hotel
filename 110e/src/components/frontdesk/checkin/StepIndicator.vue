<template>
  <div class="steps-indicator">
    <div
      v-for="(step, index) in steps"
      :key="index"
      :class="['step-item', {
        active: currentStep === index,
        completed: currentStep > index
      }]"
    >
      <div class="step-number">
        <svg
          v-if="currentStep > index"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
        >
          <path
            d="M5 13l4 4L19 7"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
          />
        </svg>
        <span v-else>{{ index + 1 }}</span>
      </div>
      <div class="step-label">
        {{ step }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  steps: string[];
  currentStep: number;
}>();
</script>

<style scoped>
.steps-indicator {
  display: flex;
  justify-content: space-between;
  margin-bottom: 32px;
  padding: 24px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 16px;
  border: 1px solid #e2e8f0;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  position: relative;
  flex: 1;
}

.step-item:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 20px;
  left: calc(50% + 30px);
  right: calc(-50% + 30px);
  height: 2px;
  background: #d1d5db;
  z-index: 0;
}

.step-item.completed:not(:last-child)::after {
  background: linear-gradient(90deg, #10b981, #059669);
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 2px solid #d1d5db;
  color: #6b7280;
  font-weight: 600;
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
}

.step-item.active .step-number {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-color: #3b82f6;
  color: white;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.step-item.completed .step-number {
  background: linear-gradient(135deg, #10b981, #059669);
  border-color: #10b981;
  color: white;
}

.step-label {
  font-size: 13px;
  font-weight: 500;
  color: #6b7280;
  text-align: center;
  max-width: 120px;
}

.step-item.active .step-label {
  color: #2563eb;
  font-weight: 600;
}

.step-item.completed .step-label {
  color: #059669;
}
</style>
