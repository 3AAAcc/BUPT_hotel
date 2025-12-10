/**
 * HVAC 系统 API 接口
 */
// @ts-nocheck
/* eslint-env es2020 */
import request from './request';
import type {
  RoomState,
  DetailRecord,
  Bill,
  CheckInRecord,
  StatisticsReport,
  ServiceRequest
} from '../types';
import { ACMode, FanSpeed } from '../types';

// 工具：统一获取房间列表，用于过滤已入住/可用房间
async function fetchRooms(): Promise<any[]> {
  try {
    const rooms = await request.get<any[]>('/hotel/rooms');
    return rooms || [];
  } catch (e) {
    console.error('获取房间列表失败', e);
    return [];
  }
}

/**
 * 前台管理接口
 */
export const frontDeskApi = {
  // 办理入住（支持空调初始化参数）
  checkIn(
    roomId: string,
    guestName: string,
    guestPhone: string,
    idCard: string,
    stayDays: number,
    roomType: string,
    mode?: ACMode,
    roomTemp?: number,
    targetTemp?: number,
    fanSpeed?: FanSpeed
  ) {
    // 后端 /hotel/checkin 接收房间与客户信息
    return request.post('/hotel/checkin', {
      roomId,
      name: guestName,
      phoneNumber: guestPhone,
      idCard,
      stayDays,
      roomType,
      mode: mode || ACMode.COOLING,
      roomTemp: roomTemp ?? 25,
      targetTemp: targetTemp ?? 25,
      fanSpeed: fanSpeed || FanSpeed.MEDIUM
    });
  },

  // 办理退房
  checkOut(roomId: string) {
    return request.post<Bill>(`/hotel/checkout/${roomId}`);
  },

  // 获取账单
  getBill(roomId: string) {
    // 当前后端未提供单独账单查询，退房返回账单，这里直接返回 null 占位
    return Promise.resolve(null as unknown as Bill);
  },

  // 获取所有账单
  getAllBills() {
    // 后端无对应接口，返回空数组占位
    return Promise.resolve([] as Bill[]);
  },

  // 获取已入住房间列表
  getOccupiedRooms() {
    return fetchRooms().then((rooms) =>
      rooms
        .filter((r) => r.status === 'OCCUPIED')
        .map((r) => String(r.id ?? r.roomId ?? r.room_id ?? ''))
        .filter(Boolean)
    );
  },

  // 获取可入住房间列表
  getAvailableRooms(params?: {
    roomType?: string;
    minPrice?: number;
    maxPrice?: number;
    floor?: number;
  }) {
    // 优先调用后端可用房间详情接口，失败回退 rooms 列表过滤
    return request
      .get<any[]>('/hotel/rooms/available')
      .then((rooms) =>
        rooms
          .filter((r) => r.status === 'AVAILABLE')
          .map((r) => ({
            ...r,
            roomType: params?.roomType ?? r.roomType,
            price: r.price
          }))
      )
      .catch(() =>
        fetchRooms().then((rooms) =>
          rooms
            .filter((r) => r.status === 'AVAILABLE')
            .map((r) => ({
              ...r,
              roomType: params?.roomType ?? r.roomType,
              price: r.price
            }))
        )
      );
  },

  // 获取入住记录
  getCheckInRecords() {
    // 后端未提供入住记录接口，使用房间列表占位
    return fetchRooms().then((rooms) =>
      rooms
        .filter((r) => r.status === 'OCCUPIED')
        .map(
          (r) =>
            ({
              roomId: String(r.id ?? r.roomId ?? r.room_id ?? ''),
              checkedOut: false,
              guestName: r.customerName ?? r.guestName ?? '住客',
              roomType: r.roomType ?? 'STANDARD'
            } as CheckInRecord)
        )
    );
  },

  // 获取详单记录
  getDetailRecords(roomId: string) {
    // 后端无对应 JSON 详单接口（仅 CSV 导出），返回空数组占位
    return Promise.resolve([] as DetailRecord[]);
  }
};

/**
 * 房间客户端接口
 */
export const roomApi = {
  // 获取房间状态
  getRoomState(roomId: string) {
    return request.get<RoomState>('/ac/state', { params: { roomId } });
  },

  // 开机 (后端不接受额外参数，只接受 roomId)
  turnOn(roomId: string) {
    return request.post('/ac/power', { roomId });
  },

  // 关机
  turnOff(roomId: string) {
    return request.post('/ac/power/off', { roomId });
  },

  // 发送请求（调温、调风）
  sendRequest(roomId: string, targetTemp: number, fanSpeed: FanSpeed, mode: ACMode) {
    // 分别调用后端温度/风速/模式接口
    return Promise.all([
      request.post('/ac/temp', { roomId, targetTemp }),
      request.post('/ac/speed', { roomId, fanSpeed }),
      request.post('/ac/mode', { roomId, mode })
    ]).then(() => undefined);
  },

  // 初始化房间参数
  initializeRoom(roomId: string, mode: ACMode, roomTemp: number, targetTemp: number, fanSpeed: FanSpeed) {
    // 后端无初始化接口，退化为设置模式/温度/风速
    return Promise.all([
      request.post('/ac/mode', { roomId, mode }),
      request.post('/ac/temp', { roomId, targetTemp }),
      request.post('/ac/speed', { roomId, fanSpeed })
    ]).then(() => this.getRoomState(roomId));
  }
};

/**
 * 管理员监控接口
 */
export const adminApi = {
  // 获取所有房间状态（从 room 接口获取）
  getAllRoomStates() {
    return request.get<RoomState[]>('/admin/rooms/status');
  },

  // 获取服务队列
  getServiceQueue() {
    return request.get<any>('/monitor/status').then((res) => res?.serving_queue || res?.servingQueue || []);
  },

  // 获取等待队列
  getWaitingQueue() {
    return request.get<any>('/monitor/status').then((res) => res?.waiting_queue || res?.waitingQueue || []);
  },

  // 一键关机
  turnOffAll() {
    // 后端未提供批量接口，留空实现
    return Promise.resolve();
  },

  // 一键开机
  turnOnAll() {
    return Promise.resolve();
  },

  // 清空等待队列
  clearWaitingQueue() {
    return Promise.resolve();
  }
};

/**
 * 经理统计接口
 */
export const managerApi = {
  // 获取统计报表（后端使用 POST 方法，传递时间戳毫秒）
  getStatistics(startTime: number, endTime: number) {
    // 后端提供 /report/daily 与 /report/weekly，这里返回周报为兼容
    const startDate = new Date(startTime).toISOString().slice(0, 10);
    return request.get<StatisticsReport>('/report/weekly', { params: { startDate } });
  },

  // 获取所有账单
  getAllBills() {
    // 后端无对应 JSON 账单接口，返回空数组占位
    return Promise.resolve([] as Bill[]);
  }
};

/**
 * 导出所有 API
 */
export default {
  frontDesk: frontDeskApi,
  room: roomApi,
  admin: adminApi,
  manager: managerApi
};

