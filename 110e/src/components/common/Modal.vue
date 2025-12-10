<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="visible" class="modal-overlay" @click="handleOverlayClick">
        <Transition name="modal-slide">
          <div v-if="visible" class="modal-container" @click.stop>
            <div class="modal-header">
              <h3 class="modal-title">
                {{ title }}
              </h3>
              <button v-if="showClose" class="modal-close" @click="handleClose">
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <path
                    d="M18 6L6 18M6 6L18 18"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                  />
                </svg>
              </button>
            </div>

            <div class="modal-body">
              <slot>{{ content }}</slot>
            </div>

            <div v-if="showFooter" class="modal-footer">
              <slot name="footer">
                <button v-if="showCancel" class="modal-btn btn-cancel" @click="handleCancel">
                  {{ cancelText }}
                </button>
                <button class="modal-btn btn-confirm" @click="handleConfirm">
                  {{ confirmText }}
                </button>
              </slot>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  visible: boolean;
  title?: string;
  content?: string;
  showClose?: boolean;
  showFooter?: boolean;
  showCancel?: boolean;
  confirmText?: string;
  cancelText?: string;
  closeOnClickOverlay?: boolean;
}>(), {
  title: '提示',
  showClose: true,
  showFooter: true,
  showCancel: true,
  confirmText: '确定',
  cancelText: '取消',
  closeOnClickOverlay: true
});

const emit = defineEmits<{
  'update:visible': [value: boolean];
  confirm: [];
  cancel: [];
  close: [];
}>();

const handleClose = () => {
  emit('update:visible', false);
  emit('close');
};

const handleConfirm = () => {
  emit('confirm');
  handleClose();
};

const handleCancel = () => {
  emit('cancel');
  handleClose();
};

const handleOverlayClick = () => {
  if (props.closeOnClickOverlay) {
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
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 16px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.modal-close {
  padding: 4px;
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: #f1f5f9;
  color: #334155;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
  font-size: 15px;
  line-height: 1.6;
  color: #475569;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.modal-btn {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  min-width: 80px;
}

.btn-cancel {
  background: #f1f5f9;
  color: #64748b;
}

.btn-cancel:hover {
  background: #e2e8f0;
  color: #475569;
}

.btn-confirm {
  background: #067ef5;
  color: white;
  box-shadow: 0 2px 4px rgba(6, 126, 245, 0.2);
}

.btn-confirm:hover {
  background: #0369a1;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(6, 126, 245, 0.3);
}

/* 动画 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-slide-enter-active {
  transition: all 0.3s ease;
}

.modal-slide-leave-active {
  transition: all 0.2s ease;
}

.modal-slide-enter-from {
  opacity: 0;
  transform: translateY(-20px) scale(0.95);
}

.modal-slide-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

@media (max-width: 768px) {
  .modal-container {
    max-width: 90%;
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding-left: 16px;
    padding-right: 16px;
  }
}
</style>

