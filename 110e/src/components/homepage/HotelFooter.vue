<template>
  <footer class="footer">
    <div class="container">
      <div class="footer-content">
        <div class="footer-brand">
          <h3>中央温控系统</h3>
          <p>智能化酒店管理解决方案</p>
        </div>
        <div class="footer-info">
          <p>© 2024 中央温控系统 - 让温控管理更简单</p>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
// 纯展示组件，无需特殊逻辑
</script>

<style scoped>
/* 底部 */
.footer {
  background: #1e293b;
  color: #94a3b8;
  padding: 48px 20px;
}

.container {
  max-width: 1700px;
  margin: 0 auto;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-brand h3 {
  color: #ffffff;
  margin: 0 0 8px 0;
  font-size: 1.25rem;
}

.footer-brand p {
  margin: 0;
  font-size: 0.9rem;
}

.footer-info p {
  margin: 0;
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .footer-content {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
}
</style>
