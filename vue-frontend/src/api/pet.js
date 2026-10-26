import request from '@/utils/request'

/**
 * 宠物列表：分页 + 多条件筛选
 * @param {Object} params page/page_size/species/breed/gender/city/age_min/age_max/health_status/vaccinated/sterilized/keyword/sort_by
 */
export function getPetListApi(params) {
  return request({
    url: '/api/pet/list',
    method: 'get',
    params
  })
}

/** 宠物详情 */
export function getPetDetailApi(petId) {
  return request({
    url: `/api/pet/${petId}`,
    method: 'get'
  })
}

/** 首页精选宠物 */
export function getRecommendPetsApi(limit = 6) {
  return request({
    url: '/api/pet/recommend',
    method: 'get',
    params: { limit }
  })
}