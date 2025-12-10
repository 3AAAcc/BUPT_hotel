import { createApp, h } from 'vue';
import Message, { type MessageType } from '../components/common/Message.vue';
import Modal from '../components/common/Modal.vue';

// 消息提示
export function showMessage(message: string, type: MessageType = 'info', duration = 3000) {
  const container = document.createElement('div');
  document.body.appendChild(container);

  const app = createApp({
    render() {
      return h(Message, {
        message,
        type,
        duration,
        onClose: () => {
          setTimeout(() => {
            app.unmount();
            document.body.removeChild(container);
          }, 300);
        }
      });
    }
  });

  app.mount(container);
}

// 成功提示
export function showSuccess(message: string, duration = 3000) {
  showMessage(message, 'success', duration);
}

// 错误提示
export function showError(message: string, duration = 3000) {
  showMessage(message, 'error', duration);
}

// 警告提示
export function showWarning(message: string, duration = 3000) {
  showMessage(message, 'warning', duration);
}

// 信息提示
export function showInfo(message: string, duration = 3000) {
  showMessage(message, 'info', duration);
}

// 确认对话框
export function showConfirm(
  title: string,
  content: string,
  options?: {
    confirmText?: string;
    cancelText?: string;
    type?: 'info' | 'warning' | 'danger';
  }
): Promise<boolean> {
  return new Promise((resolve) => {
    const container = document.createElement('div');
    document.body.appendChild(container);

    const app = createApp({
      data() {
        return {
          visible: true
        };
      },
      render() {
        return h(Modal, {
          visible: this.visible,
          'onUpdate:visible': (val: boolean) => {
            this.visible = val;
          },
          title,
          content,
          confirmText: options?.confirmText || '确定',
          cancelText: options?.cancelText || '取消',
          showCancel: true,
          closeOnClickOverlay: false,
          onConfirm: () => {
            this.visible = false;
            setTimeout(() => {
              app.unmount();
              document.body.removeChild(container);
              resolve(true);
            }, 300);
          },
          onCancel: () => {
            this.visible = false;
            setTimeout(() => {
              app.unmount();
              document.body.removeChild(container);
              resolve(false);
            }, 300);
          },
          onClose: () => {
            setTimeout(() => {
              app.unmount();
              document.body.removeChild(container);
              resolve(false);
            }, 300);
          }
        });
      }
    });

    app.mount(container);
  });
}

// 提示对话框
export function showAlert(title: string, content: string, confirmText = '确定'): Promise<void> {
  return new Promise((resolve) => {
    const container = document.createElement('div');
    document.body.appendChild(container);

    const app = createApp({
      data() {
        return {
          visible: true
        };
      },
      render() {
        return h(Modal, {
          visible: this.visible,
          'onUpdate:visible': (val: boolean) => {
            this.visible = val;
          },
          title,
          content,
          confirmText,
          showCancel: false,
          onConfirm: () => {
            this.visible = false;
            setTimeout(() => {
              app.unmount();
              document.body.removeChild(container);
              resolve();
            }, 300);
          },
          onClose: () => {
            setTimeout(() => {
              app.unmount();
              document.body.removeChild(container);
              resolve();
            }, 300);
          }
        });
      }
    });

    app.mount(container);
  });
}

// 默认导出
export default {
  showMessage,
  showSuccess,
  showError,
  showWarning,
  showInfo,
  showConfirm,
  showAlert
};

