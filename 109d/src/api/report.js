/**
 * 报表 API
 */
import request from './request'

/**
 * 获取房间报表
 */
export function getRoomReport(roomId) {
  return request({
    url: '/report/room',
    method: 'get',
    params: { roomId }
  })
}

/**
 * 获取日报表
 */
export function getDailyReport(date) {
  return request({
    url: '/report/daily',
    method: 'get',
    params: { date }
  })
}

/**
 * 获取周报表
 */
export function getWeeklyReport(startDate) {
  return request({
    url: '/report/weekly',
    method: 'get',
    params: { startDate }
  })
}

