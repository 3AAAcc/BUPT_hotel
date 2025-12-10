/**
 * 轮询配置
 * 用于控制后端API轮询频率，优化网络请求
 */

export const POLLING_CONFIG = {
  // 有活跃房间时的轮询间隔（毫秒）
  ACTIVE_INTERVAL: 2000,

  // 无活跃房间时的轮询间隔（毫秒）
  IDLE_INTERVAL: 10000,

  // 页面隐藏时的轮询间隔（毫秒）
  HIDDEN_INTERVAL: 30000,

  // 是否启用智能轮询（根据房间状态动态调整）
  ENABLE_SMART_POLLING: true,

  // 是否启用页面可见性检测（页面隐藏时降低轮询频率）
  ENABLE_VISIBILITY_DETECTION: true
};

/**
 * 判断房间是否处于活跃状态
 * 活跃状态：开机 且（送风中 或 等待中）
 */
export function isRoomActive(room: { isOn: boolean; status: string }): boolean {
  return room.isOn && (room.status === 'SERVING' || room.status === 'WAITING');
}
