<template>
  <div class="pet-list-page">
    <!-- 页头 -->
    <div class="page-head">
      <div>
        <h1>寻找你的毛孩子</h1>
        <p>共 {{ pagination.total }} 只宠物等待领养，支持按品种、城市、年龄筛选</p>
      </div>
      <el-button :icon="Refresh" text @click="reset">重置全部条件</el-button>
    </div>

    <div class="page-body">
      <!-- 左侧筛选栏 -->
      <aside class="filter-panel">
        <div class="filter-head">
          <span>筛选条件</span>
          <el-button link type="primary" @click="reset">清空</el-button>
        </div>

        <div class="filter-group">
          <label class="filter-label">物种</label>
          <el-radio-group v-model="filters.species" size="small" @change="handleSpeciesChange">
            <el-radio-button label="">全部</el-radio-button>
            <el-radio-button label="猫">猫</el-radio-button>
            <el-radio-button label="狗">狗</el-radio-button>
            <el-radio-button label="其他">其他</el-radio-button>
          </el-radio-group>
        </div>

        <div class="filter-group">
          <label class="filter-label">品种</label>
          <el-select v-model="filters.breed" placeholder="不限品种" clearable class="w-full">
            <el-option v-for="item in breedOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </div>

        <div class="filter-group">
          <label class="filter-label">性别</label>
          <el-select v-model="filters.gender" placeholder="不限性别" clearable class="w-full">
            <el-option label="公" value="公" />
            <el-option label="母" value="母" />
          </el-select>
        </div>

        <div class="filter-group">
          <label class="filter-label">城市</label>
          <el-select v-model="filters.city" placeholder="不限城市" clearable class="w-full">
            <el-option v-for="city in CITIES" :key="city" :label="city" :value="city" />
          </el-select>
        </div>

        <div class="filter-group">
          <label class="filter-label">
            年龄
            <span class="age-text">{{ ageText }}</span>
          </label>
          <el-slider
            v-model="filters.ageRange"
            range
            :min="0"
            :max="120"
            :step="1"
            :marks="{ 0: '0', 24: '2岁', 60: '5岁', 120: '10岁+' }"
          />
        </div>

        <div class="filter-group">
          <label class="filter-label">健康状况</label>
          <el-select v-model="filters.health_status" placeholder="不限" clearable class="w-full">
            <el-option label="健康" value="健康" />
            <el-option label="亚健康" value="亚健康" />
            <el-option label="需治疗" value="需治疗" />
          </el-select>
        </div>

        <div class="filter-group">
          <label class="filter-label">疫苗</label>
          <el-select v-model="filters.vaccinated" placeholder="不限" clearable class="w-full">
            <el-option label="已接种" :value="true" />
            <el-option label="未接种" :value="false" />
          </el-select>
        </div>

        <div class="filter-group">
          <label class="filter-label">绝育</label>
          <el-select v-model="filters.sterilized" placeholder="不限" clearable class="w-full">
            <el-option label="已绝育" :value="true" />
            <el-option label="未绝育" :value="false" />
          </el-select>
        </div>

        <div class="filter-group">
          <label class="filter-label">关键词</label>
          <el-input
            v-model="filters.keyword"
            placeholder="昵称 / 品种 / 描述"
            clearable
            :prefix-icon="Search"
            @keyup.enter="search"
          />
        </div>

        <el-button type="primary" class="search-btn" :loading="loading" @click="search">
          筛选
        </el-button>
      </aside>

      <!-- 右侧列表 -->
      <section class="list-panel">
        <div class="sort-bar">
          <div class="sort-group">
            <span class="sort-label">排序</span>
            <el-radio-group
              :model-value="filters.sort_by"
              size="small"
              @change="changeSort"
            >
              <el-radio-button label="latest">最新</el-radio-button>
              <el-radio-button label="hot">最热</el-radio-button>
              <el-radio-button label="age">年龄</el-radio-button>
            </el-radio-group>
          </div>
          <span class="result-count">共 {{ pagination.total }} 只</span>
        </div>

        <!-- 加载骨架 -->
        <div v-if="loading" class="pet-grid">
          <div v-for="n in 8" :key="n" class="skeleton-card">
            <el-skeleton animated>
              <template #template>
                <el-skeleton-item variant="image" class="skeleton-cover" />
                <div class="skeleton-body">
                  <el-skeleton-item variant="h3" style="width: 45%" />
                  <el-skeleton-item variant="text" style="width: 85%; margin-top: 10px" />
                  <el-skeleton-item variant="text" style="width: 60%; margin-top: 8px" />
                </div>
              </template>
            </el-skeleton>
          </div>
        </div>

        <!-- 错误态 -->
        <el-result
          v-else-if="error"
          icon="error"
          title="加载失败"
          :sub-title="error"
          class="state-block"
        >
          <template #extra>
            <el-button type="primary" @click="loadPets">重新加载</el-button>
          </template>
        </el-result>

        <!-- 空态 -->
        <el-empty v-else-if="!list.length" description="没有符合条件的宠物" class="state-block">
          <el-button type="primary" plain @click="reset">清空筛选条件</el-button>
        </el-empty>

        <!-- 卡片网格 -->
        <div v-else class="pet-grid">
          <PetCard v-for="pet in list" :key="pet.id" :pet="pet" />
        </div>

        <!-- 分页 -->
        <div v-if="!loading && !error && pagination.total > pagination.page_size" class="pager">
          <el-pagination
            background
            layout="prev, pager, next, jumper, total"
            :total="pagination.total"
            :page-size="pagination.page_size"
            :current-page="pagination.page"
            @current-change="changePage"
          />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { Refresh, Search } from '@element-plus/icons-vue'

import PetCard from '@/components/PetCard.vue'
import { usePetList } from '@/hooks/usePetList'

// 城市与品种选项，后续可替换为字典接口
const CITIES = ['杭州', '上海', '北京', '成都', '广州', '南京', '深圳', '武汉']

const BREED_MAP = {
  猫: ['布偶猫', '英国短毛猫', '美国短毛猫', '橘猫', '狸花猫', '暹罗猫', '中华田园猫'],
  狗: ['柯基', '金毛寻回犬', '比熊犬', '边境牧羊犬', '萨摩耶', '柴犬', '拉布拉多', '泰迪']
}

const {
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
} = usePetList()

// 品种选项跟随物种联动
const breedOptions = computed(() => {
  if (filters.species && BREED_MAP[filters.species]) {
    return BREED_MAP[filters.species]
  }
  return [...BREED_MAP['猫'], ...BREED_MAP['狗']]
})

// 月龄区间的可读文案
const ageText = computed(() => {
  const [min, max] = filters.ageRange || [0, 120]
  const format = (months) => {
    if (months < 12) return `${months}个月`
    const year = Math.floor(months / 12)
    const rest = months % 12
    return rest ? `${year}岁${rest}个月` : `${year}岁`
  }
  if (min === 0 && max >= 120) return '不限'
  return `${format(min)} - ${max >= 120 ? '不限' : format(max)}`
})

// 切换物种时清空已选品种
const handleSpeciesChange = () => {
  filters.breed = ''
  search()
}

onMounted(() => {
  loadPets()
})
</script>

<style scoped>
.pet-list-page {
  max-width: 1180px;
  margin: 0 auto;
}

.page-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.page-head h1 {
  margin: 0 0 6px;
  font-size: 24px;
  color: var(--text-main, #1f2937);
}

.page-head p {
  margin: 0;
  font-size: 13px;
  color: var(--text-sub, #8892a0);
}

.page-body {
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  gap: 18px;
  align-items: start;
}

/* 筛选栏 */
.filter-panel {
  position: sticky;
  top: 0;
  padding: 18px;
  border-radius: var(--radius-lg, 12px);
  background: var(--bg-card, #ffffff);
  border: 1px solid var(--border, #eaedf3);
}

.filter-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 12px;
  margin-bottom: 4px;
  border-bottom: 1px solid var(--border, #eaedf3);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main, #1f2937);
}

.filter-group {
  padding: 12px 0;
  border-bottom: 1px dashed var(--border, #eaedf3);
}

.filter-group:last-of-type {
  border-bottom: none;
}

.filter-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
  color: var(--text-body, #4b5563);
}

.age-text {
  color: var(--brand, #ff7a59);
  font-size: 11px;
}

.w-full {
  width: 100%;
}

.search-btn {
  width: 100%;
  margin-top: 14px;
  border: none;
  border-radius: var(--radius-md, 10px);
  background: linear-gradient(135deg, #ff9a6c, #ff6b4a);
}

/* 右侧列表 */
.sort-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  margin-bottom: 14px;
  border-radius: var(--radius-md, 10px);
  background: var(--bg-card, #ffffff);
  border: 1px solid var(--border, #eaedf3);
}

.sort-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sort-label,
.result-count {
  font-size: 12px;
  color: var(--text-sub, #8892a0);
}

.pet-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.skeleton-card {
  overflow: hidden;
  border-radius: var(--radius-lg, 12px);
  background: var(--bg-card, #ffffff);
  border: 1px solid var(--border, #eaedf3);
}

.skeleton-cover {
  width: 100%;
  height: 160px;
}

.skeleton-body {
  padding: 14px 16px 18px;
}

.state-block {
  padding: 40px 0;
  border-radius: var(--radius-lg, 12px);
  background: var(--bg-card, #ffffff);
  border: 1px dashed var(--border, #eaedf3);
}

.pager {
  display: flex;
  justify-content: center;
  padding: 22px 0 6px;
}

@media (max-width: 992px) {
  .page-body {
    grid-template-columns: 1fr;
  }

  .filter-panel {
    position: static;
  }

  .pet-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .pet-grid {
    grid-template-columns: 1fr;
  }

  .page-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>