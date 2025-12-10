/**
 * 管理员 API
 */
import request from './request'

/**
 * 获取所有房间状态
 */
export function getAllRoomsStatus() {
  return request({
    url: '/admin/rooms/status',
    method: 'get'
  })
}

/**
 * 管理员控制开关
 */
export function adminControlPower(roomId, action) {
  return request({
    url: '/admin/control/power',
    method: 'post',
    data: { roomId, action }
  })
}

/**
 * 管理员控制温度
 */
export function adminControlTemp(roomId, targetTemp) {
  return request({
    url: '/admin/control/temp',
    method: 'post',
    data: { roomId, targetTemp }
  })
}

/**
 * 管理员控制风速
 */
export function adminControlSpeed(roomId, fanSpeed) {
  return request({
    url: '/admin/control/speed',
    method: 'post',
    data: { roomId, fanSpeed }
  })
}

/**
 * 管理员控制模式
 */
export function adminControlMode(roomId, mode) {
  return request({
    url: '/admin/control/mode',
    method: 'post',
    data: { roomId, mode }
  })
}

/**
 * 重置数据库
 */
export function resetDatabase() {
  return request({
    url: '/admin/reset-database',
    method: 'post'
  })
}

