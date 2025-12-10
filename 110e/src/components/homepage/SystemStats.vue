<template>
  <section class="system-overview">
    <div class="container">
      <h2 class="section-title">
        系统实时状态
      </h2>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon hotel-icon"></div>
          <div class="stat-content">
            <div class="stat-number">
              {{ totalRooms }}
            </div>
            <div class="stat-label">
              总房间数
            </div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon service-icon"></div>
          <div class="stat-content">
            <div class="stat-number">
              {{ maxServiceObjects }}
            </div>
            <div class="stat-label">
              最大服务数
            </div>
          </div>
        </div>
        <div class="stat-card active">
          <div class="stat-icon active-icon"></div>
          <div class="stat-content">
            <div class="stat-number">
              {{ servingCount }}
            </div>
            <div class="stat-label">
              正在服务
            </div>
          </div>
        </div>
        <div class="stat-card waiting">
          <div class="stat-icon waiting-icon"></div>
          <div class="stat-content">
            <div class="stat-number">
              {{ waitingCount }}
            </div>
            <div class="stat-label">
              等待队列
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
// Props
interface Props {
  totalRooms?: number;
  maxServiceObjects?: number;
  servingCount?: number;
  waitingCount?: number;
}

withDefaults(defineProps<Props>(), {
  totalRooms: 0,
  maxServiceObjects: 0,
  servingCount: 0,
  waitingCount: 0
});
</script>

<style scoped>
/* 系统概览 */
.system-overview {
  background: #ffffff;
  padding: 80px 20px;
}

.container {
  max-width: 1700px;
  margin: 0 auto;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e293b;
  text-align: center;
  margin: 0 0 48px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.stat-card {
  display: flex;
  gap: 20px;
  align-items: center;
  padding: 24px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 16px;
  border: 2px solid #e2e8f0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  animation: slideInRight 0.6s ease-out;
  animation-fill-mode: both;
}

.stat-card:nth-child(1) { animation-delay: 0.1s; }
.stat-card:nth-child(2) { animation-delay: 0.2s; }
.stat-card:nth-child(3) { animation-delay: 0.3s; }
.stat-card:nth-child(4) { animation-delay: 0.4s; }

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(6, 126, 245, 0.15);
  border-color: #067ef5;
}

.stat-card.active {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  color: white;
  border-color: #059669;
  box-shadow: 0 6px 16px rgba(5, 150, 105, 0.2);
}

.stat-card.waiting {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  border-color: #f59e0b;
  box-shadow: 0 6px 16px rgba(245, 158, 11, 0.2);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  position: relative;
  flex-shrink: 0;
}

/* 图标样式 */
.hotel-icon {
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border: 2px solid #067ef5;
  box-shadow: 0 2px 8px rgba(6, 126, 245, 0.1);
}

.hotel-icon::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 28px;
  height: 28px;
  background: #0284c7;
  mask: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path d="M7,13H9V19H7V13M14,13H16V19H14V13M12,7H22V20H2V7H12M12,2L17,7H12V2Z"/></svg>') center/contain no-repeat;
}

.service-icon {
  background: #f3e8ff;
  border: 2px solid #7c3aed;
}

.service-icon::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 28px;
  height: 28px;
  background: #7c3aed;
  mask: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>') center/contain no-repeat;
}

.active-icon {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  border: 2px solid #059669;
  box-shadow: 0 2px 8px rgba(5, 150, 105, 0.1);
}

.active-icon::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 28px;
  height: 28px;
  background: #22c55e;
  mask: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path d="M9,20.42L2.79,14.21L5.62,11.38L9,14.77L18.88,4.88L21.71,7.71L9,20.42Z"/></svg>') center/contain no-repeat;
}

.waiting-icon {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border: 2px solid #f59e0b;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.1);
}

.waiting-icon::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 28px;
  height: 28px;
  background: #f59e0b;
  mask: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M16.2,16.2L11,13V7H12.5V12.2L17,14.7L16.2,16.2Z"/></svg>') center/contain no-repeat;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0 0 4px 0;
  background: linear-gradient(135deg, #067ef5 0%, #0369a1 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-card.active .stat-number,
.stat-card.waiting .stat-number {
  background: none;
  -webkit-text-fill-color: white;
}

.stat-label {
  font-size: 0.95rem;
  opacity: 0.8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .section-title {
    font-size: 2rem;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
}

@media (max-width: 480px) {
  .system-overview {
    padding: 60px 16px;
  }

  .section-title {
    font-size: 1.75rem;
  }
}
</style>
