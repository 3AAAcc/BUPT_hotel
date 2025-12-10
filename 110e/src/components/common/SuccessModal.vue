<template>
  <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <div class="success-icon">
          <svg
            width="60"
            height="60"
            viewBox="0 0 24 24"
            fill="none"
          >
            <circle
              cx="12"
              cy="12"
              r="10"
              stroke="#10b981"
              stroke-width="2"
            />
            <path
              d="M8 12l2 2 4-4"
              stroke="#10b981"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </div>
        <h3>{{ title }}</h3>
        <p class="message">
          {{ message }}
        </p>
      </div>

      <div class="modal-body">
        <slot></slot>
      </div>

      <div class="modal-footer">
        <button v-if="showAction" class="btn-action" @click="handleAction">
          {{ actionText }}
        </button>
        <button class="btn-close" @click="handleClose">
          {{ closeText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  show: boolean;
  title: string;
  message: string;
  actionText?: string;
  closeText?: string;
  showAction?: boolean;
  closeOnOverlay?: boolean;
}>();

const emit = defineEmits<{
  close: [];
  action: [];
}>();

const handleClose = () => {
  emit('close');
};

const handleAction = () => {
  emit('action');
};

const handleOverlayClick = () => {
  if (props.closeOnOverlay !== false) {
    handleClose();
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 32px;
  max-width: 480px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  text-align: center;
  margin-bottom: 24px;
}

.success-icon {
  display: inline-flex;
  animation: scaleIn 0.5s ease;
  margin-bottom: 16px;
}

@keyframes scaleIn {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.modal-header h3 {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
}

.message {
  font-size: 15px;
  color: #64748b;
  line-height: 1.6;
}

.modal-body {
  margin-bottom: 24px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn-action,
.btn-close {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  min-width: 120px;
}

.btn-action {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-action:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
}

.btn-close {
  background: white;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.btn-close:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    padding: 24px;
  }

  .modal-footer {
    flex-direction: column-reverse;
  }

  .btn-action,
  .btn-close {
    width: 100%;
  }
}
</style>
