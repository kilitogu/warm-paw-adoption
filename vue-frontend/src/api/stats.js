import request from '@/utils/request'

/** 首页数据看板 */
export function getOverviewApi() {
  return request({
    url: '/api/stats/overview',
    method: 'get'
  })
}