# 🔌 前端 API 使用指南

本文档详细说明前端如何对接后端 API，包括接口列表、调用方式、请求示例和测试验证。

---

## 📋 目录

1. [快速开始](#快速开始)
2. [API 模式配置](#api-模式配置)
3. [接口分类](#接口分类)
4. [接口详情](#接口详情)
5. [调用示例](#调用示例)
6. [测试验证](#测试验证)
7. [故障排查](#故障排查)

---

## 🚀 快速开始

### 前提条件

1. **后端服务已启动**：`http://localhost:8080`
2. **前端服务已启动**：`http://localhost:5173`
3. **API 模式已配置**：`config/index.ts` 中 `API_MODE = 'api'`

### 验证连接

```bash
# 测试后端连接
curl http://localhost:8080/api/room/states

# 应返回 JSON 格式的房间状态列表
```

---

## ⚙️ API 模式配置

### 配置文件：`src/config/index.ts`

```typescript
// API 模式选择
export const API_MODE: 'mock' | 'api' = 'api';  // ✅ 使用真实 API

// API 基础路径
export const API_BASE_URL = '/api';
```

**模式说明**：
- `'api'` - 调用真实后端 API（生产模式）
- `'mock'` - 使用模拟数据（开发测试）

### Vite 代理配置：`vite.config.ts`

```typescript
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',  // 后端地址
        changeOrigin: true,
      },
    },
  },
})
```

---

## 📚 接口分类

### 接口模块总览

| 模块 | 路径前缀 | 说明 | 接口数量 |
|------|---------|------|----------|
| 房间控制 | `/room` | 开关机、调温调风、状态查询 | 5个 |
| 前台管理 | `/frontdesk` | 入住、退房、账单管理 | 7个 |
| 管理员 | `/admin` | 系统监控、批量操作 | 7个 |
| 经理统计 | `/manager` | 数据统计、报表生成 | 3个 |

---

## 📖 接口详情

### 1️⃣ 房间控制接口

#### 开机

**接口**：`POST /room/{roomId}/turnon`

**前端调用**：
```typescript
await api.room.turnOn(roomId);
```

**响应示例**：
```json
{
  "code": 200,
  "message": "开机成功",
  "data": {
    "roomId": "101",
    "isOn": true,
    "currentTemp": 30,
    "targetTemp": 25,
    "fanSpeed": "MEDIUM",
    "mode": "COOLING",
    "status": "STANDBY"
  }
}
```

#### 关机

**接口**：`POST /room/{roomId}/turnoff`

**前端调用**：
```typescript
await api.room.turnOff(roomId);
```

#### 温控请求（调温/调风/切换模式）

**接口**：`POST /room/{roomId}/request`

**前端调用**：
```typescript
await api.room.sendRequest(roomId, {
  targetTemp: 22,
  fanSpeed: 'HIGH',
  mode: 'COOLING'  // 可选，切换模式时提供
});
```

**请求参数**：
```typescript
interface ServiceRequestDTO {
  targetTemp: number;     // 目标温度 (18-30)
  fanSpeed: FanSpeed;     // 风速 (LOW/MEDIUM/HIGH)
  mode?: ACMode;          // 可选：模式 (COOLING/HEATING)
}
```

**响应示例**：
```json
{
  "code": 200,
  "message": "房间101温控请求处理成功",
  "data": {
    "success": true,
    "message": "已获得服务",
    "details": {
      "roomId": "101",
      "currentTemp": 28.5,
      "targetTemp": 22,
      "fanSpeed": "HIGH",
      "mode": "COOLING",
      "currentStatus": "SERVING",
      "serviceGranted": true,
      "currentCost": 1.93,
      "serviceDuration": 121
    }
  }
}
```

#### 获取房间状态

**接口**：`GET /room/{roomId}/state`

**前端调用**：
```typescript
const state = await api.room.getRoomState(roomId);
```

#### 获取所有房间状态

**接口**：`GET /room/states`

**前端调用**：
```typescript
const rooms = await api.room.getAllRoomStates();
```

---

### 2️⃣ 前台管理接口

#### 办理入住

**接口**：`POST /frontdesk/checkin`

**前端调用**：
```typescript
await api.frontDesk.checkIn({
  roomId: '101',
  guestName: '张三',
  guestPhone: '13800138000',
  idCard: '110101199001011234',
  idType: 'ID_CARD',
  stayDays: 3,
  roomType: 'STANDARD',
  pricePerNight: 200,
  deposit: 500,
  mode: 'COOLING'
});
```

**请求参数**：
```typescript
interface CheckInDTO {
  roomId: string;         // 房间号
  guestName: string;      // 客户姓名
  guestPhone: string;     // 手机号
  idCard: string;         // 证件号码
  idType: string;         // 证件类型
  stayDays: number;       // 入住天数
  roomType: string;       // 房型
  pricePerNight: number;  // 房费/晚
  deposit: number;        // 押金
  mode: ACMode;           // 空调模式
}
```

#### 办理退房

**接口**：`POST /frontdesk/checkout/{roomId}`

**前端调用**：
```typescript
const bill = await api.frontDesk.checkOut(roomId);
```

**响应示例**：
```json
{
  "code": 200,
  "message": "退房办理成功",
  "data": {
    "roomId": "101",
    "guestName": "张三",
    "checkInTime": "2024-11-20T10:00:00",
    "checkOutTime": "2024-11-21T12:00:00",
    "totalCost": 650.50,
    "roomFee": 600.00,
    "acCost": 50.50,
    "detailRecords": [...]
  }
}
```

#### 获取账单

**接口**：`GET /frontdesk/bill/{roomId}`

**前端调用**：
```typescript
const bill = await api.frontDesk.getBill(roomId);
```

#### 获取所有账单

**接口**：`GET /frontdesk/bills`

**前端调用**：
```typescript
const bills = await api.frontDesk.getAllBills();
```

#### 获取已入住房间列表

**接口**：`GET /frontdesk/occupied-rooms`

**前端调用**：
```typescript
const occupiedRooms = await api.frontDesk.getOccupiedRooms();
```

#### 获取可入住房间列表

**接口**：`GET /frontdesk/available-rooms`

**前端调用**：
```typescript
const availableRooms = await api.frontDesk.getAvailableRooms({
  roomType: 'STANDARD',  // 可选：房型筛选
  minPrice: 100,         // 可选：最低价格
  maxPrice: 500,         // 可选：最高价格
  floor: 2              // 可选：楼层
});
```

#### 获取入住记录

**接口**：`GET /frontdesk/checkin-records`

**前端调用**：
```typescript
const records = await api.frontDesk.getCheckInRecords();
```

---

### 3️⃣ 管理员接口

#### 获取服务队列

**接口**：`GET /admin/service-queue`

**前端调用**：
```typescript
const serviceQueue = await api.admin.getServiceQueue();
```

**响应示例**：
```json
{
  "code": 200,
  "message": "获取服务队列成功，当前有3个房间在服务中",
  "data": [
    {
      "id": "service_1700000000000_abc123",
      "roomId": "101",
      "fanSpeed": "HIGH",
      "startTime": "2024-11-21T10:00:00",
      "duration": 120
    }
  ]
}
```

#### 获取等待队列

**接口**：`GET /admin/waiting-queue`

**前端调用**：
```typescript
const waitingQueue = await api.admin.getWaitingQueue();
```

#### 一键开机

**接口**：`POST /admin/turnon-all`

**前端调用**：
```typescript
await api.admin.turnOnAll();
```

#### 一键关机

**接口**：`POST /admin/turnoff-all`

**前端调用**：
```typescript
await api.admin.turnOffAll();
```

#### 清空等待队列

**接口**：`POST /admin/clear-waiting-queue`

**前端调用**：
```typescript
await api.admin.clearWaitingQueue();
```

#### 管理员强制开机

**接口**：`POST /admin/room/{roomId}/force-on`

**前端调用**：
```typescript
await api.admin.forceOn(roomId);
```

#### 管理员强制关机

**接口**：`POST /admin/room/{roomId}/force-off`

**前端调用**：
```typescript
await api.admin.forceOff(roomId);
```

---

### 4️⃣ 经理统计接口

#### 生成统计报表

**接口**：`POST /manager/statistics`

**前端调用**：
```typescript
const report = await api.manager.getStatistics({
  startTime: 1700000000000,  // 时间戳
  endTime: 1700086400000
});
```

**响应示例**：
```json
{
  "code": 200,
  "message": "报表生成成功",
  "data": {
    "totalRevenue": 5280.50,
    "totalRooms": 20,
    "occupancyRate": 75.5,
    "totalDuration": 12480,
    "fanSpeedDistribution": {
      "LOW": 30,
      "MEDIUM": 45,
      "HIGH": 25
    },
    "roomDetails": [...]
  }
}
```

#### 生成统计报表（灵活时间格式）

**接口**：`POST /manager/statistics-flexible`

**前端调用**：
```typescript
// 方式1：使用日期字符串
const report = await api.manager.getStatisticsFlexible({
  startDate: '2024-11-01',
  endDate: '2024-11-21'
});

// 方式2：使用快捷选项
const report = await api.manager.getStatisticsFlexible({
  quickOption: 'thisMonth'  // today/yesterday/thisWeek/thisMonth/lastMonth
});
```

#### 获取历史账单

**接口**：`GET /manager/bills`

**前端调用**：
```typescript
const bills = await api.manager.getAllBills();
```

---

## 💻 调用示例

### 在组件中使用 API

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { api } from '@/api/hvac';
import { showSuccess, showError } from '@/composables/useDialog';

const roomId = ref('101');
const roomState = ref(null);

// 开机
const handleTurnOn = async () => {
  try {
    const result = await api.room.turnOn(roomId.value);
    showSuccess('开机成功');
    roomState.value = result;
  } catch (error) {
    showError('开机失败：' + error.message);
  }
};

// 调温
const handleAdjustTemp = async (targetTemp: number) => {
  try {
    await api.room.sendRequest(roomId.value, {
      targetTemp,
      fanSpeed: 'MEDIUM'
    });
    showSuccess('温度调节成功');
  } catch (error) {
    showError('调节失败：' + error.message);
  }
};

// 获取房间状态
const fetchRoomState = async () => {
  try {
    roomState.value = await api.room.getRoomState(roomId.value);
  } catch (error) {
    console.error('获取状态失败', error);
  }
};

// 页面加载时获取状态
onMounted(() => {
  fetchRoomState();
  
  // 定时刷新（每2秒）
  setInterval(fetchRoomState, 2000);
});
</script>
```

### 使用 ApiAdapter（自动模式切换）

```typescript
import { ApiAdapter } from '@/services/ApiAdapter';

const apiAdapter = new ApiAdapter();

// ApiAdapter 会根据 config/index.ts 中的 API_MODE 自动选择调用方式
// API_MODE = 'api'  → 调用真实后端 API
// API_MODE = 'mock' → 使用 Mock 数据

// 办理入住
const result = await apiAdapter.checkIn({
  roomId: '101',
  guestName: '张三',
  // ... 其他参数
});
```

---

## ✅ 测试验证

### 1. 房间控制测试

**测试步骤**：

1. 打开浏览器开发者工具（F12）
2. 切换到 Network 面板
3. 以客户身份登录，选择房间
4. 点击"开机"按钮
   - ✅ 观察 Network 面板：应看到 `POST /api/room/101/turnon`
   - ✅ 检查响应：`code: 200, message: "开机成功"`
   - ✅ 界面更新：按钮变为"关机"，显示绿色
5. 调节温度滑块
   - ✅ 观察 Network 面板：应看到 `POST /api/room/101/request`
   - ✅ 检查请求体：包含 `targetTemp` 和 `fanSpeed`
6. 点击"关机"按钮
   - ✅ 观察 Network 面板：应看到 `POST /api/room/101/turnoff`

### 2. 前台服务测试

**测试步骤**：

1. 以前台身份登录
2. 点击"办理入住"
3. 完成四步入住流程
4. 点击"确认入住"
   - ✅ 观察 Network 面板：`POST /api/frontdesk/checkin`
   - ✅ 检查请求体：包含完整的 CheckInDTO 数据
   - ✅ 检查响应：入住成功，返回入住记录ID
5. 点击"退房结账"
6. 选择房间，点击"退房"
   - ✅ 观察 Network 面板：`POST /api/frontdesk/checkout/101`
   - ✅ 检查响应：返回完整的账单信息

### 3. 管理员功能测试

**测试步骤**：

1. 以管理员身份登录
2. 观察服务队列和等待队列
   - ✅ Network 面板：定时请求 `GET /api/admin/service-queue` 和 `GET /api/admin/waiting-queue`
3. 点击"一键关机"
   - ✅ 弹出确认对话框
   - ✅ 确认后，Network 面板：`POST /api/admin/turnoff-all`
4. 点击"刷新"按钮
   - ✅ 手动触发数据刷新

### 4. 经理统计测试

**测试步骤**：

1. 以经理身份登录
2. 选择时间范围（或快捷选项）
3. 点击"生成报表"
   - ✅ Network 面板：`POST /api/manager/statistics` 或 `POST /api/manager/statistics-flexible`
   - ✅ 检查请求体：包含时间参数
   - ✅ 检查响应：返回统计报表数据
   - ✅ 界面显示：图表和数据表正确渲染

---

## 🐛 故障排查

### 问题 1：所有请求返回 404

**原因**：后端服务未启动或路径错误

**解决方案**：
```bash
# 1. 检查后端是否运行
curl http://localhost:8080/api/room/states

# 2. 如果失败，启动后端
cd back-end
mvn spring-boot:run

# 3. 确认后端启动成功
# 应该看到：中央温控系统启动成功！
```

### 问题 2：请求返回 403 (CORS 错误)

**原因**：跨域配置问题

**检查**：
1. 后端 `WebConfig.java` 是否配置了 CORS
2. Vite 代理配置是否正确

**解决方案**：
```typescript
// vite.config.ts - 确保代理配置正确
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true,  // ✅ 必须为 true
    },
  },
}
```

### 问题 3：请求超时

**原因**：网络慢或后端响应慢

**解决方案**：
```typescript
// src/api/request.ts - 增加超时时间
const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,  // 改为 30 秒
});
```

### 问题 4：数据格式错误

**原因**：前后端数据格式不一致

**检查**：
1. 前端发送的字段名是否与后端 DTO 一致
2. 枚举值大小写是否匹配（如 `COOLING` vs `cooling`）

**调试方法**：
```typescript
// 在发送请求前打印数据
console.log('发送数据:', data);

// 在接收响应后打印数据
console.log('响应数据:', response);
```

### 问题 5：接口调用成功但界面不更新

**原因**：响应式数据未正确更新

**解决方案**：
```typescript
// ✅ 正确：使用 ref 包装
const roomState = ref<RoomState | null>(null);
roomState.value = await api.room.getRoomState(roomId);

// ❌ 错误：直接赋值
let roomState = null;
roomState = await api.room.getRoomState(roomId);  // Vue 无法追踪
```

---

## 📊 接口调用统计

| 组件 | 主要调用的接口 | 调用频率 |
|------|---------------|----------|
| RoomClient.vue | `turnon`, `turnoff`, `sendRequest`, `getRoomState` | 高频（2秒/次） |
| FrontDeskBilling.vue | `checkIn`, `checkOut`, `getBill`, `getAvailableRooms` | 按需调用 |
| AdminMonitor.vue | `getServiceQueue`, `getWaitingQueue`, `getAllRoomStates` | 中频（3秒/次） |
| ManagerStatistics.vue | `getStatistics`, `getAllBills` | 低频（按需） |

---

## 🔗 相关文档

- [快速启动指南](QUICKSTART.md) - 项目安装和启动
- [项目结构文档](PROJECT_STRUCTURE.md) - 代码组织和架构
- [入住流程文档](CHECKIN_PROCESS.md) - 业务流程详解
- [后端 API 文档](../../back-end/docs/APIFOX_GUIDE.md) - 完整的后端接口文档

---

**Happy Coding!** 🎉
