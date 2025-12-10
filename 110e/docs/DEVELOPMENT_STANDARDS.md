# 📋 前端开发规范文档

本文档定义了酒店中央温控系统前端项目的开发规范和最佳实践，旨在保持代码一致性、可维护性和高质量。

---

## 📑 目录

1. [项目技术栈](#项目技术栈)
2. [代码规范](#代码规范)
3. [Vue 组件开发规范](#vue-组件开发规范)
4. [TypeScript 使用规范](#typescript-使用规范)
5. [API 调用规范](#api-调用规范)
6. [样式编写规范](#样式编写规范)
7. [命名规范](#命名规范)
8. [Git 提交规范](#git-提交规范)
9. [性能优化建议](#性能优化建议)
10. [代码审查清单](#代码审查清单)

---

## 🛠 项目技术栈

- **框架**: Vue 3 (Composition API)
- **语言**: TypeScript 5.x
- **构建工具**: Vite 5.x
- **路由**: Vue Router 4.x
- **HTTP 客户端**: Axios
- **代码规范**: ESLint + Prettier
- **样式**: CSS3 (Scoped Styles)

---

## 📝 代码规范

### 1. 基础规则

#### 缩进与格式
```typescript
// ✅ 正确：使用 2 空格缩进
const greeting = (name: string): string => {
  return `Hello, ${name}!`;
};

// ❌ 错误：使用 4 空格或 Tab
const greeting = (name: string): string => {
    return `Hello, ${name}!`;
};
```

#### 分号使用
```typescript
// ✅ 正确：统一使用分号
const name = 'John';
const age = 25;

// ❌ 错误：不一致的分号使用
const name = 'John'
const age = 25;
```

#### 引号使用
```typescript
// ✅ 正确：字符串统一使用单引号
const message = 'Hello World';

// ✅ 正确：模板字符串使用反引号
const greeting = `Welcome, ${userName}!`;

// ❌ 错误：混用双引号
const message = "Hello World";
```

### 2. 注释规范

#### 文件注释
```typescript
/**
 * @file ACService.ts
 * @description 空调服务模块，处理空调控制的核心逻辑
 * @author Your Name
 * @date 2025-12-05
 */
```

#### 函数注释
```typescript
/**
 * 处理入住请求
 * @param roomId - 房间号
 * @param guestInfo - 客人信息
 * @returns Promise<CheckInResponse> 入住结果
 * @throws {Error} 当房间不可用时抛出错误
 */
async function handleCheckIn(
  roomId: string, 
  guestInfo: GuestInfo
): Promise<CheckInResponse> {
  // 实现代码...
}
```

#### 复杂逻辑注释
```typescript
// ✅ 正确：为复杂逻辑添加说明性注释
// 计算房费：房费 = 单价 × 天数，不满1天按1天计算
const stayDays = Math.ceil((checkOutTime - checkInTime) / (1000 * 60 * 60 * 24));
const roomCharge = roomRate * Math.max(stayDays, 1);

// ❌ 错误：无意义的注释
// 声明变量 x
const x = 10;
```

### 3. 代码整洁

#### 保持函数简短
```typescript
// ✅ 正确：单一职责，易于测试
const calculateRoomFee = (rate: number, days: number): number => {
  return rate * days;
};

const calculateACFee = (powerConsumption: number, pricePerKwh: number): number => {
  return powerConsumption * pricePerKwh;
};

const calculateTotalBill = (roomFee: number, acFee: number): number => {
  return roomFee + acFee;
};

// ❌ 错误：函数过长，职责不清
const calculateBill = (/* 大量参数 */) => {
  // 100+ 行代码...
};
```

#### 避免魔法数字
```typescript
// ✅ 正确：使用常量
const DEFAULT_ROOM_RATE = 280;
const DEFAULT_DEPOSIT = 200;
const PRICE_PER_KWH = 1.0;

// ❌ 错误：直接使用魔法数字
if (amount > 280) { /* ... */ }
```

---

## 🎨 Vue 组件开发规范

### 1. 组件结构顺序

```vue
<template>
  <!-- 模板内容 -->
</template>

<script setup lang="ts">
// 1. 导入语句
import { ref, computed, onMounted } from 'vue';
import type { PropType } from 'vue';

// 2. Props 定义
const props = defineProps<{
  roomId: string;
  isActive?: boolean;
}>();

// 3. Emits 定义
const emit = defineEmits<{
  update: [value: string];
  close: [];
}>();

// 4. 响应式数据
const count = ref(0);
const isLoading = ref(false);

// 5. 计算属性
const doubleCount = computed(() => count.value * 2);

// 6. 方法
const handleClick = () => {
  count.value++;
};

// 7. 生命周期钩子
onMounted(() => {
  console.log('Component mounted');
});
</script>

<style scoped>
/* 样式内容 */
</style>
```

### 2. 组件命名

```typescript
// ✅ 正确：使用 PascalCase
components/
  ├── FrontDeskBilling.vue      // 多单词组件名
  ├── CheckInForm.vue
  └── bill/
      ├── BillHeader.vue
      ├── ChargesBreakdown.vue
      └── ACUsageRecords.vue

// ❌ 错误
components/
  ├── billing.vue               // 小写
  ├── CheckInform.vue           // 大小写不一致
  └── AC-usage.vue              // 使用连字符
```

### 3. Props 定义规范

```typescript
// ✅ 正确：使用 TypeScript 定义 Props
defineProps<{
  roomId: string;                    // 必填属性
  roomRate?: number;                 // 可选属性
  isActive?: boolean;
  items: string[];                   // 数组
  config: Record<string, any>;       // 对象
}>();

// ✅ 正确：使用 PropType 定义复杂类型
import type { PropType } from 'vue';

defineProps({
  bill: {
    type: Object as PropType<Bill>,
    required: true
  },
  records: {
    type: Array as PropType<DetailRecord[]>,
    default: () => []
  }
});

// ❌ 错误：缺少类型定义
defineProps({
  roomId: String,                   // 应使用 TypeScript 类型
  items: Array                      // 缺少具体类型
});
```

### 4. 组件拆分原则

#### 单一职责
```vue
<!-- ✅ 正确：每个组件只负责一个功能 -->
<!-- BillHeader.vue - 只负责账单头部 -->
<!-- ChargesBreakdown.vue - 只负责费用明细 -->
<!-- ACUsageRecords.vue - 只负责空调使用详单 -->

<!-- ❌ 错误：一个组件包含所有功能 -->
<!-- BillDetail.vue - 2000+ 行代码，包含所有逻辑 -->
```

#### 组件粒度
- **容器组件** (100-200 行)：负责数据获取和业务逻辑
- **展示组件** (50-100 行)：只负责 UI 展示
- **基础组件** (< 50 行)：可复用的基础元素

```vue
<!-- ✅ 正确：合理的组件层次 -->
<FrontDeskBilling>           <!-- 容器组件 -->
  <CheckInForm>              <!-- 业务组件 -->
    <RoomSelector />         <!-- 展示组件 -->
    <GuestInfoInput />       <!-- 展示组件 -->
  </CheckInForm>
</FrontDeskBilling>
```

### 5. Emits 使用规范

```typescript
// ✅ 正确：明确定义事件类型
const emit = defineEmits<{
  update: [value: string];           // 单个参数
  submit: [data: FormData];
  close: [];                         // 无参数
  change: [id: string, value: number]; // 多个参数
}>();

// 触发事件
emit('update', 'new value');
emit('change', 'room-101', 25);

// ❌ 错误：没有类型定义
const emit = defineEmits(['update', 'close']);
emit('update', 'value');  // 缺少类型检查
```

### 6. Ref 和 Reactive 使用

```typescript
// ✅ 正确：基本类型使用 ref
const count = ref(0);
const name = ref('');
const isActive = ref(false);

// ✅ 正确：对象使用 reactive 或 ref
const state = reactive({
  roomId: '',
  temperature: 26,
  isRunning: false
});

// 或者
const state = ref({
  roomId: '',
  temperature: 26,
  isRunning: false
});

// ❌ 错误：解构后失去响应性
const { roomId } = reactive({ roomId: '101' });  // 失去响应性

// ✅ 正确：使用 toRefs
const state = reactive({ roomId: '101' });
const { roomId } = toRefs(state);  // 保持响应性
```

---

## 🔷 TypeScript 使用规范

### 1. 类型定义

```typescript
// ✅ 正确：在 types/index.ts 中统一定义类型
export interface Room {
  roomId: string;
  isOccupied: boolean;
  currentTemp: number;
  targetTemp?: number;
  fanSpeed?: FanSpeed;
  mode?: ACMode;
}

export type FanSpeed = 'LOW' | 'MEDIUM' | 'HIGH';
export type ACMode = 'HEAT' | 'COOL';

// ✅ 正确：使用类型别名简化复杂类型
export type RoomID = string;
export type Timestamp = number;
export type Temperature = number;

// ❌ 错误：使用 any
const data: any = fetchData();  // 失去类型检查
```

### 2. 接口 vs 类型别名

```typescript
// ✅ 接口：用于定义对象结构
interface Bill {
  roomId: string;
  checkInTime: number;
  checkOutTime: number;
  totalCost: number;
}

// ✅ 类型别名：用于联合类型、交叉类型、函数类型
type Status = 'pending' | 'success' | 'error';
type Handler = (data: string) => void;
type Combined = TypeA & TypeB;
```

### 3. 函数类型注解

```typescript
// ✅ 正确：完整的类型注解
const calculateTotal = (
  roomFee: number, 
  acCost: number
): number => {
  return roomFee + acCost;
};

// ✅ 正确：异步函数
const fetchBill = async (roomId: string): Promise<Bill> => {
  const response = await api.getBill(roomId);
  return response.data;
};

// ❌ 错误：缺少返回类型
const calculateTotal = (roomFee: number, acCost: number) => {
  return roomFee + acCost;  // 应明确标注返回类型
};
```

### 4. 类型守卫

```typescript
// ✅ 正确：使用类型守卫
function isBill(obj: any): obj is Bill {
  return 'roomId' in obj && 'totalCost' in obj;
}

const data = fetchData();
if (isBill(data)) {
  // TypeScript 知道 data 是 Bill 类型
  console.log(data.roomId);
}

// ✅ 正确：可选链和空值合并
const roomId = bill?.roomId ?? 'unknown';
```

### 5. 泛型使用

```typescript
// ✅ 正确：使用泛型提高代码复用性
interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

const fetchData = async <T>(url: string): Promise<ApiResponse<T>> => {
  const response = await axios.get(url);
  return response.data;
};

// 使用
const billData = await fetchData<Bill>('/api/bill/room-101');
```

---

## 🌐 API 调用规范

### 1. API 封装

```typescript
// ✅ 正确：在 api/hvac.ts 中统一封装 API
import request from './request';

export const hvacApi = {
  // 获取账单
  getBill: (roomId: string) => 
    request.get<Bill>(`/api/billing/${roomId}`),
  
  // 调整温度
  adjustTemperature: (roomId: string, targetTemp: number) =>
    request.post('/api/room/adjust-temp', { roomId, targetTemp }),
  
  // 切换风速
  changeFanSpeed: (roomId: string, fanSpeed: FanSpeed) =>
    request.post('/api/room/change-fan-speed', { roomId, fanSpeed })
};

// ❌ 错误：在组件中直接调用 axios
const bill = await axios.get('/api/billing/room-101');
```

### 2. 错误处理

```typescript
// ✅ 正确：统一的错误处理
const fetchBill = async (roomId: string) => {
  try {
    const response = await hvacApi.getBill(roomId);
    if (response.code === 200) {
      return response.data;
    } else {
      throw new Error(response.message);
    }
  } catch (error) {
    console.error('获取账单失败:', error);
    ElMessage.error('获取账单失败，请重试');
    throw error;
  }
};

// ❌ 错误：忽略错误
const fetchBill = async (roomId: string) => {
  const response = await hvacApi.getBill(roomId);
  return response.data;  // 没有错误处理
};
```

### 3. 加载状态管理

```typescript
// ✅ 正确：管理加载状态
const isLoading = ref(false);
const error = ref<string | null>(null);

const fetchData = async () => {
  isLoading.value = true;
  error.value = null;
  
  try {
    const data = await hvacApi.getBill(roomId);
    // 处理数据...
  } catch (err) {
    error.value = (err as Error).message;
  } finally {
    isLoading.value = false;
  }
};
```

### 4. API 请求优化

```typescript
// ✅ 正确：使用防抖避免频繁请求
import { debounce } from 'lodash-es';

const searchRooms = debounce(async (keyword: string) => {
  const results = await hvacApi.searchRooms(keyword);
  // 处理结果...
}, 300);

// ✅ 正确：取消未完成的请求
const controller = new AbortController();

onUnmounted(() => {
  controller.abort();
});

const fetchData = async () => {
  await fetch('/api/data', { signal: controller.signal });
};
```

---

## 🎨 样式编写规范

### 1. Scoped 样式

```vue
<!-- ✅ 正确：使用 scoped 避免样式污染 -->
<style scoped>
.bill-header {
  display: flex;
  justify-content: space-between;
  padding: 20px;
}

.header-title {
  font-size: 24px;
  font-weight: 600;
}
</style>

<!-- ❌ 错误：全局样式可能污染其他组件 -->
<style>
.header {  /* 太通用的类名 */
  padding: 20px;
}
</style>
```

### 2. CSS 类命名

```css
/* ✅ 正确：BEM 命名法 */
.bill-header { }
.bill-header__title { }
.bill-header__actions { }
.bill-header--collapsed { }

/* ✅ 正确：语义化命名 */
.charge-breakdown { }
.charge-row { }
.charge-amount { }

/* ❌ 错误：无意义的命名 */
.box1 { }
.container2 { }
.div-wrapper { }
```

### 3. 样式组织

```css
/* ✅ 正确：按功能分组 */
/* 布局 */
.bill-detail {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 文字样式 */
.bill-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

/* 交互样式 */
.btn-print:hover {
  background-color: #1e40af;
  transform: translateY(-2px);
}
```

### 4. 响应式设计

```css
/* ✅ 正确：移动优先 */
.container {
  padding: 12px;
}

@media (min-width: 768px) {
  .container {
    padding: 24px;
  }
}

@media (min-width: 1024px) {
  .container {
    padding: 32px;
  }
}
```

### 5. CSS 变量

```css
/* ✅ 正确：使用 CSS 变量统一主题 */
:root {
  --color-primary: #3b82f6;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  
  --border-radius: 8px;
  --transition-duration: 0.3s;
}

.button {
  background-color: var(--color-primary);
  padding: var(--spacing-md);
  border-radius: var(--border-radius);
  transition: all var(--transition-duration);
}
```

---

## 📛 命名规范

### 1. 文件命名

```
✅ 正确：
components/
  ├── FrontDeskBilling.vue        # PascalCase
  ├── CheckInForm.vue
  └── bill/
      ├── BillHeader.vue
      └── ChargesBreakdown.vue

api/
  ├── hvac.ts                     # camelCase
  └── request.ts

types/
  └── index.ts

❌ 错误：
components/
  ├── frontdeskBilling.vue        # 不统一
  ├── check-in-form.vue           # kebab-case
  └── Bill_Header.vue             # snake_case
```

### 2. 变量命名

```typescript
// ✅ 正确：camelCase
const roomRate = 280;
const isLoading = ref(false);
const totalPowerConsumption = 8.35;

// ✅ 正确：常量使用 UPPER_SNAKE_CASE
const DEFAULT_ROOM_RATE = 280;
const MAX_TEMPERATURE = 30;
const API_BASE_URL = 'http://localhost:8080';

// ❌ 错误：不清晰的命名
const data = fetchData();  // 太泛化
const temp = 26;           // 缩写不清晰
const flag = true;         // 无意义的命名
```

### 3. 函数命名

```typescript
// ✅ 正确：动词开头，清晰表达意图
const fetchBillData = async () => { };
const handleCheckIn = () => { };
const validateGuestInfo = () => { };
const calculateTotalCost = () => { };
const isRoomAvailable = () => { };  // 布尔值返回

// ❌ 错误：无意义或不清晰
const bill = () => { };        // 应该是 fetchBill 或 getBill
const data = () => { };        // 太泛化
const doSomething = () => { }; // 无意义
```

### 4. 组件命名

```typescript
// ✅ 正确：多单词、PascalCase
const FrontDeskBilling = { };
const CheckInForm = { };
const ACUsageRecords = { };

// ❌ 错误：单个单词或不规范
const Billing = { };      // 应该更具体
const checkin = { };      // 应该是 PascalCase
const AC_Usage = { };     // 不应该使用下划线
```

---

## 🚀 Git 提交规范

### 1. Commit Message 格式

```bash
<type>(<scope>): <subject>

<body>

<footer>
```

### 2. Type 类型

- **feat**: 新功能
- **fix**: Bug 修复
- **docs**: 文档更新
- **style**: 代码格式调整（不影响功能）
- **refactor**: 重构（既不是新功能也不是 Bug 修复）
- **perf**: 性能优化
- **test**: 测试相关
- **chore**: 构建过程或辅助工具的变动

### 3. 示例

```bash
# ✅ 正确
feat(billing): 添加账单打印功能

- 实现账单 HTML 生成逻辑
- 支持费用明细展示
- 添加押金说明模块

Closes #123

# ✅ 正确
fix(billing): 修复打印账单费用计算错误

修复空调使用费显示为总费用而不是单独空调费的问题
- 将 bill.totalCost 改为 bill.acCost
- 修正小计计算逻辑

# ❌ 错误
update code          # 太简略
修复bug              # 缺少详细信息
feat: 更新           # 没有说明更新了什么
```

### 4. 分支命名

```bash
# ✅ 正确
feature/add-bill-print        # 新功能
bugfix/fix-fee-calculation   # Bug 修复
hotfix/urgent-security-fix   # 紧急修复
refactor/optimize-components # 重构

# ❌ 错误
dev                  # 太泛化
fix                  # 不清晰
update-code          # 无意义
```

---

## ⚡ 性能优化建议

### 1. 组件懒加载

```typescript
// ✅ 正确：路由懒加载
const routes = [
  {
    path: '/frontdesk',
    component: () => import('@/components/frontdesk/FrontDeskBilling.vue')
  },
  {
    path: '/manager',
    component: () => import('@/components/manager/ManagerDashboard.vue')
  }
];
```

### 2. 计算属性缓存

```typescript
// ✅ 正确：使用 computed 缓存计算结果
const totalCost = computed(() => {
  return bill.value.roomFee + bill.value.acCost;
});

// ❌ 错误：每次访问都重新计算
const getTotalCost = () => {
  return bill.value.roomFee + bill.value.acCost;
};
```

### 3. 避免不必要的响应式

```typescript
// ✅ 正确：静态数据不需要响应式
const FAN_SPEED_OPTIONS = ['LOW', 'MEDIUM', 'HIGH'];
const ROOM_RATE = 280;

// ❌ 错误：常量不需要 ref
const FAN_SPEED_OPTIONS = ref(['LOW', 'MEDIUM', 'HIGH']);
```

### 4. 合理使用 v-if 和 v-show

```vue
<!-- ✅ v-if: 条件很少改变 -->
<div v-if="isAdmin">
  <AdminPanel />
</div>

<!-- ✅ v-show: 频繁切换 -->
<div v-show="isDialogVisible">
  <Dialog />
</div>
```

### 5. 列表渲染优化

```vue
<!-- ✅ 正确：使用唯一 key -->
<div v-for="record in records" :key="record.id">
  {{ record.name }}
</div>

<!-- ❌ 错误：使用 index 作为 key -->
<div v-for="(record, index) in records" :key="index">
  {{ record.name }}
</div>
```

---

## ✅ 代码审查清单

### 提交前自检

- [ ] 代码符合 ESLint 规则
- [ ] 所有函数都有清晰的类型定义
- [ ] 组件职责单一，不超过 200 行
- [ ] 添加了必要的注释
- [ ] 移除了 console.log 和调试代码
- [ ] 错误处理完善
- [ ] 使用了语义化的命名
- [ ] 样式使用了 scoped
- [ ] Commit message 符合规范

### 代码审查关注点

#### 功能性
- [ ] 代码实现了预期功能
- [ ] 边界情况处理正确
- [ ] 错误处理完善

#### 可维护性
- [ ] 代码易于理解
- [ ] 组件拆分合理
- [ ] 没有重复代码

#### 性能
- [ ] 没有不必要的重新渲染
- [ ] 列表使用了合适的 key
- [ ] 大数据使用了虚拟滚动

#### 安全性
- [ ] 没有 XSS 漏洞
- [ ] 敏感信息不在前端暴露
- [ ] API 调用有权限验证

---

## 📚 参考资源

- [Vue 3 官方文档](https://vuejs.org/)
- [TypeScript 官方文档](https://www.typescriptlang.org/)
- [Vue Style Guide](https://vuejs.org/style-guide/)
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## 🔄 文档更新

本规范文档会根据项目演进持续更新。如有建议或疑问，请在团队会议中提出。

**最后更新**: 2025-12-05
**维护者**: 前端开发团队
