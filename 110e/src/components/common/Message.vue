<template>
  <Teleport to="body">
    <Transition name="message-fade">
      <div v-if="visible" :class="['message-container', `message-${type}`]">
        <div class="message-icon">
          <svg
            v-if="type === 'success'"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
          >
            <path
              d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
            />
          </svg>
          <svg
            v-else-if="type === 'error'"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
          >
            <path
              d="M12 8V12M12 16H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
            />
          </svg>
          <svg
            v-else-if="type === 'warning'"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
          >
            <path
              d="M12 9V13M12 17H12.01M3 12L10.5 3.5L21 12L10.5 20.5L3 12Z"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
            />
          </svg>
          <svg
            v-else
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
          >
            <path
              d="M13 16H12V12H11M12 8H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
            />
          </svg>
        </div>
        <div class="message-content">
          {{ message }}
        </div>
        <button v-if="closable" class="message-close" @click="close">
          <svg
            width="16"
            height="16"
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
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

export type MessageType = 'success' | 'error' | 'warning' | 'info';

const props = withDefaults(defineProps<{
  message: string;
  type?: MessageType;
  duration?: number;
  closable?: boolean;
}>(), {
  type: 'info',
  duration: 3000,
  closable: true
});

const emit = defineEmits<{
  close: [];
}>();

const visible = ref(false);
let timer: ReturnType<typeof setTimeout> | null = null;

const close = () => {
  visible.value = false;
  emit('close');
};

onMounted(() => {
  visible.value = true;

  if (props.duration > 0) {
    timer = setTimeout(() => {
      close();
    }, props.duration);
  }
});
</script>

<style scoped>
.message-container {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10000;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  min-width: 300px;
  max-width: 500px;
  font-size: 14px;
  font-weight: 500;
}

.message-success {
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border: 1px solid #a7f3d0;
  color: #047857;
}

.message-error {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border: 1px solid #fecaca;
  color: #dc2626;
}

.message-warning {
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
  border: 1px solid #fde68a;
  color: #d97706;
}

.message-info {
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border: 1px solid #bfdbfe;
  color: #2563eb;
}

.message-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message-content {
  flex: 1;
  line-height: 1.5;
}

.message-close {
  flex-shrink: 0;
  padding: 4px;
  border: none;
  background: transparent;
  color: currentColor;
  opacity: 0.6;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message-close:hover {
  opacity: 1;
  background: rgba(0, 0, 0, 0.05);
}

/* 动画 */
.message-fade-enter-active {
  transition: all 0.3s ease;
}

.message-fade-leave-active {
  transition: all 0.2s ease;
}

.message-fade-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

.message-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) scale(0.9);
}

@media (max-width: 768px) {
  .message-container {
    min-width: auto;
    max-width: calc(100vw - 40px);
    left: 20px;
    right: 20px;
    transform: none;
  }

  .message-fade-enter-from {
    transform: translateY(-20px);
  }

  .message-fade-leave-to {
    transform: scale(0.9);
  }
}
</style>

