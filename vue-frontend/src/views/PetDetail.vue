<template>
  <div class="pet-detail-page">
    <!-- 面包屑 -->
    <el-breadcrumb separator="/" class="crumb">
      <el-breadcrumb-item :to="{ path: '/manager/home' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item :to="{ path: '/manager/pets' }">宠物列表</el-breadcrumb-item>
      <el-breadcrumb-item>{{ pet?.name || '宠物详情' }}</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 加载态 -->
    <div v-if="loading" class="detail-card">
      <el-skeleton animated :rows="8" />
    </div>

    <!-- 错误态 -->
    <el-result
      v-else-if="error"
      icon="error"
      title="无法加载宠物信息"
      :sub-title="error"
      class="detail-card"
    >
      <template #extra>
        <el-button type="primary" @click="loadDetail">重新加载</el-button>
        <el-button @click="router.push('/manager/pets')">返回列表</el-button>
      </template>
    </el-result>

    <!-- 详情内容 -->
    <div v-else-if="pet" class="detail-layout">
      <!-- 左侧相册 -->
      <div class="gallery-card">
        <el-carousel
          v-if="galleryImages.length"
          height="420px"
          :interval="5000"
          indicator-position="outside"
          class="gallery"
        >
          <el-carousel-item v-for="(img, index) in galleryImages" :key="index">
            <img :src="img" :alt="`${pet.name} 的照片${index + 1}`" class="gallery-img" />
          </el-carousel-item>
        </el-carousel>

        <div v-else class="gallery-fallback">
          {{ speciesEmoji }}
        </div>

        <div class="gallery-footer">
          <span class="gallery-count">
            {{ galleryImages.length ? `共 ${galleryImages.length} 张照片` : '暂无照片' }}
          </span>
          <span class="view-count">👀 {{ pet.view_count }} 次浏览</span>
        </div>
      </div>

      <!-- 右侧信息 -->
      <div class="info-card">
        <div class="title-row">
          <div>
            <h1>{{ pet.name }}</h1>
            <p class="sub-title">
              {{ pet.breed || '未知品种' }} · {{ pet.age_text }} · {{ pet.city || '城市待确认' }}
            </p>
          </div>
          <el-tag :type="statusTagType" effect="light" round size="large">
            {{ pet.status }}
          </el-tag>
        </div>

        <div class="quick-tags">
          <span class="quick-tag">{{ pet.gender === '公' ? '♂ 公' : '♀ 母' }}</span>
          <span class="quick-tag">{{ pet.species }}</span>
          <span class="quick-tag" :class="pet.health_status === '健康' ? 'is-healthy' : 'is-warning'">
            {{ pet.health_status }}
          </span>
          <span class="quick-tag">{{ pet.vaccinated ? '已接种疫苗' : '未接种疫苗' }}</span>
          <span class="quick-tag">{{ pet.sterilized ? '已绝育' : '未绝育' }}</span>
        </div>

        <el-divider />

        <h2 class="section-title">关于 {{ pet.name }}</h2>
        <p class="description">{{ pet.description || '暂无更多介绍，欢迎联系志愿者了解。' }}</p>

        <el-descriptions :column="2" border class="info-table">
          <el-descriptions-item label="宠物编号">{{ pet.id }}</el-descriptions-item>
          <el-descriptions-item label="所在城市">{{ pet.city || '待确认' }}</el-descriptions-item>
          <el-descriptions-item label="月龄">{{ pet.age_text }}</el-descriptions-item>
          <el-descriptions-item label="健康状况">{{ pet.health_status }}</el-descriptions-item>
          <el-descriptions-item label="疫苗情况">
            {{ pet.vaccinated ? '已接种' : '未接种' }}
          </el-descriptions-item>
          <el-descriptions-item label="绝育情况">
            {{ pet.sterilized ? '已绝育' : '未绝育' }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="action-bar">
          <el-button
            type="primary"
            size="large"
            class="apply-btn"
            :disabled="pet.status !== '可领养' || applied"
            :loading="applying"
            @click="openApplyDialog"
          >
            {{ applied ? '申请已提交' : pet.status === '可领养' ? '申请领养' : '暂不可申请' }}
          </el-button>

          <el-button
            size="large"
            :type="isFavorited ? 'danger' : 'default'"
            :plain="isFavorited"
            :icon="isFavorited ? StarFilled : Star"
            :loading="favoriteLoading"
            @click="handleToggleFavorite"
          >
            {{ isFavorited ? '已收藏' : '收藏' }}
            <span v-if="favoriteCount" class="fav-count">{{ favoriteCount }}</span>
          </el-button>

          <el-button size="large" text @click="router.push('/manager/pets')">返回列表</el-button>
        </div>

        <el-alert
          type="warning"
          :closable="false"
          show-icon
          class="notice"
          title="领养前请确认"
          description="领养不是一时冲动。请确认家庭成员同意、居住环境允许养宠，并能承担未来十余年的陪伴与医疗费用。"
        />
      </div>
    </div>

    <!-- 申请弹窗 -->
    <el-dialog
      v-model="applyVisible"
      title="填写领养申请"
      width="520px"
      :close-on-click-modal="false"
    >
      <div class="apply-pet">
        <span class="apply-pet-emoji">{{ speciesEmoji }}</span>
        <div>
          <strong>{{ pet?.name }}</strong>
          <span>{{ pet?.breed }} · {{ pet?.age_text }} · {{ pet?.city }}</span>
        </div>
      </div>

      <el-form ref="applyFormRef" :model="applyForm" :rules="applyRules" label-position="top">
        <el-form-item label="申请理由" prop="reason">
          <el-input
            v-model="applyForm.reason"
            type="textarea"
            :rows="5"
            maxlength="500"
            show-word-limit
            placeholder="请介绍你的居住环境、家庭成员是否同意、每天能陪伴多久，以及为什么想领养它（至少 10 个字）"
          />
        </el-form-item>
      </el-form>

      <el-alert
        type="info"
        :closable="false"
        show-icon
        title="提交后志愿者会在 48 小时内联系你，请保持手机畅通。"
      />

      <template #footer>
        <el-button @click="applyVisible = false">取消</el-button>
        <el-button type="primary" :loading="applying" @click="handleApply">提交申请</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Star, StarFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

import { getPetDetailApi } from '@/api/pet'
import {
  applyAdoptionApi,
  getFavoriteStatusApi,
  toggleFavoriteApi
} from '@/api/adoption'

const route = useRoute()
const router = useRouter()

const pet = ref(null)
const loading = ref(false)
const error = ref('')

const isFavorited = ref(false)
const favoriteCount = ref(0)
const favoriteLoading = ref(false)

const applyVisible = ref(false)
const applying = ref(false)
const applied = ref(false)
const applyFormRef = ref(null)

const applyForm = reactive({ reason: '' })

const applyRules = {
  reason: [
    { required: true, message: '请填写申请理由', trigger: 'blur' },
    { min: 10, max: 500, message: '申请理由需要 10 - 500 个字', trigger: 'blur' }
  ]
}

// 相册：优先使用 images，没有则用封面兜底
const galleryImages = computed(() => {
  if (!pet.value) return []
  const images = Array.isArray(pet.value.images) ? pet.value.images : []
  const valid = images.filter(Boolean)
  if (valid.length) return valid
  return pet.value.cover_image ? [pet.value.cover_image] : []
})

const speciesEmoji = computed(() => {
  if (!pet.value) return '🐾'
  if (pet.value.species === '猫') return '🐱'
  if (pet.value.species === '狗') return '🐶'
  return '🐾'
})

const statusTagType = computed(() => {
  if (!pet.value) return 'info'
  if (pet.value.status === '可领养') return 'success'
  if (pet.value.status === '审核中') return 'warning'
  return 'info'
})

const petId = computed(() => Number(route.params.id))

// 加载详情
const loadDetail = async () => {
  if (!Number.isFinite(petId.value) || petId.value <= 0) {
    error.value = '宠物编号不合法'
    return
  }

  loading.value = true
  error.value = ''
  try {
    const res = await getPetDetailApi(petId.value)
    if (res.code === 200) {
      pet.value = res.data
    } else {
      error.value = res.message || '宠物不存在或已下架'
    }
  } catch (err) {
    console.error('宠物详情加载失败:', err)
    error.value = '网络异常，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 加载收藏状态
const loadFavoriteStatus = async () => {
  try {
    const res = await getFavoriteStatusApi(petId.value)
    if (res.code === 200) {
      isFavorited.value = Boolean(res.data?.is_favorited)
      favoriteCount.value = Number(res.data?.favorite_count) || 0
    }
  } catch (err) {
    // 收藏状态失败不阻断详情展示
    console.warn('收藏状态加载失败:', err)
  }
}

// 收藏 / 取消收藏
const handleToggleFavorite = async () => {
  favoriteLoading.value = true
  try {
    const res = await toggleFavoriteApi({ pet_id: petId.value })
    if (res.code === 200) {
      isFavorited.value = Boolean(res.data?.is_favorited)
      favoriteCount.value = Number(res.data?.favorite_count) || 0
      ElMessage.success(res.message || '操作成功')
    }
  } catch (err) {
    console.error('收藏操作失败:', err)
  } finally {
    favoriteLoading.value = false
  }
}

const openApplyDialog = () => {
  if (!pet.value || pet.value.status !== '可领养') return
  applyForm.reason = ''
  applyVisible.value = true
}

// 提交申请
const handleApply = async () => {
  const valid = await applyFormRef.value?.validate().catch(() => false)
  if (!valid) return

  applying.value = true
  try {
    const res = await applyAdoptionApi({
      pet_id: petId.value,
      reason: applyForm.reason.trim()
    })

    if (res.code === 200) {
      applied.value = true
      applyVisible.value = false
      ElMessage.success(res.message || '申请提交成功')
    } else {
      ElMessage.error(res.message || '申请提交失败')
    }
  } catch (err) {
    console.error('领养申请提交失败:', err)
  } finally {
    applying.value = false
  }
}

onMounted(() => {
  loadDetail()
  loadFavoriteStatus()
})
</script>

<style scoped>
.pet-detail-page {
  max-width: 1180px;
  margin: 0 auto;
}

.crumb {
  margin-bottom: 16px;
  font-size: 13px;
}

.detail-card {
  padding: 32px;
  border-radius: var(--radius-lg, 12px);
  background: var(--bg-card, #ffffff);
  border: 1px solid var(--border, #eaedf3);
}

.detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr);
  gap: 20px;
  align-items: start;
}

/* 相册 */
.gallery-card {
  overflow: hidden;
  border-radius: var(--radius-lg, 12px);
  background: var(--bg-card, #ffffff);
  border: 1px solid var(--border, #eaedf3);
}

.gallery {
  background: #fff6f1;
}

.gallery-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.gallery-fallback {
  display: grid;
  place-items: center;
  height: 420px;
  font-size: 96px;
  background: linear-gradient(135deg, #fff1ec, #ffe1d6);
}

.gallery-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  font-size: 12px;
  color: var(--text-sub, #8892a0);
  border-top: 1px solid var(--border, #eaedf3);
}

/* 右侧信息 */
.info-card {
  padding: 24px;
  border-radius: var(--radius-lg, 12px);
  background: var(--bg-card, #ffffff);
  border: 1px solid var(--border, #eaedf3);
}

.title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.title-row h1 {
  margin: 0 0 6px;
  font-size: 28px;
  color: var(--text-main, #1f2937);
}

.sub-title {
  margin: 0;
  font-size: 13px;
  color: var(--text-sub, #8892a0);
}

.quick-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}

.quick-tag {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  color: var(--text-body, #4b5563);
  background: var(--bg-muted, #f4f6fa);
}

.is-healthy {
  color: #15803d;
  background: #f0fdf4;
}

.is-warning {
  color: #b45309;
  background: #fffbeb;
}

.section-title {
  margin: 0 0 8px;
  font-size: 16px;
  color: var(--text-main, #1f2937);
}

.description {
  margin: 0 0 18px;
  font-size: 13px;
  line-height: 1.9;
  color: var(--text-body, #4b5563);
}

.info-table {
  margin-bottom: 18px;
}

.info-table :deep(.el-descriptions__label) {
  width: 92px;
  font-size: 12px;
  color: var(--text-sub, #8892a0);
}

.info-table :deep(.el-descriptions__content) {
  font-size: 12px;
  color: var(--text-main, #1f2937);
}

.action-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.apply-btn {
  min-width: 140px;
  border: none;
  border-radius: var(--radius-md, 10px);
  background: linear-gradient(135deg, #ff9a6c, #ff6b4a);
}

.apply-btn.is-disabled {
  background: #d8dee9;
}

.fav-count {
  margin-left: 4px;
  font-size: 12px;
}

.notice {
  border-radius: var(--radius-md, 10px);
}

/* 申请弹窗 */
.apply-pet {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  margin-bottom: 16px;
  border-radius: var(--radius-md, 10px);
  background: var(--brand-weak, #fff1ec);
}

.apply-pet-emoji {
  font-size: 30px;
}

.apply-pet div {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.apply-pet strong {
  font-size: 15px;
  color: var(--text-main, #1f2937);
}

.apply-pet span {
  font-size: 12px;
  color: var(--text-sub, #8892a0);
}

@media (max-width: 992px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .info-card {
    padding: 18px;
  }

  .title-row h1 {
    font-size: 24px;
  }

  .action-bar :deep(.el-button) {
    flex: 1;
  }
}
</style>