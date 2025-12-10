<script setup lang="ts">
import { ref } from 'vue';

// 用户角色类型
export type UserRole = 'guest' | 'admin' | 'frontdesk' | 'manager' | 'superadmin';

// 角色配置
const roles = [
  { value: 'guest' as UserRole, label: '房客', description: '客房控制', shortName: '房' },
  { value: 'admin' as UserRole, label: '管理员', description: '管理监控', shortName: '管' },
  { value: 'frontdesk' as UserRole, label: '前台', description: '前台结账', shortName: '台' },
  { value: 'manager' as UserRole, label: '经理', description: '统计报表', shortName: '经' },
  { value: 'superadmin' as UserRole, label: '超级管理员', description: '全部权限', shortName: '超' }
];

// Props
interface Props {
  onLogin: (role: UserRole) => void;
}

const props = defineProps<Props>();

// 状态
const selectedRole = ref<UserRole>('guest');
const isAnimating = ref(false);

// 登录处理
const handleLogin = () => {
  if (!selectedRole.value) return;

  isAnimating.value = true;

  // 延迟执行登录，增加交互体验
  setTimeout(() => {
    props.onLogin(selectedRole.value);
    isAnimating.value = false;
  }, 300);
};

// 获取当前选择的角色信息
const selectedRoleInfo = () => {
  return roles.find(r => r.value === selectedRole.value);
};
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="logo">
          <div class="logo-icon">
            <svg
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <rect
                x="3"
                y="4"
                width="18"
                height="16"
                rx="2"
                stroke="currentColor"
                stroke-width="2"
              />
              <path
                d="M8 9H16M8 13H13"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
              />
            </svg>
          </div>
          <h1>中央温控系统</h1>
          <p class="subtitle">
            智能空调管理平台
          </p>
        </div>
      </div>

      <div class="login-body">
        <div class="form-group">
          <label class="form-label">
            <span class="label-text">请选择您的身份</span>
          </label>

          <div class="role-selector">
            <select v-model="selectedRole" class="role-select">
              <option
                v-for="role in roles"
                :key="role.value"
                :value="role.value"
              >
                {{ role.label }} - {{ role.description }}
              </option>
            </select>
          </div>

          <!-- 角色卡片展示 -->
          <div class="role-info-card">
            <div class="role-icon">
              {{ selectedRoleInfo()?.shortName }}
            </div>
            <div class="role-details">
              <h3>{{ selectedRoleInfo()?.label }}</h3>
              <p>{{ selectedRoleInfo()?.description }}</p>
            </div>
          </div>
        </div>

        <button
          class="login-btn"
          :disabled="isAnimating"
          @click="handleLogin"
        >
          <span v-if="!isAnimating">进入系统</span>
          <span v-else>登录中...</span>
        </button>
      </div>

      <div class="login-footer">
        <p class="footer-text">
          © 2024 中央温控系统
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  position: relative;
  width: 100%;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f8f9fb;
  padding: 20px;
}

.login-card {
  position: relative;
  width: 100%;
  max-width: 480px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  animation: fadeInUp 0.4s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  padding: 48px 40px 36px;
  text-align: center;
  background: #ffffff;
  border-bottom: 2px solid #f0f4f8;
}

.logo {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f7ff;
  border-radius: 16px;
  color: #067ef5;
  margin-bottom: 4px;
}

.logo h1 {
  font-size: 26px;
  font-weight: 600;
  margin: 0;
  color: #1e293b;
  letter-spacing: 0.5px;
}

.subtitle {
  margin: 0;
  font-size: 14px;
  color: #64748b;
  font-weight: 400;
}

.login-body {
  padding: 40px 40px 36px;
}

.form-group {
  margin-bottom: 0;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 12px;
}

.label-text {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

.role-selector {
  position: relative;
  margin-bottom: 20px;
}

.role-select {
  width: 100%;
  padding: 12px 16px;
  font-size: 15px;
  color: #1f2937;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  outline: none;
  cursor: pointer;
  transition: all 0.2s ease;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='%2364748b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 16px center;
  padding-right: 40px;
}

.role-select:hover {
  border-color: #cbd5e1;
  background-color: #ffffff;
}

.role-select:focus {
  border-color: #067ef5;
  background-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(6, 126, 245, 0.1);
}

.role-info-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s ease;
}

.role-icon {
  font-size: 24px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
  border-radius: 10px;
  border: 2px solid #e5e7eb;
  color: #067ef5;
  font-weight: 600;
  flex-shrink: 0;
}

.role-details {
  flex: 1;
}

.role-details h3 {
  font-size: 17px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 6px 0;
}

.role-details p {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.login-btn {
  width: 100%;
  padding: 14px;
  margin-top: 28px;
  font-size: 15px;
  font-weight: 500;
  color: #ffffff;
  background: #067ef5;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(6, 126, 245, 0.2);
  letter-spacing: 0.3px;
}

.login-btn:hover {
  background: #0570e0;
  box-shadow: 0 4px 12px rgba(6, 126, 245, 0.3);
  transform: translateY(-1px);
}

.login-btn:active {
  transform: translateY(0);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.login-footer {
  padding: 20px 40px;
  text-align: center;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
}

.footer-text {
  margin: 0;
  font-size: 13px;
  color: #9ca3af;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    padding: 15px;
  }

  .login-card {
    border-radius: 12px;
  }

  .login-header {
    padding: 36px 24px 28px;
  }

  .logo h1 {
    font-size: 24px;
  }

  .logo-icon {
    width: 56px;
    height: 56px;
  }

  .login-body {
    padding: 32px 24px 28px;
  }

  .role-info-card {
    padding: 16px;
  }

  .role-icon {
    width: 52px;
    height: 52px;
    font-size: 20px;
  }

  .role-details h3 {
    font-size: 16px;
  }

  .role-details p {
    font-size: 13px;
  }

  .login-footer {
    padding: 16px 24px;
  }

  .footer-text {
    font-size: 12px;
  }
}
</style>
