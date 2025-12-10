<template>
  <div class="admin-page">
    <el-container>
      <el-header>
        <h1>监控界面</h1>
        <el-button type="danger" @click="handleResetDatabase" :loading="resetLoading">
          重置数据库
        </el-button>
      </el-header>

      <el-main>
        <el-card>
          <template #header>
            <span>所有房间状态</span>
            <el-button type="primary" size="small" @click="loadRoomsStatus" :loading="loading" style="float: right">
              刷新
            </el-button>
          </template>

          <el-table :data="roomsStatus" v-loading="loading" border>
            <el-table-column prop="id" label="房间号" width="80" fixed />
            <el-table-column prop="currentTemp" label="当前温度" width="100">
              <template #default="{ row }">
                {{ row.currentTemp }}°C
              </template>
            </el-table-column>
            <el-table-column prop="targetTemp" label="目标温度" width="100">
              <template #default="{ row }">
                {{ row.targetTemp }}°C
              </template>
            </el-table-column>
            <el-table-column prop="ac_on" label="空调状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.ac_on ? 'success' : 'info'">
                  {{ row.ac_on ? '运行中' : '已关闭' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="ac_mode" label="模式" width="100">
              <template #default="{ row }">
                {{ row.ac_mode === 'COOLING' ? '制冷' : '制热' }}
              </template>
            </el-table-column>
            <el-table-column prop="fan_speed" label="风速" width="100">
              <template #default="{ row }">
                {{ getFanSpeedText(row.fan_speed) }}
              </template>
            </el-table-column>
            <el-table-column prop="queueState" label="队列状态" width="120">
              <template #default="{ row }">
                <el-tag :type="getQueueStateType(row.queueState)">
                  {{ getQueueStateText(row.queueState) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="total_cost" label="总费用" width="120">
              <template #default="{ row }">
                ¥{{ row.total_cost?.toFixed(2) || '0.00' }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAllRoomsStatus, resetDatabase } from '@/api/admin'

const roomsStatus = ref([])
const loading = ref(false)
const resetLoading = ref(false)
let statusInterval = null

// 加载房间状态
async function loadRoomsStatus() {
  loading.value = true
  try {
    roomsStatus.value = await getAllRoomsStatus()
  } catch (error) {
    ElMessage.error('加载房间状态失败')
  } finally {
    loading.value = false
  }
}


// 获取风速文本
function getFanSpeedText(speed) {
  const map = { 'LOW': '低风', 'MEDIUM': '中风', 'HIGH': '高风' }
  return map[speed] || speed
}

// 获取队列状态文本
function getQueueStateText(state) {
  const map = {
    'IDLE': '空闲',
    'SERVING': '服务中',
    'WAITING': '等待中',
    'PAUSED': '已暂停'
  }
  return map[state] || state
}

// 获取队列状态类型
function getQueueStateType(state) {
  const map = {
    'IDLE': 'info',
    'SERVING': 'success',
    'WAITING': 'warning',
    'PAUSED': ''
  }
  return map[state] || 'info'
}

// 重置数据库
async function handleResetDatabase() {
  try {
    await ElMessageBox.confirm('确认重置数据库？此操作将清空所有数据！', '警告', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })

    resetLoading.value = true
    try {
      await resetDatabase()
      ElMessage.success('数据库已重置')
      await loadRoomsStatus()
    } catch (error) {
      ElMessage.error('重置失败')
    } finally {
      resetLoading.value = false
    }
  } catch {
    // 用户取消
  }
}

onMounted(() => {
  loadRoomsStatus()
  // 自动刷新
  statusInterval = setInterval(() => {
    loadRoomsStatus()
  }, 5000)
})

onUnmounted(() => {
  if (statusInterval) {
    clearInterval(statusInterval)
  }
})
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.el-header {
  background: white;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: nowrap;
}

.el-header h1 {
  margin: 0;
  color: #303133;
  white-space: nowrap;
}
</style>

