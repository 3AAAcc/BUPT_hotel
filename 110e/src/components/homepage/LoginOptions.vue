<template>
  <div class="login-section">
    <p class="login-intro">
      我们的酒店配备智能中央空调系统，为您提供贴心的个性化服务，您个人的舒适，我们用心的呵护，让您有宾至如归的体验。
      不论是商务差旅还是休闲度假，我们都能满足您对舒适的各种需求，让我们一起开启温馨的旅程吧！
    </p>

    <div class="login-options">
      <!-- 顾客入口 -->
      <div class="login-card guest-card">
        <div class="card-icon guest-icon"></div>
        <h3>顾客入口</h3>
        <p>进入房间，享受空调，开启您的美好一天</p>
        <button class="login-btn guest-btn" @click="handleQuickLogin('guest')">
          进入客房系统
        </button>
      </div>

      <!-- 管理员入口 -->
      <div class="login-card admin-card">
        <div class="card-icon admin-icon"></div>
        <h3>管理员入口</h3>
        <p>监控设备状态，维护系统运行，查看数据统计</p>
        <button class="login-btn admin-btn" @click="handleQuickLogin('admin')">
          进入管理系统
        </button>
      </div>

      <!-- 前台入口 -->
      <div class="login-card frontdesk-card">
        <div class="card-icon frontdesk-icon"></div>
        <h3>前台入口</h3>
        <p>办理入住退房手续，费用结算，客户服务</p>
        <button class="login-btn frontdesk-btn" @click="handleQuickLogin('frontdesk')">
          进入前台系统
        </button>
      </div>

      <!-- 经理入口 -->
      <div class="login-card manager-card">
        <div class="card-icon manager-icon"></div>
        <h3>经理入口</h3>
        <p>查看经营数据，财务报表，系统全面管理</p>
        <button class="login-btn manager-btn" @click="handleQuickLogin('manager')">
          进入管理后台
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 用户角色类型
export type UserRole = 'guest' | 'admin' | 'frontdesk' | 'manager' | 'superadmin';

// Props
interface Props {
  onLogin: (role: UserRole) => void;
}

const props = defineProps<Props>();

// 快速登录处理
const handleQuickLogin = (role: UserRole) => {
  props.onLogin(role);
};
</script>

<style scoped>
/* 登录选项区域 */
.login-section {
  text-align: center;
  margin-bottom: 60px;
}

.login-intro {
  font-size: 1.1rem;
  color: #475569;
  line-height: 1.8;
  margin: 0 0 48px 0;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.login-options {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  max-width: 1700px;
  margin: 0 auto;
}

.login-card {
  background: #ffffff;
  border-radius: 20px;
  padding: 40px 32px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 2px solid #f1f5f9;
  transition: all 0.3s ease;
}

.login-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  border-color: #e2e8f0;
}

.card-icon {
  width: 60px;
  height: 60px;
  margin: 0 auto 20px;
  display: block;
  border-radius: 12px;
  position: relative;
}

/* 不同角色的图标样式 */
.guest-icon {
  background: #dbeafe;
  border: 2px solid #3b82f6;
}

.guest-icon::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 24px;
  height: 24px;
  background: #3b82f6;
  mask: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>') center/contain no-repeat;
}

.admin-icon {
  background: #dcfce7;
  border: 2px solid #10b981;
}

.admin-icon::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 24px;
  height: 24px;
  background: #10b981;
  mask: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.6 14.8,10V11H16.2V16H7.8V11H9.2V10C9.2,8.6 10.6,7 12,7M12,8.2C11.2,8.2 10.4,8.7 10.4,10V11H13.6V10C13.6,8.7 12.8,8.2 12,8.2Z"/></svg>') center/contain no-repeat;
}

.frontdesk-icon {
  background: #fef3c7;
  border: 2px solid #f59e0b;
}

.frontdesk-icon::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 24px;
  height: 24px;
  background: #f59e0b;
  mask: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path d="M2 17h20v2H2zm1.15-4.05L4 11l.85 1.95L6.8 13l-1.95.85L4 15.8l-.85-1.95L1.2 13l1.95-.85M9.85 12.65L11 10l1.15 2.65L15 13l-2.85 .35L11 16l-1.15-2.65L7 13l2.85-.35M18.85 5.95L20 4l1.15 1.95L23 6l-1.85.05L20 8l-1.15-1.95L17 6l1.85-.05z"/></svg>') center/contain no-repeat;
}

.manager-icon {
  background: #ede9fe;
  border: 2px solid #8b5cf6;
}

.manager-icon::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 24px;
  height: 24px;
  background: #8b5cf6;
  mask: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path d="M3,3H21A1,1 0 0,1 22,4V20A1,1 0 0,1 21,21H3A1,1 0 0,1 2,20V4A1,1 0 0,1 3,3M4,5V19H20V5H4M6,7H18V9H6V7M6,11H18V13H6V11M6,15H18V17H6V15Z"/></svg>') center/contain no-repeat;
}

.login-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 16px 0;
}

.login-card p {
  color: #64748b;
  font-size: 1rem;
  line-height: 1.6;
  margin: 0 0 32px 0;
}

.login-btn {
  width: 100%;
  padding: 16px 24px;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 0.5px;
}

.guest-btn {
  background: linear-gradient(135deg, #067ef5 0%, #0369a1 100%);
  color: white;
}

.guest-btn:hover {
  background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(6, 126, 245, 0.3);
}

.admin-btn {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  color: white;
}

.admin-btn:hover {
  background: linear-gradient(135deg, #047857 0%, #065f46 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(5, 150, 105, 0.3);
}

.frontdesk-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.frontdesk-btn:hover {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.3);
}

.manager-btn {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
}

.manager-btn:hover {
  background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(139, 92, 246, 0.3);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .login-options {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .login-options {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .login-card {
    padding: 24px 20px;
  }

  .login-intro {
    font-size: 1rem;
    margin-bottom: 32px;
  }
}
</style>
