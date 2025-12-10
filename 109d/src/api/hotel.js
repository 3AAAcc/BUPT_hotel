/**
 * 酒店管理 API
 */
import request from './request'

/**
 * 获取所有房间
 */
export function getAllRooms() {
  return request({
    url: '/hotel/rooms',
    method: 'get'
  })
}

/**
 * 获取可用房间ID列表
 */
export function getAvailableRoomIds() {
  return request({
    url: '/hotel/available',
    method: 'get'
  })
}

/**
 * 获取可用房间详情
 */
export function getAvailableRooms() {
  return request({
    url: '/hotel/rooms/available',
    method: 'get'
  })
}

/**
 * 办理入住
 */
export function checkIn(data) {
  return request({
    url: '/hotel/checkin',
    method: 'post',
    data
  })
}

/**
 * 办理退房
 */
export function checkOut(roomId) {
  return request({
    url: `/hotel/checkout/${roomId}`,
    method: 'post'
  })
}

