<template>
  <router-link class="pet-card" :to="`/manager/pet/detail/${pet.id}`">
    <div class="pet-cover">
      <img
        v-if="pet.cover_image && !imgError"
        :src="pet.cover_image"
        :alt="pet.name"
        loading="lazy"
        @error="imgError = true"
      />
      <div v-else class="cover-fallback">{{ speciesEmoji }}</div>

      <span class="status-chip" :class="statusClass">{{ pet.status }}</span>
      <span v-if="pet.view_count > 300" class="hot-chip">🔥 热门</span>
    </div>

    <div class="pet-body">
      <div class="pet-title-row">
        <h3 class="pet-name">{{ pet.name }}</h3>
        <span class="pet-gender" :class="pet.gender === '公' ? 'is-male' : 'is-female'">
          {{ pet.gender === '公' ? '♂' : '♀' }}
        </span>
      </div>

      <p class="pet-meta">
        {{ pet.breed || '未知品种' }} · {{ pet.age_text }} · {{ pet.city || '待确认' }}
      </p>

      <div class="pet-tags">
        <el-tag
          size="small"
          effect="light"
          :type="pet.health_status === '健康' ? 'success' : 'warning'"
        >
          {{ pet.health_status }}
        </el-tag>
        <el-tag v-if="pet.vaccinated" size="small" type="info" effect="plain">已疫苗</el-tag>
        <el-tag v-if="pet.sterilized" size="small" type="info" effect="plain">已绝育</el-tag>
      </div>
    </div>
  </router-link>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  pet: {
    type: Object,
    required: true
  }
})

// 图片加载失败时降级为 emoji，避免出现破图
const imgError = ref(false)

// 切换到另一只宠物时重置错误状态
watch(
  () => props.pet.id,
  () => {
    imgError.value = false
  }
)

// 不同物种的占位图标
const speciesEmoji = computed(() => {
  if (props.pet.species === '猫') return '🐱'
  if (props.pet.species === '狗') return '🐶'
  return '🐾'
})

// 状态颜色
const statusClass = computed(() => {
  if (props.pet.status === '已领养') return 'is-adopted'
  if (props.pet.status === '审核中') return 'is-reviewing'
  return 'is-available'
})
</script>

<style scoped>
.pet-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: var(--radius-lg, 12px);
  background: var(--bg-card, #ffffff);
  border: 1px solid var(--border, #eaedf3);
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.pet-card:hover {
  transform: translateY(-4px);
  border-color: #ffd2c4;
  box-shadow: 0 14px 30px rgba(31, 41, 55, 0.1);
}

.pet-cover {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  background: var(--brand-weak, #fff1ec);
  overflow: hidden;
}

.pet-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.35s ease;
}

.pet-card:hover .pet-cover img {
  transform: scale(1.05);
}

.cover-fallback {
  display: grid;
  place-items: center;
  width: 100%;
  height: 100%;
  font-size: 56px;
  background: linear-gradient(135deg, #fff1ec, #ffe1d6);
}

.status-chip {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  color: #ffffff;
  backdrop-filter: blur(4px);
}

.is-available {
  background: rgba(34, 197, 94, 0.9);
}

.is-reviewing {
  background: rgba(245, 158, 11, 0.92);
}

.is-adopted {
  background: rgba(107, 114, 128, 0.9);
}

.hot-chip {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 11px;
  color: #ffffff;
  background: rgba(239, 91, 58, 0.92);
}

.pet-body {
  padding: 14px 16px 16px;
}

.pet-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pet-name {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: var(--text-main, #1f2937);
}

.pet-gender {
  display: grid;
  place-items: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 700;
}

.is-male {
  color: #2563eb;
  background: #eff6ff;
}

.is-female {
  color: #db2777;
  background: #fdf2f8;
}

.pet-meta {
  margin: 8px 0 10px;
  font-size: 12px;
  color: var(--text-sub, #8892a0);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pet-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.pet-tags :deep(.el-tag) {
  border-radius: 6px;
}
</style>