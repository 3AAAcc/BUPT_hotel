<template>
  <div class="app-container">
    <!-- 优雅导航栏 -->
    <nav class="navbar">
      <!-- 左侧：系统标题 -->
      <div class="nav-left">
        <div class="nav-brand">
          <svg
            class="brand-icon"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
          >
            <path
              d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <path
              d="M9 22V12h6v10"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
          <h1>中央温控系统</h1>
        </div>
        <div class="nav-separator"></div>
        <div class="current-module">
          {{ getModuleName(currentView) }}
        </div>
      </div>

      <!-- 中间：导航菜单 -->
      <div class="nav-menu">
        <button
          v-if="hasPermission('room')"
          :class="['nav-item', { active: currentView === 'room' }]"
          @click="switchView('room')"
        >
          客房控制
        </button>
        <button
          v-if="hasPermission('admin')"
          :class="['nav-item', { active: currentView === 'admin' }]"
          @click="switchView('admin')"
        >
          管理监控
        </button>
        <button
          v-if="hasPermission('frontdesk')"
          :class="['nav-item', { active: currentView === 'frontdesk' }]"
          @click="switchView('frontdesk')"
        >
          前台结账
        </button>
        <button
          v-if="hasPermission('manager')"
          :class="['nav-item', { active: currentView === 'manager' }]"
          @click="switchView('manager')"
        >
          统计报表
        </button>
      </div>

      <!-- 右侧：用户信息和退出 -->
      <div class="nav-right">
        <div class="user-role">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
          >
            <circle
              cx="12"
              cy="8"
              r="4"
              stroke="currentColor"
              stroke-width="2"
            />
            <path
              d="M6 21C6 17.6863 8.68629 15 12 15C15.3137 15 18 17.6863 18 21"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
            />
          </svg>
          <span>{{ getRoleName(currentView) }}</span>
        </div>
        <button class="logout-btn" @click="onLogout">
          退出登录
        </button>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="main-content">
      <router-view
        v-bind="$attrs"
        :max-service-objects="maxServiceObjects"
        @refresh="$emit('refresh')"
        @switch-view="switchView"
      />
    </main>

    <!-- 紧凑型状态栏 -->
    <div class="status-bar">
      <div class="status-item serving">
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
        >
          <circle
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="2"
          />
          <path
            d="M12 6v6l4 2"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
          />
        </svg>
        <span class="status-label">服务队列</span>
        <span class="status-value">{{ servingCount }}</span>
      </div>
      <div class="status-divider"></div>
      <div class="status-item waiting">
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
        >
          <path
            d="M12 2v10l4.5 2.5"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
          />
          <circle
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="2"
          />
        </svg>
        <span class="status-label">等待队列</span>
        <span class="status-value">{{ waitingCount }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
type ViewType = 'room' | 'admin' | 'frontdesk' | 'manager';

defineOptions({
  inheritAttrs: false
});

defineProps<{
  userName: string;
  currentView: ViewType;
  totalRooms: number;
  maxServiceObjects: number;
  waitTime: number;
  servingCount: number;
  waitingCount: number;
  hasPermission: (view: ViewType) => boolean;
  switchView: (view: ViewType) => void;
  onLogout: () => void;
}>();

defineEmits<{
  refresh: [];
}>();

// 获取角色名称
const getRoleName = (view: ViewType): string => {
  const roleMap: Record<ViewType, string> = {
    'room': '客房',
    'admin': '管理员',
    'frontdesk': '前台',
    'manager': '经理'
  };
  return roleMap[view] || '';
};

// 获取模块名称
const getModuleName = (view: ViewType): string => {
  const moduleMap: Record<ViewType, string> = {
    'room': '客房控制',
    'admin': '管理监控',
    'frontdesk': '前台结账',
    'manager': '统计报表'
  };
  return moduleMap[view] || '';
};
</script>

<style scoped>
.app-container {
  width: 100%;
  height: 100vh;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 优雅导航栏样式 */
.navbar {
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
  height: 50px;
  z-index: 100;
}

/* 左侧区域 */
.nav-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-icon {
  color: #067ef5;
  flex-shrink: 0;
}

.nav-brand h1 {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  white-space: nowrap;
}

.nav-separator {
  width: 1px;
  height: 24px;
  background: #e5e7eb;
}

.current-module {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

/* 中间导航菜单 */
.nav-menu {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-item {
  padding: 6px 16px;
  background: transparent;
  border: none;
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  position: relative;
}

.nav-item:hover {
  color: #111827;
}

.nav-item.active {
  color: #067ef5;
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: -13px;
  left: 0;
  right: 0;
  height: 2px;
  background: #067ef5;
}

/* 右侧区域 */
.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.user-role {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #f9fafb;
  border-radius: 6px;
  font-size: 13px;
  color: #4b5563;
  font-weight: 500;
}

.user-role svg {
  color: #6b7280;
}

.logout-btn {
  padding: 6px 14px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  color: #6b7280;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.logout-btn:hover {
  background: #fef2f2;
  border-color: #fca5a5;
  color: #ef4444;
}

/* 主内容区 - 最大化 */
.main-content {
  flex: 1;
  padding: 20px 24px;
  background: #f9fafb;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;
}

/* 紧凑型状态栏 */
.status-bar {
  background: #ffffff;
  border-top: 1px solid #e2e8f0;
  padding: 8px 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 32px;
  flex-shrink: 0;
  height: 40px;
  box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.05);
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-item svg {
  flex-shrink: 0;
}

.status-item.serving svg {
  color: #059669;
}

.status-item.waiting svg {
  color: #d97706;
}

.status-label {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

.status-value {
  font-size: 18px;
  font-weight: 700;
  min-width: 24px;
  text-align: center;
}

.status-item.serving .status-value {
  color: #059669;
}

.status-item.waiting .status-value {
  color: #d97706;
}

.status-divider {
  width: 1px;
  height: 20px;
  background: #e2e8f0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .navbar {
    height: auto;
    padding: 8px 12px;
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .nav-left {
    justify-content: space-between;
  }

  .nav-brand h1 {
    font-size: 14px;
  }

  .brand-icon {
    width: 16px;
    height: 16px;
  }

  .current-module {
    font-size: 12px;
  }

  .nav-menu {
    width: 100%;
    justify-content: flex-start;
    overflow-x: auto;
    gap: 4px;
  }

  .nav-item {
    font-size: 12px;
    padding: 4px 10px;
  }

  .nav-item.active::after {
    display: none;
  }

  .nav-right {
    justify-content: space-between;
  }

  .user-role {
    font-size: 12px;
    padding: 4px 8px;
  }

  .user-role svg {
    width: 14px;
    height: 14px;
  }

  .logout-btn {
    padding: 4px 10px;
    font-size: 12px;
  }

  .main-content {
    padding: 12px;
  }

  .status-bar {
    padding: 6px 16px;
    gap: 20px;
  }

  .status-label {
    display: none;
  }

  .status-item svg {
    width: 16px;
    height: 16px;
  }
}
</style>
