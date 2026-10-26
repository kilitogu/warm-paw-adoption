<template>
  <div class="my-page">
    <section class="my-card">
      <el-tabs v-model="activeTab" class="my-tabs" @tab-change="handleTabChange">
        <!-- 我的申请 -->
        <el-tab-pane label="我的申请" name="apply">
          <div v-if="applyLoading" class="state-block">
            <el-skeleton :rows="4" animated />
          </div>

          <el-empty
            v-else-if="!applications.length"
            description="还没有提交过领养申请"
            class="state-block"
          >
            <router-link to="/manager/pets">
              <el-button type="primary" plain>去看看毛孩子</el-button>
            </router-link>
          </el-empty>

          <div v-else class="apply-list">
            <article v-for="item in applications" :key="item.id" class="apply-item">
              <div class="apply-head">
                <div class="apply-title">
                  <h3>{{ item.pet_name || `宠物 #${item.pet_id}` }}</h3>
                  <el-tag :type="statusType(item.status)" effect="light" size="small">
                    {{ item.status }}
                  </el-tag>
                </div>
                <span class="apply-time">{{ formatTime(item.create_time) }}</span>
              </div>

              <p class="apply-reason">{{ item.reason }}</p>

              <div class="apply-foot">
                <span class="apply-no">申请单号 #{{ item.id }}</span>
                <router-link :to="`/manager/pet/detail/${item.pet_id}`">
                  <el-button size="small" text type="primary">查看宠物</el-button>
                </router-link>
              </div>
            </article>
          </div>
        </el-tab-pane>

        <!-- 我的收藏 -->
        <el-tab-pane label="我的收藏" name="favorite">
          <div v-if="favoriteLoading" class="state-block">
            <el-skeleton :rows="4" animated />
          </div>

          <el-empty
            v-else-if="!favorites.length"
            description="还没有收藏任何宠物"
            class="state-block"
          >
            <router-link to="/manager/pets">
              <el-button type="primary" plain>去挑一只</el-button>
            </router-link>
          </el-empty>

          <div v-else class="favorite-grid">
            <PetCard v-for="pet in favorites" :key="pet.id" :pet="pet" />
          </div>
        </el-tab-pane>
      </el-tabs>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

import PetCard from '@/components/PetCard.vue'
import { getFavoriteListApi, getMyApplicationsApi } from '@/api/adoption'

const route = useRoute()

const activeTab = ref(route.meta.tab === 'favorite' ? 'favorite' : 'apply')
const applications = ref([])
const favorites = ref([])
const applyLoading = ref(false)
const favoriteLoading = ref(false)

const statusType = (status) => {
  if (status === '通过') return 'success'
  if (status === '拒绝') return 'danger'
  return 'warning'
}

const formatTime = (value) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const pad = (num) => String(num).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(
    date.getHours()
  )}:${pad(date.getMinutes())}`
}

const loadApplications = async () => {
  applyLoading.value = true
  try {
    const res = await getMyApplicationsApi()
    if (res.code === 200) {
      applications.value = res.data || []
    } else {
      ElMessage.error(res.message || '申请记录加载失败')
    }
  } catch (error) {
    console.error('申请记录加载失败:', error)
    ElMessage.error('申请记录加载失败，请稍后重试')
  } finally {
    applyLoading.value = false
  }
}

const loadFavorites = async () => {
  favoriteLoading.value = true
  try {
    const res = await getFavoriteListApi({ page: 1, page_size: 24 })
    if (res.code === 200) {
      favorites.value = res.data?.items || []
    } else {
      ElMessage.error(res.message || '收藏加载失败')
    }
  } catch (error) {
    console.error('收藏加载失败:', error)
    ElMessage.error('收藏加载失败，请稍后重试')
  } finally {
    favoriteLoading.value = false
  }
}

const handleTabChange = (name) => {
  if (name === 'favorite' && !favorites.value.length) loadFavorites()
}

watch(
  () => route.meta.tab,
  (tab) => {
    activeTab.value = tab === 'favorite' ? 'favorite' : 'apply'
    handleTabChange(activeTab.value)
  }
)

onMounted(() => {
  loadApplications()
  if (activeTab.value === 'favorite') loadFavorites()
})
</script>

<style scoped>
.my-page {
  max-width: 1000px;
  margin: 0 auto;
}

.my-card {
  padding: 8px 24px 24px;
  border-radius: 16px;
  border: 1px solid var(--border, #eaedf3);
  background: #ffffff;
}

.state-block {
  padding: 32px 0;
}

.apply-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.apply-item {
  padding: 16px 18px;
  border-radius: 12px;
  border: 1px solid #f0f2f7;
  background: #fcfdff;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.apply-item:hover {
  border-color: #ffd2c4;
  box-shadow: 0 6px 18px rgba(239, 91, 58, 0.08);
}

.apply-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.apply-title {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.apply-title h3 {
  margin: 0;
  font-size: 15px;
  color: var(--text-main, #1f2937);
}

.apply-time {
  flex: none;
  font-size: 12px;
  color: var(--text-sub, #8892a0);
}

.apply-reason {
  margin: 10px 0 12px;
  font-size: 13px;
  line-height: 1.8;
  color: var(--text-body, #4b5563);
}

.apply-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.apply-no {
  font-size: 11px;
  color: var(--text-muted, #b3bbc8);
}

.favorite-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 16px;
}

@media (max-width: 560px) {
  .my-card {
    padding: 4px 14px 18px;
  }

  .apply-head {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>
