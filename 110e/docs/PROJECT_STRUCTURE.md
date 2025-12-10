# 📂 前端项目结构文档

本文档详细说明前端项目的目录结构、组件作用及前端架构设计。

---

## 📁 整体结构

```
front-end/
├── docs/                           # 📚 项目文档
│   ├── QUICKSTART.md              # 快速启动指南
│   ├── PROJECT_STRUCTURE.md       # 项目结构文档（本文档）
│   ├── CHECKIN_PROCESS.md         # 入住流程详解
│   └── API_GUIDE.md               # API 使用指南
├── public/                         # 静态资源
├── src/
│   ├── components/                 # 📦 Vue 组件
│   │   ├── admin/                 # 管理员模块
│   │   ├── frontdesk/             # 前台模块
│   │   ├── manager/               # 经理模块
│   │   ├── room/                  # 房间控制模块
│   │   ├── homepage/              # 首页模块
│   │   ├── views/                 # 页面级组件
│   │   └── common/                # 公共组件
│   ├── services/                   # 💼 业务逻辑层
│   │   ├── ACService.ts           # 空调服务
│   │   ├── Scheduler.ts           # 调度服务
│   │   ├── BillingService.ts      # 计费服务
│   │   ├── CentralController.ts   # 中央控制器
│   │   └── ApiAdapter.ts          # API 适配器
│   ├── api/                        # 🔌 API 接口层
│   │   ├── hvac.ts                # 接口定义
│   │   └── request.ts             # HTTP 请求封装
│   ├── composables/                # 🪝 组合式函数
│   │   └── useDialog.ts           # 弹窗系统
│   ├── types/                      # 📝 TypeScript 类型定义
│   │   └── index.ts               # 类型定义
│   ├── constants/                  # 🔢 常量配置
│   │   └── index.ts               # 系统常量
│   ├── config/                     # ⚙️ 配置文件
│   │   └── index.ts               # 应用配置
│   ├── router/                     # 🗺️ 路由配置
│   │   └── index.ts               # 路由定义
│   ├── assets/                     # 🎨 静态资源
│   ├── App.vue                     # 主应用组件
│   ├── main.ts                     # 应用入口
│   └── style.css                   # 全局样式
├── package.json                    # 项目依赖
├── vite.config.ts                  # Vite 配置
├── tsconfig.json                   # TypeScript 配置
└── README.md                       # 项目说明
```

---

## 🏗️ 前端架构设计

### 分层架构

本项目采用**三层架构**模式，职责分明：

| 层次 | 位置 | 职责 | 不允许做什么 |
|------|------|------|--------------|
| **组件层 (Components)** | `components/` | UI 渲染、用户交互、调用 Service | ❌ 不包含复杂业务逻辑<br>❌ 不直接调用 API |
| **服务层 (Services)** | `services/` | 业务逻辑、数据处理、状态管理 | ❌ 不操作 DOM<br>❌ 不包含 UI 逻辑 |
| **接口层 (API)** | `api/` | HTTP 请求、数据传输 | ❌ 不包含业务逻辑<br>❌ 只负责数据通信 |

### 数据流向

```
用户操作 → 组件 (Vue Component)
           ↓
        服务层 (Service)
           ↓
        接口层 (API)
           ↓
        后端服务器
           ↓
        数据库
```

---

## 📦 组件层详解

### 1️⃣ admin/ - 管理员模块

**主组件**: `AdminMonitor.vue` (354行)

**作用**: 管理员监控面板，实时监控系统运行状态

**核心功能**:
- 查看所有房间实时状态
- 监控服务队列和等待队列
- 批量控制房间（一键开关机）
- 强制开关机操作

**子组件**:

| 组件 | 文件 | 作用 | 行数 |
|------|------|------|------|
| 系统概览 | `SystemOverview.vue` | 显示系统运行统计数据（开机数、服务数、等待数） | 122行 |
| 队列列表 | `QueueList.vue` | 显示服务队列和等待队列详情 | 168行 |
| 房间状态网格 | `RoomStatusGrid.vue` | 网格展示所有房间状态 | 243行 |

**使用示例**:
```vue
<template>
  <div class="admin-monitor">
    <SystemOverview :stats="systemStats" />
    <QueueList :serviceQueue="serviceQueue" :waitingQueue="waitingQueue" />
    <RoomStatusGrid :rooms="rooms" @force-action="handleForceAction" />
  </div>
</template>
```

---

### 2️⃣ frontdesk/ - 前台模块

**主组件**: `FrontDeskBilling.vue` (512行)

**作用**: 前台办理入住、退房和账单管理

**核心功能**:
- 办理入住（四步流程）
- 办理退房结账
- 查看账单详情
- 历史账单查询

**子组件**:

| 组件 | 文件 | 作用 | 行数 |
|------|------|------|------|
| 入住表单 | `CheckInForm.vue` | 四步式入住流程（见下文详解） | 250行 |
| 退房表单 | `CheckOutForm.vue` | 办理退房、生成账单 | 186行 |
| 账单详情 | `BillDetail.vue` | 显示详细账单信息 | 95行 |
| 账单历史 | `BillHistory.vue` | 历史账单列表查询 | 142行 |

**入住流程子组件** (`frontdesk/checkin/`):

| 组件 | 文件 | 作用 | 行数 |
|------|------|------|------|
| 步骤指示器 | `StepIndicator.vue` | 显示当前步骤进度 | 110行 |
| 步骤1：选择房间 | `Step1RoomSelection.vue` | 可视化房间选择、筛选 | 270行 |
| 步骤2：客户信息 | `Step2GuestInfo.vue` | 填写客户信息、证件验证 | 230行 |
| 步骤3：空调设置 | `Step3ACSettings.vue` | 初始化空调模式设置 | 250行 |
| 步骤4：确认支付 | `Step4Confirmation.vue` | 信息确认、押金支付 | 340行 |

**账单详情子组件** (`frontdesk/bill/`):

| 组件 | 文件 | 作用 | 行数 |
|------|------|------|------|
| 账单标题 | `BillHeader.vue` | 显示账单编号、时间 | 90行 |
| 客户信息 | `GuestInfoSection.vue` | 显示客户基本信息 | 75行 |
| 入住信息 | `StayInfoSection.vue` | 显示入住时间、房型等 | 95行 |
| 费用明细 | `ChargesBreakdown.vue` | 详细费用拆分（房费+空调费） | 270行 |
| 使用记录 | `ACUsageRecords.vue` | 空调使用详单记录 | 220行 |

---

### 3️⃣ manager/ - 经理模块

**主组件**: `ManagerStatistics.vue` (428行)

**作用**: 经理数据统计和报表分析

**核心功能**:
- 选择时间范围统计
- 收入统计分析
- 房间使用率统计
- 数据可视化图表

**子组件**:

| 组件 | 文件 | 作用 | 行数 |
|------|------|------|------|
| 时间选择器 | `TimeRangeSelector.vue` | 选择统计时间范围 | 156行 |
| 统计概览 | `StatisticsOverview.vue` | 显示关键指标卡片 | 124行 |
| 风速分布图 | `FanSpeedChart.vue` | 风速使用分布饼图 | 198行 |
| 房间详情表 | `RoomDetailsTable.vue` | 房间统计详情表格 | 215行 |

---

### 4️⃣ room/ - 房间控制模块

**主组件**: `RoomClient.vue` (486行)

**作用**: 客户房间控制面板

**核心功能**:
- 空调开关机
- 温度调节（18-30°C）
- 风速控制（低/中/高）
- 模式切换（制冷/制热）
- 实时费用显示

**子组件**:

| 组件 | 文件 | 作用 | 行数 |
|------|------|------|------|
| 房间选择对话框 | `RoomSelectionDialog.vue` | 选择房间号 | 128行 |
| 温度显示 | `TemperatureDisplay.vue` | 大屏温度显示 | 156行 |
| 温度控制 | `TemperatureControl.vue` | 温度调节滑块 | 187行 |
| 风速控制 | `FanSpeedControl.vue` | 风速三档切换 | 142行 |
| 模式控制 | `ModeControl.vue` | 制冷/制热模式切换 | 165行 |
| 计费显示 | `BillingDisplay.vue` | 实时费用显示 | 132行 |

---

### 5️⃣ homepage/ - 首页模块

**主组件**: `Homepage.vue` (367行)

**作用**: 系统首页和角色选择

**核心功能**:
- 酒店介绍轮播图
- 角色登录选项
- 系统功能展示
- 实时统计数据

**子组件**:

| 组件 | 文件 | 作用 | 行数 |
|------|------|------|------|
| 轮播图 | `HotelCarousel.vue` | 酒店图片轮播 | 145行 |
| 登录选项 | `LoginOptions.vue` | 四个角色选择卡片 | 178行 |
| 系统统计 | `SystemStats.vue` | 实时系统数据展示 | 123行 |
| 功能展示 | `FeatureShowcase.vue` | 系统功能介绍 | 156行 |
| 页脚 | `HotelFooter.vue` | 版权信息、联系方式 | 89行 |

---

### 6️⃣ views/ - 页面级组件

| 组件 | 文件 | 作用 | 行数 |
|------|------|------|------|
| 主布局 | `MainLayout.vue` | 应用主布局框架 | 234行 |
| 登录页 | `Login.vue` | 用户登录页面 | 198行 |
| 404页面 | `NotFound.vue` | 页面未找到 | 87行 |

---

### 7️⃣ common/ - 公共组件

**可复用的通用组件**

| 组件 | 文件 | 作用 | 使用场景 |
|------|------|------|----------|
| 消息提示 | `Message.vue` | 成功/错误/警告提示 | 全局消息通知 |
| 模态对话框 | `Modal.vue` | 确认/提示对话框 | 需要用户确认的操作 |

---

## 💼 服务层详解

### ACService.ts - 空调服务 (570行)

**职责**: 管理空调状态、温度模拟、费用计算

**核心方法**:

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `turnOn(roomId, config)` | 房间ID、配置 | Promise<RoomState> | 空调开机 |
| `turnOff(roomId)` | 房间ID | Promise<RoomState> | 空调关机 |
| `adjustTemperature(roomId, temp)` | 房间ID、目标温度 | Promise<void> | 调节温度 |
| `adjustFanSpeed(roomId, speed)` | 房间ID、风速 | Promise<void> | 调节风速 |
| `getRoomState(roomId)` | 房间ID | RoomState | 获取房间状态 |
| `startTemperatureSimulation()` | - | void | 启动温度模拟 |

**使用示例**:
```typescript
// 开机
await acService.turnOn('101', {
  targetTemp: 25,
  fanSpeed: FanSpeed.MEDIUM,
  mode: ACMode.COOLING
});

// 调温
await acService.adjustTemperature('101', 22);
```

---

### Scheduler.ts - 调度服务 (500行)

**职责**: 服务队列管理、优先级调度、时间片轮转

**核心方法**:

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `handleRequest(request)` | 服务请求 | Promise<ServiceResult> | 处理温控请求 |
| `getServiceQueue()` | - | ServiceObject[] | 获取服务队列 |
| `getWaitingQueue()` | - | WaitingObject[] | 获取等待队列 |
| `releaseService(roomId)` | 房间ID | void | 释放服务对象 |

**调度算法**:
1. **优先级调度**: 高风速优先获得服务
2. **时间片轮转**: 服务对象轮流获得CPU时间
3. **等待队列**: 服务满载时进入等待队列

---

### BillingService.ts - 计费服务 (280行)

**职责**: 费用计算、账单生成、统计报表

**核心方法**:

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `generateBill(roomId)` | 房间ID | Bill | 生成账单 |
| `calculateCost(detailRecords)` | 详单记录 | number | 计算总费用 |
| `generateStatistics(timeRange)` | 时间范围 | Statistics | 生成统计报表 |

**计费规则**:
```typescript
// 风速费率
const COST_PER_UNIT = {
  [FanSpeed.LOW]: 0.6,    // 低风: ¥0.6/度
  [FanSpeed.MEDIUM]: 0.8, // 中风: ¥0.8/度
  [FanSpeed.HIGH]: 1.0    // 高风: ¥1.0/度
};
```

---

### CentralController.ts - 中央控制器 (420行)

**职责**: 协调各服务、统一入口、状态同步

**核心方法**:

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `checkIn(data)` | 入住数据 | Promise<CheckInResult> | 办理入住 |
| `checkout(roomId)` | 房间ID | Promise<Bill> | 办理退房 |
| `handleACRequest(request)` | 温控请求 | Promise<void> | 处理温控请求 |

---

### ApiAdapter.ts - API 适配器 (400行)

**职责**: 切换 Mock/API 模式、数据格式转换

**模式切换**:
```typescript
// config/index.ts
export const API_MODE: 'mock' | 'api' = 'api';

// ApiAdapter 根据模式自动选择数据源
if (API_MODE === 'api') {
  // 调用真实后端 API
  return await api.frontDesk.checkIn(data);
} else {
  // 使用 Mock 数据
  return mockCheckInService(data);
}
```

---

## 🔌 接口层详解

### hvac.ts - 接口定义 (150行)

**接口分类**:

| 模块 | 接口对象 | 说明 |
|------|----------|------|
| 房间控制 | `api.room.*` | 开关机、调温调风、状态查询 |
| 前台管理 | `api.frontDesk.*` | 入住、退房、账单查询 |
| 管理员 | `api.admin.*` | 队列查询、批量操作 |
| 经理统计 | `api.manager.*` | 统计报表、数据分析 |

**接口示例**:
```typescript
export const api = {
  room: {
    // 开机
    turnOn: (roomId: string) => 
      request.post(`/room/${roomId}/turnon`),
    
    // 温控请求
    sendRequest: (roomId: string, data: ServiceRequestDTO) =>
      request.post(`/room/${roomId}/request`, data),
  },
  
  frontDesk: {
    // 办理入住
    checkIn: (data: CheckInDTO) =>
      request.post('/frontdesk/checkin', data),
      
    // 办理退房
    checkOut: (roomId: string) =>
      request.post(`/frontdesk/checkout/${roomId}`),
  }
};
```

---

### request.ts - HTTP 请求封装 (120行)

**功能**:
- 统一的请求/响应拦截器
- 错误处理
- 请求超时控制
- 自动添加 base URL

**封装示例**:
```typescript
import axios from 'axios';
import { API_BASE_URL } from '@/config';

const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// 请求拦截器
request.interceptors.request.use(config => {
  // 可以添加 token 等
  return config;
});

// 响应拦截器
request.interceptors.response.use(
  response => response.data,
  error => {
    // 统一错误处理
    console.error('请求失败:', error);
    return Promise.reject(error);
  }
);
```

---

## 🪝 组合式函数

### useDialog.ts - 弹窗系统 (180行)

**提供的弹窗方法**:

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `showSuccess(message)` | 消息内容 | void | 成功提示 |
| `showError(message)` | 消息内容 | void | 错误提示 |
| `showWarning(message)` | 消息内容 | void | 警告提示 |
| `showInfo(message)` | 消息内容 | void | 信息提示 |
| `showConfirm(title, message)` | 标题、内容 | Promise<boolean> | 确认对话框 |
| `showAlert(title, message)` | 标题、内容 | Promise<void> | 提示对话框 |

**使用示例**:
```typescript
import { showSuccess, showConfirm } from '@/composables/useDialog';

// 成功提示
showSuccess('操作成功！');

// 确认对话框
const confirmed = await showConfirm('确认操作', '确定要执行此操作吗？');
if (confirmed) {
  // 用户点击了确定
}
```

---

## 📝 类型定义

### types/index.ts - TypeScript 类型 (136行)

**核心类型**:

```typescript
// 房间状态
export interface RoomState {
  roomId: string;
  guestName: string;
  checkedIn: boolean;
  isOn: boolean;
  currentTemp: number;
  targetTemp: number;
  fanSpeed: FanSpeed;
  mode: ACMode;
  status: RoomStatus;
  currentCost: number;
  currentPowerConsumption: number;
}

// 枚举类型
export enum FanSpeed {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH'
}

export enum ACMode {
  COOLING = 'COOLING',
  HEATING = 'HEATING'
}

export enum RoomStatus {
  OFF = 'OFF',
  STANDBY = 'STANDBY',
  SERVING = 'SERVING',
  WAITING = 'WAITING',
  TARGET_REACHED = 'TARGET_REACHED'
}

// 账单
export interface Bill {
  roomId: string;
  guestName: string;
  checkInTime: string;
  checkOutTime: string;
  totalDuration: number;
  totalCost: number;
  roomFee: number;
  acCost: number;
  detailRecords: DetailRecord[];
}

// 详单记录
export interface DetailRecord {
  startTime: string;
  endTime: string;
  fanSpeed: FanSpeed;
  duration: number;
  cost: number;
  powerConsumption: number;
}
```

---

## 🔢 常量配置

### constants/index.ts - 系统常量 (80行)

```typescript
// 温度范围
export const TEMP_RANGE = {
  COOLING: { min: 18, max: 25, default: 22 },
  HEATING: { min: 25, max: 30, default: 28 }
};

// 费率
export const COST_RATES = {
  LOW: 0.6,
  MEDIUM: 0.8,
  HIGH: 1.0
};

// 调度配置
export const SCHEDULER_CONFIG = {
  MAX_SERVICE_OBJECTS: 5,    // 最大服务对象数
  TIME_SLICE: 120,           // 时间片（秒）
  WAIT_TIMEOUT: 300          // 等待超时（秒）
};

// 温度更新间隔
export const TEMP_UPDATE_INTERVAL = 1000; // 毫秒
```

---

## 🎨 架构亮点

### 1. 模块化设计

- **组件拆分**: 大组件拆分为小组件（CheckInForm: 1364行 → 250行 + 5个子组件）
- **功能分类**: 按业务模块组织目录（admin/frontdesk/manager/room）
- **高内聚低耦合**: 每个组件职责单一，依赖最小化

### 2. 分层架构

- **组件层**: 专注 UI 展示和用户交互
- **服务层**: 处理业务逻辑和数据
- **接口层**: 统一 API 调用

### 3. 状态管理

- **响应式数据**: 使用 Vue 3 Composition API
- **服务单例**: 全局唯一的服务实例
- **状态同步**: 自动更新和通知

### 4. 错误处理

- **统一拦截**: 请求/响应拦截器
- **友好提示**: 自定义弹窗系统
- **异常捕获**: try-catch 包裹关键操作

---

## 🎯 开发规范

### 组件命名

- **大驼峰命名**: `CheckInForm.vue`
- **见名知意**: 组件名清晰表达功能
- **避免缩写**: 除非是通用缩写（如 AC、API）

### 文件组织

```
功能模块/
├── MainComponent.vue          # 主组件
├── SubComponent1.vue          # 子组件1
├── SubComponent2.vue          # 子组件2
└── subfolder/                 # 更细粒度的子组件
    ├── DetailComponent1.vue
    └── DetailComponent2.vue
```

### 代码风格

```vue
<template>
  <!-- 模板内容 -->
</template>

<script setup lang="ts">
// 导入
import { ref, computed, onMounted } from 'vue';

// 类型定义
interface Props {
  title: string;
}

// 属性和状态
const props = defineProps<Props>();
const count = ref(0);

// 计算属性
const doubleCount = computed(() => count.value * 2);

// 方法
const increment = () => {
  count.value++;
};

// 生命周期
onMounted(() => {
  // 初始化逻辑
});
</script>

<style scoped>
/* 组件样式 */
</style>
```

---

## 🔗 相关文档

- [快速启动指南](QUICKSTART.md) - 项目安装和启动
- [入住流程文档](CHECKIN_PROCESS.md) - 详细业务流程说明
- [API 使用指南](API_GUIDE.md) - 接口对接文档
- [后端文档](../../back-end/docs) - 后端 API 详情

---

**Happy Coding!** 🎉
