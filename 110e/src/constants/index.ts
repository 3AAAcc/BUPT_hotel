import { ACMode, FanSpeed } from '../types';

// 温控范围
export const TEMP_RANGE = {
  [ACMode.COOLING]: { min: 18, max: 25 },
  [ACMode.HEATING]: { min: 25, max: 30 }
};

// 默认温度
export const DEFAULT_TEMP = 25;

// 温度调节步长
export const TEMP_STEP = 0.5;

// 初始环境温度（根据模式）
export const INITIAL_TEMP = {
  [ACMode.COOLING]: 30, // 制冷模式下初始温度较高
  [ACMode.HEATING]: 15  // 制热模式下初始温度较低
};

// 计费标准（元/度）
export const BILLING_RATE = 1;

// 耗电标准（度/分钟）
export const POWER_CONSUMPTION_RATE = {
  [FanSpeed.HIGH]: 1,     // 1度/分钟
  [FanSpeed.MEDIUM]: 0.5,  // 1度/2分钟
  [FanSpeed.LOW]: 1/3     // 1度/3分钟
};

// 温度变化率（度/分钟）
export const TEMP_CHANGE_RATE = {
  [FanSpeed.MEDIUM]: 0.5,           // 中风：0.5度/分钟
  [FanSpeed.HIGH]: 0.5 * 1.2,       // 高风：提高20%
  [FanSpeed.LOW]: 0.5 * 0.8         // 低风：减少20%
};

// 关机状态下温度变化率（度/分钟）
export const TEMP_CHANGE_RATE_OFF = 0.5;

// 目标温度偏离阈值（度）
export const TEMP_DEVIATION_THRESHOLD = 1;

// 最大服务对象数量（根据中央空调服务能力配置，表示同时最多可为多少间房间送风）
export const MAX_SERVICE_OBJECTS = 5;

// 等待时长（秒，默认值，可配置）
export const WAIT_TIME = 120; // 2分钟

// 温度更新间隔（毫秒）
export const TEMP_UPDATE_INTERVAL = 1000; // 每秒更新一次

// 指令防抖时间（毫秒）
export const COMMAND_DEBOUNCE_TIME = 1000; // 1秒

// 风速优先级
export const FAN_SPEED_PRIORITY = {
  [FanSpeed.HIGH]: 3,
  [FanSpeed.MEDIUM]: 2,
  [FanSpeed.LOW]: 1
};

// 房间数量（默认配置）
export const TOTAL_ROOMS = 20;

// 可用房间列表（房间号：101-108, 201-206, 301-306）
export const ROOM_IDS = [
  // 1楼：101-108
  ...Array.from({ length: 8 }, (_, i) => `${101 + i}`),
  // 2楼：201-206
  ...Array.from({ length: 6 }, (_, i) => `${201 + i}`),
  // 3楼：301-306
  ...Array.from({ length: 6 }, (_, i) => `${301 + i}`)
];

