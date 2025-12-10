/**
 * API 适配器 - 后端 API 服务
 */
import api from '../api/hvac';
import type {
  RoomState,
  DetailRecord,
  Bill,
  CheckInRecord,
  StatisticsReport,
  ServiceObject,
  WaitingObject
} from '../types';
import { ACMode, FanSpeed } from '../types';

/**
 * HVAC服务接口定义
 */
export interface IHvacService {
  // 前台接口
  checkIn(roomId: string, mode: ACMode, guestName?: string, guestPhone?: string, idCard?: string, stayDays?: number, roomType?: string, roomTemp?: number, targetTemp?: number, fanSpeed?: FanSpeed): Promise<{ success: boolean; message: string }>;
  checkOut(roomId: string): Promise<Bill>;
  getDetailRecords(roomId: string): Promise<DetailRecord[]>;
  getBill(roomId: string): Promise<Bill | null>;
  getBillHistory(): Promise<Bill[]>;
  getCheckInRecords(): Promise<CheckInRecord[]>;
  getCheckInRecord(roomId: string): CheckInRecord | null;
  getOccupiedRooms(): string[];

  // 房间接口
  getRoomState(roomId: string): RoomState | null;
  getAllRoomStates(): RoomState[];
  turnOn(roomId: string): Promise<void>;
  turnOff(roomId: string): Promise<void>;
  sendRequest(roomId: string, targetTemp: number, fanSpeed: FanSpeed, mode: ACMode): Promise<void>;
  setMode(roomId: string, mode: ACMode): Promise<void>;

  // 管理员接口
  getServiceQueue(): ServiceObject[];
  getWaitingQueue(): WaitingObject[];
  turnOffAll(): Promise<void>;
  turnOnAll(): Promise<void>;
  clearWaitingQueue(): Promise<void>;

  // 经理接口
  generateStatistics(startTime: number, endTime: number, roomId?: string): Promise<StatisticsReport>;

  // 系统方法
  refreshRoomStates(): Promise<void>;      // 刷新房间状态
  refreshQueues(): Promise<void>;          // 刷新队列
  refreshCheckInRecords(): Promise<void>;  // 刷新入住记录
  refreshBillHistory(): Promise<void>;     // 刷新历史账单
  onStateChange(callback: () => void): void;
  destroy(): void;
}

/**
 * 后端API适配器
 */
class HvacService implements IHvacService {
  // 缓存数据
  private roomStatesCache: Map<string, RoomState> = new Map();
  private serviceQueueCache: ServiceObject[] = [];
  private waitingQueueCache: WaitingObject[] = [];
  private checkInRecordsCache: Map<string, CheckInRecord> = new Map();
  private billHistoryCache: Bill[] = [];
  private stateChangeCallbacks: Set<() => void> = new Set();

  constructor() {
    // 初始化时加载基础数据
    this.refreshRoomStates();
    this.refreshCheckInRecords();
    this.refreshBillHistory();
    this.refreshQueues();
  }

  // ==================== 刷新方法 ====================

  async refreshRoomStates(): Promise<void> {
    try {
      const rooms = await api.admin.getAllRoomStates();
      this.roomStatesCache.clear();
      rooms.forEach((room) => {
        this.roomStatesCache.set(room.roomId, room);
      });
      this.stateChangeCallbacks.forEach(callback => callback());
    } catch (error) {
      console.error('刷新房间状态失败:', error);
    }
  }

  async refreshQueues(): Promise<void> {
    try {
      const [serviceQueue, waitingQueue] = await Promise.all([
        api.admin.getServiceQueue(),
        api.admin.getWaitingQueue()
      ]);
      this.serviceQueueCache = serviceQueue;
      this.waitingQueueCache = waitingQueue;
      this.stateChangeCallbacks.forEach(callback => callback());
    } catch (error) {
      console.error('刷新队列失败:', error);
    }
  }

  async refreshCheckInRecords(): Promise<void> {
    try {
      const checkInRecords = await api.frontDesk.getCheckInRecords();
      this.checkInRecordsCache.clear();

      // 只缓存未退房的记录
      checkInRecords
        .filter(record => !record.checkedOut)
        .forEach((record) => {
          this.checkInRecordsCache.set(record.roomId, record);
        });

      this.stateChangeCallbacks.forEach(callback => callback());
    } catch (error) {
      console.error('刷新入住记录失败:', error);
    }
  }

  async refreshBillHistory(): Promise<void> {
    try {
      const bills = await api.frontDesk.getAllBills();
      this.billHistoryCache = bills;
      this.stateChangeCallbacks.forEach(callback => callback());
    } catch (error) {
      console.error('刷新历史账单失败:', error);
    }
  }

  // ==================== 前台接口 ====================

  async checkIn(roomId: string, mode: ACMode, guestName?: string, guestPhone?: string, idCard?: string, stayDays?: number, roomType?: string, roomTemp?: number, targetTemp?: number, fanSpeed?: FanSpeed): Promise<{ success: boolean; message: string }> {
    try {
      await api.frontDesk.checkIn(
        roomId,
        guestName || '未提供',
        guestPhone || '00000000000',
        idCard || '000000000000000000',
        stayDays || 1,
        roomType || 'STANDARD',
        mode,
        roomTemp ?? 25,
        targetTemp ?? 25,
        fanSpeed || FanSpeed.MEDIUM
      );
      return { success: true, message: `房间 ${roomId} 入住办理成功` };
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } }; message?: string };
      return { success: false, message: err.response?.data?.message || err.message || '入住失败' };
    }
  }

  async checkOut(roomId: string): Promise<Bill> {
    const bill = await api.frontDesk.checkOut(roomId);
    // 退房成功后，刷新历史账单列表
    await this.refreshBillHistory();
    return bill;
  }

  async getDetailRecords(roomId: string): Promise<DetailRecord[]> {
    return await api.frontDesk.getDetailRecords(roomId);
  }

  async getBill(roomId: string): Promise<Bill | null> {
    try {
      return await api.frontDesk.getBill(roomId);
    } catch {
      return null;
    }
  }

  async getBillHistory(): Promise<Bill[]> {
    // 如果缓存为空，先刷新一次
    if (this.billHistoryCache.length === 0) {
      await this.refreshBillHistory();
    }
    return this.billHistoryCache;
  }

  async getCheckInRecords(): Promise<CheckInRecord[]> {
    return Array.from(this.checkInRecordsCache.values());
  }

  getCheckInRecord(roomId: string): CheckInRecord | null {
    return this.checkInRecordsCache.get(roomId) || null;
  }

  getOccupiedRooms(): string[] {
    return Array.from(this.checkInRecordsCache.keys());
  }

  // ==================== 房间接口 ====================

  getRoomState(roomId: string): RoomState | null {
    return this.roomStatesCache.get(roomId) || null;
  }

  getAllRoomStates(): RoomState[] {
    return Array.from(this.roomStatesCache.values());
  }

  async turnOn(roomId: string): Promise<void> {
    try {
      await api.room.turnOn(roomId);
      await this.refreshRoomStates();

      const room = this.roomStatesCache.get(roomId);
      if (room) {
        await api.room.sendRequest(roomId, room.targetTemp, room.fanSpeed, room.mode);
        await this.refreshRoomStates();
        // 开机后立即刷新队列，确保队列状态更新
        await this.refreshQueues();
      }
    } catch (error) {
      console.error('开机失败:', error);
      throw error;
    }
  }

  async turnOff(roomId: string): Promise<void> {
    try {
      await api.room.turnOff(roomId);
      await this.refreshRoomStates();
      // 关机后立即刷新队列，确保队列状态更新
      await this.refreshQueues();
    } catch (error) {
      console.error('关机失败:', error);
      throw error;
    }
  }

  async sendRequest(roomId: string, targetTemp: number, fanSpeed: FanSpeed, mode: ACMode): Promise<void> {
    try {
      await api.room.sendRequest(roomId, targetTemp, fanSpeed, mode);
      await this.refreshRoomStates();
      // 发送请求后立即刷新队列，确保队列状态更新
      await this.refreshQueues();
    } catch (error) {
      console.error('发送服务请求失败:', error);
      throw error;
    }
  }

  async setMode(roomId: string, mode: ACMode): Promise<void> {
    try {
      const room = this.roomStatesCache.get(roomId);
      if (room) {
        room.mode = mode;
        this.stateChangeCallbacks.forEach(callback => callback());
      }
    } catch (error) {
      console.error('切换模式失败:', error);
      throw error;
    }
  }

  // ==================== 管理员接口 ====================

  getServiceQueue(): ServiceObject[] {
    return this.serviceQueueCache;
  }

  getWaitingQueue(): WaitingObject[] {
    return this.waitingQueueCache;
  }

  async turnOffAll(): Promise<void> {
    try {
      await api.admin.turnOffAll();
      await this.refreshRoomStates();
      await this.refreshQueues();
    } catch (error) {
      console.error('一键关机失败:', error);
      throw error;
    }
  }

  async turnOnAll(): Promise<void> {
    try {
      await api.admin.turnOnAll();
      await this.refreshRoomStates();
      await this.refreshQueues();
    } catch (error) {
      console.error('一键开机失败:', error);
      throw error;
    }
  }

  async clearWaitingQueue(): Promise<void> {
    try {
      await api.admin.clearWaitingQueue();
      await this.refreshQueues();
    } catch (error) {
      console.error('清空等待队列失败:', error);
      throw error;
    }
  }

  // ==================== 经理接口 ====================

  async generateStatistics(startTime: number, endTime: number, _roomId?: string): Promise<StatisticsReport> {
    // 直接传递时间戳（毫秒），后端 StatisticsQueryDTO 期望 Long 类型
    // 注意：后端当前不支持按房间筛选，_roomId 参数暂时忽略

    try {
      const result = await api.manager.getStatistics(startTime, endTime);
      return result;
    } catch (error) {
      console.error('生成报表失败:', error);
      throw error;
    }
  }

  // ==================== 系统方法 ====================

  onStateChange(callback: () => void): void {
    this.stateChangeCallbacks.add(callback);
  }

  destroy(): void {
    this.stateChangeCallbacks.clear();
  }
}

/**
 * 创建HVAC服务实例
 */
export function createHvacService(): IHvacService {
  return new HvacService();
}

export default HvacService;
