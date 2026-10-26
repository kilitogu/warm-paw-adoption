import { reactive, ref } from 'vue'
import { getPetListApi } from '@/api/pet'

/** 筛选条件默认值 */
const DEFAULT_FILTERS = {
  species: '',
  breed: '',
  gender: '',
  city: '',
  ageRange: [0, 120],
  health_status: '',
  vaccinated: null,
  sterilized: null,
  keyword: '',
  sort_by: 'latest'
}

/**
 * 宠物列表状态管理
 * 统一处理筛选条件、分页、加载态、错误态和请求竞态
 */
export function usePetList() {
  const filters = reactive({ ...DEFAULT_FILTERS, ageRange: [0, 120] })
  const pagination = reactive({ page: 1, page_size: 12, total: 0 })
  const list = ref([])
  const loading = ref(false)
  const error = ref('')

  // 请求序号：快速切换筛选时只接受最后一次请求的结果
  let requestSeq = 0

  const buildParams = () => {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      sort_by: filters.sort_by
    }

    if (filters.species) params.species = filters.species
    if (filters.breed) params.breed = filters.breed
    if (filters.gender) params.gender = filters.gender
    if (filters.city) params.city = filters.city
    if (filters.health_status) params.health_status = filters.health_status
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.vaccinated !== null) params.vaccinated = filters.vaccinated
    if (filters.sterilized !== null) params.sterilized = filters.sterilized

    const [ageMin, ageMax] = filters.ageRange || [0, 120]
    if (ageMin > 0) params.age_min = ageMin
    if (ageMax < 120) params.age_max = ageMax

    return params
  }

  const loadPets = async () => {
    const seq = ++requestSeq
    loading.value = true
    error.value = ''

    try {
      const res = await getPetListApi(buildParams())

      // 已有更新的请求发出，丢弃本次结果
      if (seq !== requestSeq) return

      if (res.code === 200) {
        list.value = res.data?.items || []
        pagination.total = res.data?.total || 0
      } else {
        error.value = res.message || '宠物列表加载失败'
      }
    } catch (err) {
      if (seq !== requestSeq) return
      console.error('宠物列表请求失败:', err)
      error.value = '网络异常，请检查后端服务后重试'
    } finally {
      if (seq === requestSeq) {
        loading.value = false
      }
    }
  }

  /** 点击"筛选"：回到第一页重新查询 */
  const search = () => {
    pagination.page = 1
    loadPets()
  }

  /** 重置筛选条件 */
  const reset = () => {
    Object.assign(filters, { ...DEFAULT_FILTERS, ageRange: [0, 120] })
    pagination.page = 1
    loadPets()
  }

  /** 切换排序 */
  const changeSort = (sort) => {
    filters.sort_by = sort
    pagination.page = 1
    loadPets()
  }

  /** 翻页 */
  const changePage = (page) => {
    pagination.page = page
    loadPets()
  }

  return {
    filters,
    pagination,
    list,
    loading,
    error,
    loadPets,
    search,
    reset,
    changeSort,
    changePage
  }
}