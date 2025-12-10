<template>
  <div class="homepage">
    <!-- 酒店标题 -->
    <header class="hotel-header">
      <h1 class="hotel-title">
        欢迎来到巴普特酒店
      </h1>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content">
      <!-- 酒店图片轮播 -->
      <HotelCarousel />

      <!-- 登录选项 -->
      <LoginOptions :on-login="onLogin" />
    </main>

    <!-- 系统概览 -->
    <SystemStats
      :total-rooms="totalRooms"
      :max-service-objects="maxServiceObjects"
      :serving-count="servingCount"
      :waiting-count="waitingCount"
    />

    <!-- 功能展示 -->
    <FeatureShowcase />

    <!-- 页脚 -->
    <HotelFooter />
  </div>
</template>

<script setup lang="ts">
// 导入子组件
import HotelCarousel from './HotelCarousel.vue';
import LoginOptions from './LoginOptions.vue';
import SystemStats from './SystemStats.vue';
import FeatureShowcase from './FeatureShowcase.vue';
import HotelFooter from './HotelFooter.vue';

// 用户角色类型
export type UserRole = 'guest' | 'admin' | 'frontdesk' | 'manager' | 'superadmin';

// Props
interface Props {
  onLogin: (role: UserRole) => void;
  totalRooms?: number;
  maxServiceObjects?: number;
  servingCount?: number;
  waitingCount?: number;
}

defineProps<Props>();
</script>

<style scoped>
.homepage {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

/* 酒店标题 */
.hotel-header {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  padding: 40px 20px;
  text-align: center;
  border-bottom: 3px solid #067ef5;
  box-shadow: 0 4px 12px rgba(6, 126, 245, 0.1);
  position: relative;
  overflow: hidden;
}

.hotel-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 200%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(6, 126, 245, 0.05), transparent);
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}

.hotel-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
  letter-spacing: 1px;
  background: linear-gradient(135deg, #067ef5 0%, #0369a1 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: fadeInDown 0.6s ease-out;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 主内容区域 */
.main-content {
  max-width: 1700px;
  margin: 0 auto;
  padding: 40px 20px;
  animation: slideInUp 0.8s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hotel-title {
    font-size: 2rem;
  }

  .main-content {
    padding: 20px 16px;
  }
}

@media (max-width: 480px) {
  .hotel-header {
    padding: 24px 16px;
  }

  .hotel-title {
    font-size: 1.75rem;
  }

  .main-content {
    padding: 16px 12px;
  }
}
</style>
