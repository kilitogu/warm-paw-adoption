import request from '@/utils/request'

/**
 * 注册请求
 */
export function registerApi(data) {
  return request({
    url: '/api/register',
    method: 'post',
    data
  })
}