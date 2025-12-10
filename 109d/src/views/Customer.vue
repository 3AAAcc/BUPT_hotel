<template>
  <div class="customer-page">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>客户空调控制界面</h1>
          <el-select v-model="selectedRoomId" placeholder="选择房间" @change="handleRoomChange">
            <el-option
              v-for="room in rooms"
              :key="room.id"
              :label="`房间 ${room.id}`"
              :value="room.id"
            />
          </el-select>
        </div>
      </el-header>
      
      <el-main v-if="selectedRoomId">
        <el-card class="status-card">
          <template #header>
            <span>房间 {{ selectedRoomId }} 状态</span>
            <el-button type="primary" size="small" @click="refreshState" :loading="loading" style="float: right">
              刷新
            </el-button>
          </template>
          
          <div v-if="roomState" class="status-content">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="当前温度">
                {{ roomState.currentTemp }}°C
              </el-descriptions-item>
              <el-descriptions-item label="目标温度">
                {{ roomState.targetTemp }}°C
              </el-descriptions-item>
              <el-descriptions-item label="空调状态">
                <el-tag :type="roomState.ac_on ? 'success' : 'info'">
                  {{ roomState.ac_on ? '运行中' : '已关闭' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="模式">
                {{ roomState.ac_mode === 'COOLING' ? '制冷' : '制热' }}
              </el-descriptions-item>
              <el-descriptions-item label="风速">
                {{ getFanSpeedText(roomState.fan_speed) }}
              </el-descriptions-item>
              <el-descriptions-item label="队列状态">
                <el-tag :type="getQueueStateType(roomState.queueState)">
                  {{ getQueueStateText(roomState.queueState) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="当前费用">
                ¥{{ roomState.current_cost?.toFixed(2) || '0.00' }}
              </el-descriptions-item>
              <el-descriptions-item label="总费用">
                ¥{{ roomState.total_cost?.toFixed(2) || '0.00' }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>

        <el-card class="control-card">
          <template #header>
            <span>空调控制</span>
          </template>
          
          <div class="control-buttons">
            <el-button
              :type="roomState?.ac_on ? 'danger' : 'success'"
              size="large"
              @click="togglePower"
              :loading="powerLoading"
            >
              {{ roomState?.ac_on ? '关闭空调' : '开启空调' }}
            </el-button>
          </div>

          <el-divider />

          <div class="temp-control">
            <h3>温度设置</h3>
            <el-slider
              v-model="targetTemp"
              :min="getMinTemp()"
              :max="getMaxTemp()"
              :step="1"
              show-input
              @change="handleTempChange"
            />
          </div>

          <el-divider />

          <div class="speed-control">
            <h3>风速设置</h3>
            <el-radio-group v-model="fanSpeed" @change="handleSpeedChange">
              <el-radio-button label="LOW">低风</el-radio-button>
              <el-radio-button label="MEDIUM">中风</el-radio-button>
              <el-radio-button label="HIGH">高风</el-radio-button>
            </el-radio-group>
          </div>

          <el-divider />

          <div class="mode-control">
            <h3>模式设置</h3>
            <el-radio-group v-model="acMode" @change="handleModeChange">
              <el-radio-button label="COOLING">制冷</el-radio-button>
              <el-radio-button label="HEATING">制热</el-radio-button>
            </el-radio-group>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoomStore } from '@/store/room'
import { useACStore } from '@/store/ac'
import { powerOn, powerOff, changeTemp, changeSpeed, changeMode } from '@/api/ac'

const roomStore = useRoomStore()
const acStore = useACStore()

const selectedRoomId = ref(null)
const rooms = ref([])
const roomState = ref(null)
const loading = ref(false)
const powerLoading = ref(false)

const targetTemp = ref(25)
const fanSpeed = ref('MEDIUM')
const acMode = ref('COOLING')

// 获取房间列表
async function loadRooms() {
  try {
    const all = await roomStore.fetchAllRooms()
    const occupiedRooms = (all || []).filter(r => r.status === 'OCCUPIED')
    rooms.value = occupiedRooms
    
    // 如果当前选中的房间已退房，清空选择
    if (selectedRoomId.value) {
      const stillOccupied = occupiedRooms.some(r => r.id === selectedRoomId.value)
      if (!stillOccupied) {
        selectedRoomId.value = null
        roomState.value = null
      }
    }
    
    if (rooms.value.length === 0) {
      selectedRoomId.value = null
      roomState.value = null
    }
  } catch (error) {
    ElMessage.error('加载房间列表失败')
  }
}

// 房间切换
async function handleRoomChange(roomId) {
  if (roomId) {
    await fetchRoomState(roomId)
  }
}

// 获取房间状态
async function fetchRoomState(roomId) {
  loading.value = true
  try {
    const state = await acStore.fetchRoomState(roomId)
    roomState.value = state
    
    // 同步控制面板
    if (state.target_temp) targetTemp.value = state.target_temp
    if (state.fan_speed) fanSpeed.value = state.fan_speed
    if (state.ac_mode) acMode.value = state.ac_mode
  } catch (error) {
    ElMessage.error('获取房间状态失败')
  } finally {
    loading.value = false
  }
}

// 刷新状态
async function refreshState() {
  if (selectedRoomId.value) {
    await fetchRoomState(selectedRoomId.value)
  }
}

// 开关空调
async function togglePower() {
  if (!selectedRoomId.value) return
  
  powerLoading.value = true
  try {
    if (roomState.value?.ac_on) {
      await powerOff(selectedRoomId.value)
      ElMessage.success('空调已关闭')
    } else {
      await powerOn(selectedRoomId.value)
      ElMessage.success('空调已开启')
    }
    await refreshState()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    powerLoading.value = false
  }
}

// 改变温度
async function handleTempChange() {
  if (!selectedRoomId.value) return
  try {
    const resp = await changeTemp(selectedRoomId.value, targetTemp.value)
    ElMessage.success(resp?.message || '温度已更新')
    await refreshState()
  } catch (error) {
    ElMessage.error('设置温度失败')
  }
}

// 改变风速
async function handleSpeedChange() {
  if (!selectedRoomId.value) return
  try {
    await changeSpeed(selectedRoomId.value, fanSpeed.value)
    ElMessage.success('风速已更新')
    await refreshState()
  } catch (error) {
    ElMessage.error('设置风速失败')
  }
}

// 改变模式
async function handleModeChange() {
  if (!selectedRoomId.value) return
  try {
    await changeMode(selectedRoomId.value, acMode.value)
    ElMessage.success('模式已切换')
    await refreshState()
  } catch (error) {
    ElMessage.error('切换模式失败')
  }
}

// 获取最小温度
function getMinTemp() {
  return acMode.value === 'HEATING' ? 25 : 18
}

// 获取最大温度
function getMaxTemp() {
  return acMode.value === 'HEATING' ? 30 : 25
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

// 自动刷新
let refreshTimer = null
let roomListTimer = null

watch(selectedRoomId, (newVal) => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
  if (newVal) {
    refreshTimer = setInterval(() => {
      refreshState()
    }, 3000) // 每3秒刷新一次房间状态
  }
})

onMounted(() => {
  loadRooms()
  // 定期刷新房间列表，以便及时反映入住/退房状态变化
  roomListTimer = setInterval(() => {
    loadRooms()
  }, 5000) // 每5秒刷新一次房间列表
})

// 组件卸载时清理定时器
onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  if (roomListTimer) {
    clearInterval(roomListTimer)
  }
})
</script>

<style scoped>
.customer-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.header-content h1 {
  margin: 0;
  color: #303133;
  white-space: nowrap;
}

.status-card,
.control-card {
  margin-bottom: 20px;
}

.status-content {
  padding: 10px 0;
}

.control-buttons {
  text-align: center;
  margin: 20px 0;
}

.temp-control,
.speed-control,
.mode-control {
  margin: 20px 0;
}

.temp-control h3,
.speed-control h3,
.mode-control h3 {
  margin-bottom: 15px;
  color: #606266;
}
</style>

