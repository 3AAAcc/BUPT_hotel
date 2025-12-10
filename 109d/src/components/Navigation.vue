<template>
  <el-menu
    :default-active="activeIndex"
    mode="horizontal"
    router
    class="navigation-menu"
  >
    <el-menu-item index="/customer">
      <el-icon><User /></el-icon>
      <span>客户界面</span>
    </el-menu-item>
    <el-menu-item index="/reception">
      <el-icon><OfficeBuilding /></el-icon>
      <span>前台管理</span>
    </el-menu-item>
    <el-menu-item index="/admin">
      <el-icon><Setting /></el-icon>
      <span>监控</span>
    </el-menu-item>
    <el-menu-item index="/manager">
      <el-icon><DataAnalysis /></el-icon>
      <span>经理报表</span>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { User, OfficeBuilding, Setting, DataAnalysis } from '@element-plus/icons-vue'

const route = useRoute()
const activeIndex = computed(() => route.path)
</script>

<style scoped>
.navigation-menu {
  border-bottom: 1px solid #e4e7ed;
  background: white;
}
</style>

