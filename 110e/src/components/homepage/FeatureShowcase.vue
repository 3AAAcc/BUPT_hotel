<template>
  <section class="features">
    <div class="container">
      <h2 class="section-title">
        核心功能
      </h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-header">
            <div class="feature-icon-large room-icon"></div>
            <h3>客房控制</h3>
          </div>
          <p>房客可以自主调节房间温度、风速，享受个性化舒适体验</p>
          <ul class="feature-list">
            <li>温度精准调节</li>
            <li>多档风速选择</li>
            <li>实时状态显示</li>
          </ul>
        </div>

        <div class="feature-card">
          <div class="feature-header">
            <div class="feature-icon-large monitor-icon"></div>
            <h3>管理监控</h3>
          </div>
          <p>管理员实时监控所有房间状态，统一调度系统资源</p>
          <ul class="feature-list">
            <li>实时监控面板</li>
            <li>服务队列管理</li>
            <li>系统状态预警</li>
          </ul>
        </div>

        <div class="feature-card">
          <div class="feature-header">
            <div class="feature-icon-large payment-icon"></div>
            <h3>前台结账</h3>
          </div>
          <p>前台人员便捷办理入住退房，自动计算空调使用费用</p>
          <ul class="feature-list">
            <li>快速入住登记</li>
            <li>自动费用结算</li>
            <li>详细账单明细</li>
          </ul>
        </div>

        <div class="feature-card">
          <div class="feature-header">
            <div class="feature-icon-large analytics-icon"></div>
            <h3>统计报表</h3>
          </div>
          <p>经理查看详细的使用统计和财务报表，辅助决策管理</p>
          <ul class="feature-list">
            <li>使用量统计</li>
            <li>收入分析报告</li>
            <li>趋势预测图表</li>
          </ul>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
// 纯展示组件，无需特殊逻辑
</script>

<style scoped>
/* 功能模块 */
.features {
  background: #f8fafc;
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

.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 32px;
}

.feature-card {
  background: #ffffff;
  padding: 32px;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  border-color: #cbd5e1;
}

.feature-header {
  margin-bottom: 20px;
}

.feature-icon-large {
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
  border-radius: 16px;
  position: relative;
  display: block;
}

/* 功能图标样式 */
.room-icon {
  background: #dbeafe;
  border: 2px solid #3b82f6;
}

.room-icon::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 36px;
  height: 36px;
  background: #3b82f6;
  mask: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path d="M12,3L2,12H5V20H19V12H22L12,3M7,18V10.99L12,6L17,11V18H15V12H9V18H7Z"/></svg>') center/contain no-repeat;
}

.monitor-icon {
  background: #dcfce7;
  border: 2px solid #10b981;
}

.monitor-icon::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 36px;
  height: 36px;
  background: #10b981;
  mask: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path d="M21,16H3V4H21M21,2H3C1.89,2 1,2.89 1,4V16A2,2 0 0,0 3,18H10V20H8V22H16V20H14V18H21A2,2 0 0,0 23,16V4C23,2.89 22.1,2 21,2Z"/></svg>') center/contain no-repeat;
}

.payment-icon {
  background: #fef3c7;
  border: 2px solid #f59e0b;
}

.payment-icon::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 36px;
  height: 36px;
  background: #f59e0b;
  mask: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path d="M20,4H4C2.89,4 2,4.89 2,6V18A2,2 0 0,0 4,20H20A2,2 0 0,0 22,18V6C22,4.89 21.1,4 20,4M20,18H4V12H20V18M20,8H4V6H20V8Z"/></svg>') center/contain no-repeat;
}

.analytics-icon {
  background: #ede9fe;
  border: 2px solid #8b5cf6;
}

.analytics-icon::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 36px;
  height: 36px;
  background: #8b5cf6;
  mask: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24"><path d="M22,21H2V3H4V19H6V17H10V19H12V16H16V19H18V17H22V21M16,15H12V8H16V15M10,15H6V12H10V15Z"/></svg>') center/contain no-repeat;
}

.feature-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 16px 0;
}

.feature-card p {
  color: #64748b;
  line-height: 1.6;
  margin: 0 0 20px 0;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-list li {
  padding: 8px 0;
  color: #475569;
  position: relative;
  padding-left: 20px;
}

.feature-list li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #059669;
  font-weight: bold;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }
}

@media (max-width: 768px) {
  .section-title {
    font-size: 2rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}

@media (max-width: 480px) {
  .features {
    padding: 60px 16px;
  }

  .section-title {
    font-size: 1.75rem;
  }
}
</style>
