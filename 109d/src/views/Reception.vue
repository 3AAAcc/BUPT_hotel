<template>
  <div class="reception-page">
    <el-container>
      <el-header>
        <h1>前台管理系统</h1>
        <el-menu
          mode="horizontal"
          :default-active="activeTab"
          @select="handleTabSelect"
        >
          <el-menu-item index="rooms">房间管理</el-menu-item>
          <el-menu-item index="checkin">办理入住</el-menu-item>
          <el-menu-item index="checkout">办理退房</el-menu-item>
        </el-menu>
      </el-header>

      <el-main>
        <!-- 房间管理 -->
        <div v-if="activeTab === 'rooms'" class="tab-content">
          <el-card>
            <template #header>
              <span>房间列表</span>
              <el-button type="primary" size="small" @click="loadRooms" :loading="loading" style="float: right">
                刷新
              </el-button>
            </template>
            <el-table :data="rooms" v-loading="loading">
              <el-table-column prop="id" label="房间号" width="100" />
              <el-table-column prop="status" label="状态" width="120">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)">
                    {{ getStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="currentTemp" label="当前温度" width="120">
                <template #default="{ row }">
                  {{ Number(row.currentTemp ?? 0).toFixed(2) }}°C
                </template>
              </el-table-column>
              <el-table-column prop="acOn" label="空调状态" width="120">
                <template #default="{ row }">
                  <el-tag :type="row.acOn ? 'success' : 'info'">
                    {{ row.acOn ? '运行中' : '已关闭' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="customer_name" label="客户姓名" />
            </el-table>
          </el-card>
        </div>

        <!-- 办理入住 -->
        <div v-if="activeTab === 'checkin'" class="tab-content">
          <el-card>
            <template #header>
              <span>办理入住</span>
            </template>
            <el-form :model="checkInForm" label-width="120px" style="max-width: 600px">
              <el-form-item label="选择房间">
                <el-select v-model="checkInForm.roomId" placeholder="请选择房间" filterable>
                  <el-option
                    v-for="room in availableRooms"
                    :key="room.id"
                    :label="`房间 ${room.id}`"
                    :value="room.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="客户姓名" required>
                <el-input v-model="checkInForm.name" placeholder="请输入客户姓名" />
              </el-form-item>
              <el-form-item label="身份证号" required>
                <el-input v-model="checkInForm.idCard" placeholder="请输入身份证号" />
              </el-form-item>
              <el-form-item label="联系电话" required>
                <el-input v-model="checkInForm.phoneNumber" placeholder="请输入联系电话" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleCheckIn" :loading="checkInLoading">
                  办理入住
                </el-button>
                <el-button @click="resetCheckInForm">重置</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>

        <!-- 办理退房 -->
        <div v-if="activeTab === 'checkout'" class="tab-content">
          <el-card>
            <template #header>
              <span>办理退房</span>
            </template>
            <el-form :model="checkOutForm" label-width="120px" style="max-width: 600px">
              <el-form-item label="选择房间">
                <el-select v-model="checkOutForm.roomId" placeholder="请选择房间" filterable>
                  <el-option
                    v-for="room in occupiedRooms"
                    :key="room.id"
                    :label="`房间 ${room.id} - ${room.customer_name || '未知'}`"
                    :value="room.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleCheckOut" :loading="checkOutLoading">
                  办理退房
                </el-button>
              </el-form-item>
            </el-form>

            <!-- 退房账单显示 -->
            <el-card v-if="checkOutBill" style="margin-top: 20px">
              <template #header>
                <span>退房账单</span>
              </template>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="房间号">{{ checkOutBill.bill?.roomId }}</el-descriptions-item>
                <el-descriptions-item label="入住时间">{{ checkOutBill.bill?.checkinTime }}</el-descriptions-item>
                <el-descriptions-item label="退房时间">{{ checkOutBill.bill?.checkoutTime }}</el-descriptions-item>
                <el-descriptions-item label="住宿天数">{{ checkOutBill.bill?.duration }} 天</el-descriptions-item>
                <el-descriptions-item label="房费">¥{{ checkOutBill.bill?.roomFee?.toFixed(2) }}</el-descriptions-item>
                <el-descriptions-item label="空调费">¥{{ checkOutBill.bill?.acFee?.toFixed(2) }}</el-descriptions-item>
                <el-descriptions-item label="总金额" :span="2">
                  <span style="font-size: 18px; color: #f56c6c; font-weight: bold">
                    ¥{{ (checkOutBill.bill?.roomFee + checkOutBill.bill?.acFee)?.toFixed(2) }}
                  </span>
                </el-descriptions-item>
              </el-descriptions>
              <el-divider />
              <h4>空调用能详单</h4>
              <el-table :data="checkOutBill.detailBill || []" border size="small">
                <el-table-column prop="roomId" label="房间号" width="90" />
                <el-table-column prop="startTime" label="开始时间" width="160" />
                <el-table-column prop="endTime" label="结束时间" width="160" />
                <el-table-column prop="fanSpeed" label="风速" width="80">
                  <template #default="{ row }">
                    {{ getFanSpeedText(row.fanSpeed) }}
                  </template>
                </el-table-column>
                <el-table-column prop="mode" label="模式" width="80">
                  <template #default="{ row }">
                    {{ getModeText(row.mode) }}
                  </template>
                </el-table-column>
                <el-table-column prop="duration" label="时长(分钟)" width="110" />
                <el-table-column prop="startTemp" label="起始温度(°C)" width="120">
                  <template #default="{ row }">
                    {{ row.startTemp?.toFixed(2) ?? '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="endTemp" label="结束温度(°C)" width="120">
                  <template #default="{ row }">
                    {{ row.endTemp?.toFixed(2) ?? '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="tempDelta" label="温差(°C)" width="110">
                  <template #default="{ row }">
                    {{ row.tempDelta !== null && row.tempDelta !== undefined ? row.tempDelta.toFixed(2) : '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="energy" label="耗电量(度)" width="110">
                  <template #default="{ row }">
                    {{ row.energy?.toFixed(2) ?? '0.00' }}
                  </template>
                </el-table-column>
                <el-table-column prop="fee" label="费用(元)" width="110">
                  <template #default="{ row }">
                    ¥{{ row.fee?.toFixed(2) }}
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-card>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAllRooms, getAvailableRooms, checkIn, checkOut } from '@/api/hotel'

const activeTab = ref('rooms')
const rooms = ref([])
const loading = ref(false)

const checkInForm = ref({
  roomId: null,
  name: '',
  idCard: '',
  phoneNumber: ''
})
const checkInLoading = ref(false)

const checkOutForm = ref({
  roomId: null
})
const checkOutLoading = ref(false)
const checkOutBill = ref(null)

// 可用房间
const availableRooms = computed(() => {
  return rooms.value.filter(room => room.status === 'AVAILABLE')
})

// 已入住房间
const occupiedRooms = computed(() => {
  return rooms.value.filter(room => room.status === 'OCCUPIED')
})

// 加载房间列表
async function loadRooms() {
  loading.value = true
  try {
    rooms.value = await getAllRooms()
  } catch (error) {
    ElMessage.error('加载房间列表失败')
  } finally {
    loading.value = false
  }
}

// 切换标签
function handleTabSelect(key) {
  activeTab.value = key
  if (key === 'rooms') {
    loadRooms()
  }
}

// 办理入住
async function handleCheckIn() {
  if (!checkInForm.value.roomId) {
    ElMessage.warning('请选择房间')
    return
  }
  if (!checkInForm.value.name || !checkInForm.value.idCard || !checkInForm.value.phoneNumber) {
    ElMessage.warning('请填写完整信息')
    return
  }

  checkInLoading.value = true
  try {
    await checkIn(checkInForm.value)
    ElMessage.success('入住成功')
    resetCheckInForm()
    await loadRooms()
  } catch (error) {
    ElMessage.error('办理入住失败')
  } finally {
    checkInLoading.value = false
  }
}

// 重置入住表单
function resetCheckInForm() {
  checkInForm.value = {
    roomId: null,
    name: '',
    idCard: '',
    phoneNumber: ''
  }
}

// 办理退房
async function handleCheckOut() {
  if (!checkOutForm.value.roomId) {
    ElMessage.warning('请选择房间')
    return
  }

  try {
    await ElMessageBox.confirm('确认办理退房？', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })

    checkOutLoading.value = true
    try {
      const bill = await checkOut(checkOutForm.value.roomId)
      checkOutBill.value = bill
      ElMessage.success('退房成功')
      await loadRooms()
    } catch (error) {
      ElMessage.error('办理退房失败')
    } finally {
      checkOutLoading.value = false
    }
  } catch {
    // 用户取消
  }
}

// 获取状态文本（已入住/空闲）
function getStatusText(status) {
  if (status === 'OCCUPIED') return '已入住'
  return '空闲'
}

// 获取状态类型
function getStatusType(status) {
  if (status === 'OCCUPIED') return 'success'
  return 'info'
}

function getFanSpeedText(speed) {
  const map = { 'LOW': '低风', 'MEDIUM': '中风', 'HIGH': '高风' }
  return map[speed] || speed || '-'
}

function getModeText(mode) {
  return mode === 'HEATING' ? '制热' : '制冷'
}

onMounted(() => {
  loadRooms()
})
</script>

<style scoped>
.reception-page {
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
</style>

