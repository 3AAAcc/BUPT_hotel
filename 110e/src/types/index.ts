// 空调模式 - 与后端枚举保持一致（大写）
export const ACMode = {
  COOLING: 'COOLING' as const,
  HEATING: 'HEATING' as const
};
export type ACMode = typeof ACMode[keyof typeof ACMode];

// 风速等级 - 与后端枚举保持一致（大写）
export const FanSpeed = {
  LOW: 'LOW' as const,
  MEDIUM: 'MEDIUM' as const,
  HIGH: 'HIGH' as const
};
export type FanSpeed = typeof FanSpeed[keyof typeof FanSpeed];

// 房间状态 - 与后端枚举保持一致（大写）
export const RoomStatus = {
  OFF: 'OFF' as const,
  STANDBY: 'STANDBY' as const,
  SERVING: 'SERVING' as const,
  WAITING: 'WAITING' as const,
  TARGET_REACHED: 'TARGET_REACHED' as const
};
export type RoomStatus = typeof RoomStatus[keyof typeof RoomStatus];

// 服务请求
export interface ServiceRequest {
  roomId: string;
  targetTemp: number;
  fanSpeed: FanSpeed;
  timestamp: number;
  currentTemp: number;
}

// 服务对象
export interface ServiceObject {
  id: string;
  roomId: string;
  fanSpeed: FanSpeed;
  targetTemp: number;
  currentTemp: number;
  serviceStartTime: number;
  serviceDuration: number; // 服务时长（秒）
  powerConsumption: number; // 耗电量（度）
  cost: number; // 费用（元）
}

// 等待对象
export interface WaitingObject {
  roomId: string;
  fanSpeed: FanSpeed;
  targetTemp: number;
  currentTemp: number;
  waitStartTime: number;
  waitDuration: number; // 已等待时长（秒）
  assignedWaitTime: number; // 分配的等待时长（秒）
}

// 房型枚举
export const RoomType = {
  STANDARD_SINGLE: 'STANDARD_SINGLE' as const,  // 标准单人间
  STANDARD_DOUBLE: 'STANDARD_DOUBLE' as const,  // 标准双人间
  DELUXE: 'DELUXE' as const,                    // 豪华间
  SUITE: 'SUITE' as const                        // 套间
};
export type RoomType = typeof RoomType[keyof typeof RoomType];

// 房间状态
export interface RoomState {
  roomId: string;
  roomType?: string;             // 房型
  pricePerNight?: number;        // 房费（元/晚）
  floor?: number;                // 楼层
  roomFeatures?: string;         // 房间特色
  isOn: boolean;
  mode: ACMode;
  currentTemp: number;
  initialTemp: number;           // 初始温度
  targetTemp: number;
  fanSpeed: FanSpeed;
  status: RoomStatus;
  totalCost: number;
  totalPowerConsumption: number;
  lastUpdateTime: number;
  serviceStartTime: number | null;
  detailRecords: DetailRecord[]; // 详单记录
}

// 详单记录
export interface DetailRecord {
  timestamp: number;
  action: string; // 操作类型：开机、关机、调温、调风、开始送风、停止送风等
  fanSpeed?: FanSpeed;
  targetTemp?: number;
  currentTemp: number;
  powerConsumption: number; // 本次操作的耗电量
  cost: number; // 本次操作的费用
  duration: number; // 持续时间（秒）
}

// 账单
export interface Bill {
  roomId: string;
  checkInTime: number;
  checkOutTime: number;
  roomFee: number; // 房费总额（后端返回）
  acCost: number; // 空调费用（后端返回）
  totalCost: number; // 总费用 = 房费 + 空调费（后端返回）
  totalPowerConsumption: number; // 总耗电量（度）
  totalServiceDuration: number; // 总服务时长（秒）
  detailRecords: DetailRecord[]; // 空调使用详单
  // 前端计算或可选字段
  roomRate?: number; // 房费单价（元/天）
  stayDays?: number; // 入住天数
  roomCharge?: number; // 房费总额（前端计算，已废弃，使用roomFee）
  deposit?: number; // 押金
  finalAmount?: number; // 最终应付金额（已废弃）
  guestName?: string; // 客户姓名
  guestPhone?: string; // 客户电话
}

// 统计报表数据
export interface StatisticsReport {
  startTime: number;
  endTime: number;
  totalRooms: number;
  totalServiceRequests: number;
  totalCost: number;
  totalPowerConsumption: number;
  averageCostPerRoom: number;
  roomStatistics: RoomStatistics[];
  fanSpeedDistribution: {
    low: number;
    medium: number;
    high: number;
  };
}

// 房间统计
export interface RoomStatistics {
  roomId: string;
  serviceCount: number;
  totalCost: number;
  totalPowerConsumption: number;
  totalServiceDuration: number;
  averageTemp: number;
  mostUsedFanSpeed: FanSpeed;
}

// 入住记录
export interface CheckInRecord {
  roomId: string;
  guestName?: string; // 客户姓名
  guestPhone?: string; // 客户电话
  idCard?: string; // 身份证号
  stayDays?: number; // 入住天数
  expectedCheckoutDate?: number; // 预计退房日期（时间戳）
  roomType?: string; // 房间类型
  pricePerNight?: number; // 房费单价（元/晚）
  totalRoomFee?: number; // 总房费（元）
  deposit?: number; // 押金金额
  depositStatus?: string; // 押金状态
  checkInTime: number; // 入住时间（时间戳）
  actualCheckoutTime?: number | null; // 实际退房时间（时间戳）
  mode: ACMode; // 选择的空调模式（制冷/制热）
  checkedOut: boolean; // 是否已退房
  // 兼容旧字段
  checkInDays?: number; // 入住天数（已废弃，使用 stayDays）
  roomRate?: number; // 房费单价（已废弃，使用 pricePerNight）
}

