import request from '../utils/request'

// 获取操作日志列表
export function getLogs(params) {
  return request({
    url: '/api/logs/',
    method: 'get',
    params
  })
}

// 获取操作日志统计信息
export function getLogStats() {
  return request({
    url: '/api/logs/stats',
    method: 'get'
  })
}

// 导出日志
export function exportLogs(params) {
  return request({
    url: '/api/logs/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
} 