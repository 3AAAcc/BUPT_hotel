/**
 * 空调控制 API
 */
import request from './request'

/**
 * 获取空调状态
 */
export function getACState(roomId) {
  return request({
    url: '/ac/state',
    method: 'get',
    params: { roomId }
  })
}

/**
 * 开启空调
 */
export function powerOn(roomId) {
  return request({
    url: '/ac/power',
    method: 'post',
    data: { roomId }
  })
}

/**
 * 关闭空调
 */
export function powerOff(roomId) {
  return request({
    url: '/ac/power/off',
    method: 'post',
    data: { roomId }
  })
}

/**
 * 改变温度
 */
export function changeTemp(roomId, targetTemp) {
  return request({
    url: '/ac/temp',
    method: 'post',
    data: { roomId, targetTemp }
  })
}

/**
 * 改变风速
 */
export function changeSpeed(roomId, fanSpeed) {
  return request({
    url: '/ac/speed',
    method: 'post',
    data: { roomId, fanSpeed }
  })
}

/**
 * 切换模式
 */
export function changeMode(roomId, mode) {
  return request({
    url: '/ac/mode',
    method: 'post',
    data: { roomId, mode }
  })
}

