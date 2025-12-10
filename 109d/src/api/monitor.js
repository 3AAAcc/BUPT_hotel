/**
 * 监控 API
 */
import request from './request'

/**
 * 获取监控状态
 */
export function getMonitorStatus() {
  return request({
    url: '/monitor/status',
    method: 'get'
  })
}

