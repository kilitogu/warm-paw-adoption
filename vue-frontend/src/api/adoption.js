import request from '@/utils/request'

/** 提交领养申请 */
export function applyAdoptionApi(data) {
  return request({
    url: '/api/adoption/apply',
    method: 'post',
    data
  })
}

/** 收藏 / 取消收藏 */
export function toggleFavoriteApi(data) {
  return request({
    url: '/api/adoption/favorite',
    method: 'post',
    data
  })
}

/** 查询某只宠物的收藏状态 */
export function getFavoriteStatusApi(petId) {
  return request({
    url: `/api/adoption/favorite/status/${petId}`,
    method: 'get'
  })
}

/** 我的收藏列表 */
export function getFavoriteListApi(params) {
  return request({
    url: '/api/adoption/favorite/list',
    method: 'get',
    params
  })
}

/** 我的领养申请 */
export function getMyApplicationsApi() {
  return request({
    url: '/api/adoption/apply/my',
    method: 'get'
  })
}