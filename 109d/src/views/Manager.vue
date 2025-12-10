<template>
  <div class="manager-page">
    <el-container>
      <el-header>
        <h1>经理报表界面</h1>
        <el-menu
          mode="horizontal"
          :default-active="activeTab"
          @select="handleTabSelect"
        >
          <el-menu-item index="monitor">实时监控</el-menu-item>
          <el-menu-item index="room-report">房间报表</el-menu-item>
          <el-menu-item index="daily-report">日报表</el-menu-item>
          <el-menu-item index="weekly-report">周报表</el-menu-item>
        </el-menu>
      </el-header>

      <el-main>
        <!-- 实时监控 -->
        <div v-if="activeTab === 'monitor'" class="tab-content">
          <el-card>
            <template #header>
              <span>调度器监控</span>
              <el-button type="primary" size="small" @click="loadMonitorStatus" :loading="monitorLoading" style="float: right">
                刷新
              </el-button>
            </template>
            <div v-if="monitorStatus">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="总容量">{{ monitorStatus.capacity }} 台</el-descriptions-item>
                <el-descriptions-item label="时间片">{{ monitorStatus.timeSlice }} 秒</el-descriptions-item>
                <el-descriptions-item label="服务队列" :span="2">
                  {{ monitorStatus.servingQueue?.length || 0 }} 个房间
                </el-descriptions-item>
                <el-descriptions-item label="等待队列" :span="2">
                  {{ monitorStatus.waitingQueue?.length || 0 }} 个房间
                </el-descriptions-item>
              </el-descriptions>

              <el-divider />

              <h3>服务队列</h3>
              <el-table :data="monitorStatus.servingQueue" border style="margin-bottom: 20px">
                <el-table-column prop="roomId" label="房间号" width="100" />
                <el-table-column prop="serviceObjectId" label="服务对象" width="110">
                  <template #default="{ row }">
                    {{ row.serviceObjectId || '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="fanSpeed" label="风速" width="100">
                  <template #default="{ row }">
                    {{ getFanSpeedText(row.fanSpeed) }}
                  </template>
                </el-table-column>
                <el-table-column prop="mode" label="模式" width="100">
                  <template #default="{ row }">
                    {{ row.mode === 'COOLING' ? '制冷' : '制热' }}
                  </template>
                </el-table-column>
                <el-table-column prop="targetTemp" label="目标温度" width="120">
                  <template #default="{ row }">
                    {{ row.targetTemp }}°C
                  </template>
                </el-table-column>
                <el-table-column prop="servingSeconds" label="服务时长" width="120">
                  <template #default="{ row }">
                    {{ Math.floor(row.servingSeconds / 60) }}分{{ Math.floor(row.servingSeconds % 60) }}秒
                  </template>
                </el-table-column>
                <el-table-column prop="totalSeconds" label="总时长" width="120">
                  <template #default="{ row }">
                    {{ Math.floor(row.totalSeconds / 60) }}分{{ Math.floor(row.totalSeconds % 60) }}秒
                  </template>
                </el-table-column>
              </el-table>

              <h3>等待队列</h3>
              <el-table :data="monitorStatus.waitingQueue" border>
                <el-table-column prop="roomId" label="房间号" width="100" />
                <el-table-column prop="fanSpeed" label="风速" width="100">
                  <template #default="{ row }">
                    {{ getFanSpeedText(row.fanSpeed) }}
                  </template>
                </el-table-column>
                <el-table-column prop="mode" label="模式" width="100">
                  <template #default="{ row }">
                    {{ row.mode === 'COOLING' ? '制冷' : '制热' }}
                  </template>
                </el-table-column>
                <el-table-column prop="targetTemp" label="目标温度" width="120">
                  <template #default="{ row }">
                    {{ row.targetTemp }}°C
                  </template>
                </el-table-column>
                <el-table-column prop="waitingSeconds" label="等待时长" width="120">
                  <template #default="{ row }">
                    {{ Math.floor(row.waitingSeconds / 60) }}分{{ Math.floor(row.waitingSeconds % 60) }}秒
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </div>

        <!-- 房间报表 -->
        <div v-if="activeTab === 'room-report'" class="tab-content">
          <el-card>
            <template #header>
              <span>房间报表</span>
            </template>
            <el-form :inline="true" style="margin-bottom: 20px">
              <el-form-item label="房间号">
                <el-input-number v-model="roomReportForm.roomId" :min="1" :max="10" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="loadRoomReport" :loading="roomReportLoading">
                  查询
                </el-button>
              </el-form-item>
            </el-form>
            <el-table :data="roomReportData" border v-loading="roomReportLoading">
              <el-table-column prop="roomId" label="房间号" width="100" />
              <el-table-column prop="startTime" label="开始时间" width="180" />
              <el-table-column prop="endTime" label="结束时间" width="180" />
              <el-table-column prop="duration" label="时长(分钟)" width="120" />
              <el-table-column prop="fanSpeed" label="风速" width="100" />
              <el-table-column prop="rate" label="费率" width="100" />
              <el-table-column prop="fee" label="费用" width="120">
                <template #default="{ row }">
                  ¥{{ row.fee?.toFixed(2) }}
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>

        <!-- 日报表 -->
        <div v-if="activeTab === 'daily-report'" class="tab-content">
          <el-card>
            <template #header>
              <span>日报表</span>
            </template>
            <el-form :inline="true" style="margin-bottom: 20px">
              <el-form-item label="日期">
                <el-date-picker
                  v-model="dailyReportForm.date"
                  type="date"
                  placeholder="选择日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="loadDailyReport" :loading="dailyReportLoading">
                  查询
                </el-button>
              </el-form-item>
            </el-form>
            <el-table :data="dailyReportData" border v-loading="dailyReportLoading">
              <el-table-column prop="roomId" label="房间号" width="100" />
              <el-table-column prop="usageCount" label="使用次数" width="120" />
              <el-table-column prop="totalDuration" label="总时长(分钟)" width="150" />
              <el-table-column prop="totalFee" label="总费用" width="120">
                <template #default="{ row }">
                  ¥{{ row.totalFee?.toFixed(2) }}
                </template>
              </el-table-column>
              <el-table-column prop="totalEnergy" label="耗电量(度)" width="140">
                <template #default="{ row }">
                  {{ row.totalEnergy?.toFixed(2) || '0.00' }}
                </template>
              </el-table-column>
              <el-table-column prop="avgTempDiff" label="平均温差(°C)" width="160">
                <template #default="{ row }">
                  {{ row.avgTempDiff?.toFixed(2) || '0.00' }}
                </template>
              </el-table-column>
              <el-table-column prop="dispatchCount" label="调度次数" width="120" />
              <el-table-column prop="recordCount" label="记录数" width="120" />
            </el-table>
          </el-card>
        </div>

        <!-- 周报表 -->
        <div v-if="activeTab === 'weekly-report'" class="tab-content">
          <el-card>
            <template #header>
              <span>周报表</span>
            </template>
            <el-form :inline="true" style="margin-bottom: 20px">
              <el-form-item label="开始日期">
                <el-date-picker
                  v-model="weeklyReportForm.startDate"
                  type="date"
                  placeholder="选择开始日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="loadWeeklyReport" :loading="weeklyReportLoading">
                  查询
                </el-button>
              </el-form-item>
            </el-form>
            <el-table :data="weeklyReportData" border v-loading="weeklyReportLoading">
              <el-table-column prop="roomId" label="房间号" width="100" />
              <el-table-column prop="usageCount" label="使用次数" width="120" />
              <el-table-column prop="totalDuration" label="总时长(分钟)" width="150" />
              <el-table-column prop="totalFee" label="总费用" width="120">
                <template #default="{ row }">
                  ¥{{ row.totalFee?.toFixed(2) }}
                </template>
              </el-table-column>
              <el-table-column prop="totalEnergy" label="耗电量(度)" width="140">
                <template #default="{ row }">
                  {{ row.totalEnergy?.toFixed(2) || '0.00' }}
                </template>
              </el-table-column>
              <el-table-column prop="avgTempDiff" label="平均温差(°C)" width="160">
                <template #default="{ row }">
                  {{ row.avgTempDiff?.toFixed(2) || '0.00' }}
                </template>
              </el-table-column>
              <el-table-column prop="dispatchCount" label="调度次数" width="120" />
              <el-table-column prop="recordCount" label="记录数" width="120" />
            </el-table>
          </el-card>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getMonitorStatus } from '@/api/monitor'
import { getRoomReport, getDailyReport, getWeeklyReport } from '@/api/report'

const activeTab = ref('monitor')

const monitorStatus = ref(null)
const monitorLoading = ref(false)

const roomReportForm = ref({ roomId: 1 })
const roomReportData = ref([])
const roomReportLoading = ref(false)

const dailyReportForm = ref({ date: new Date().toISOString().split('T')[0] })
const dailyReportData = ref([])
const dailyReportLoading = ref(false)

const weeklyReportForm = ref({ startDate: new Date().toISOString().split('T')[0] })
const weeklyReportData = ref([])
const weeklyReportLoading = ref(false)

// 切换标签
function handleTabSelect(key) {
  activeTab.value = key
  if (key === 'monitor') {
    loadMonitorStatus()
  }
}

// 加载监控状态
async function loadMonitorStatus() {
  monitorLoading.value = true
  try {
    monitorStatus.value = await getMonitorStatus()
  } catch (error) {
    ElMessage.error('加载监控状态失败')
  } finally {
    monitorLoading.value = false
  }
}

// 加载房间报表
async function loadRoomReport() {
  if (!roomReportForm.value.roomId) {
    ElMessage.warning('请选择房间号')
    return
  }
  roomReportLoading.value = true
  try {
    roomReportData.value = await getRoomReport(roomReportForm.value.roomId)
  } catch (error) {
    ElMessage.error('加载房间报表失败')
  } finally {
    roomReportLoading.value = false
  }
}

// 加载日报表
async function loadDailyReport() {
  if (!dailyReportForm.value.date) {
    ElMessage.warning('请选择日期')
    return
  }
  dailyReportLoading.value = true
  try {
    dailyReportData.value = await getDailyReport(dailyReportForm.value.date)
  } catch (error) {
    ElMessage.error('加载日报表失败')
  } finally {
    dailyReportLoading.value = false
  }
}

// 加载周报表
async function loadWeeklyReport() {
  if (!weeklyReportForm.value.startDate) {
    ElMessage.warning('请选择开始日期')
    return
  }
  weeklyReportLoading.value = true
  try {
    weeklyReportData.value = await getWeeklyReport(weeklyReportForm.value.startDate)
  } catch (error) {
    ElMessage.error('加载周报表失败')
  } finally {
    weeklyReportLoading.value = false
  }
}

// 获取风速文本
function getFanSpeedText(speed) {
  const map = { 'LOW': '低风', 'MEDIUM': '中风', 'HIGH': '高风' }
  return map[speed] || speed
}

onMounted(() => {
  loadMonitorStatus()
  // 自动刷新监控
  setInterval(() => {
    if (activeTab.value === 'monitor') {
      loadMonitorStatus()
    }
  }, 5000)
})
</script>

<style scoped>
.manager-page {
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
  margin: 0 0 20px 0;
  color: #303133;
  white-space: nowrap;
}

.tab-content {
  padding: 20px;
}

h3 {
  margin: 20px 0 10px 0;
  color: #606266;
}
</style>

