import request from '@/utils/request'

/**
 * FAQ 列表
 * @param {Object} params { category }
 */
export function getGuideFaqApi(params) {
  return request({
    url: '/api/guide/faq',
    method: 'get',
    params
  })
}

/** 按分类聚合的 FAQ */
export function getGuideFaqGroupsApi() {
  return request({
    url: '/api/guide/faq/groups',
    method: 'get'
  })
}