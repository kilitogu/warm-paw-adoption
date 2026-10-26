<template>
  <div class="home-page">
    <!-- 品牌 Hero -->
    <HomeHero />

    <!-- 数据看板 -->
    <StatBoard :stats="stats" class="home-block" />

    <!-- 领养流程 -->
    <FlowSteps class="home-block" />

    <!-- 精选宠物 -->
    <section class="home-block featured">
      <div class="block-head">
        <div>
          <h2>本周期待回家</h2>
          <p>由救助站与志愿者共同推荐</p>
        </div>
        <router-link to="/manager/pets" class="more-link">
          查看全部
          <el-icon><ArrowRight /></el-icon>
        </router-link>
      </div>

      <!-- 加载态 -->
      <div v-if="loading" class="pet-grid">
        <el-skeleton v-for="n in 4" :key="n" animated class="skeleton-card">
          <template #template>
            <el-skeleton-item variant="image" class="skeleton-cover" />
            <div class="skeleton-body">
              <el-skeleton-item variant="h3" style="width: 50%" />
              <el-skeleton-item variant="text" style="width: 80%; margin-top: 10px" />
              <el-skeleton-item variant="text" style="width: 60%; margin-top: 8px" />
            </div>
          </template>
        </el-skeleton>
      </div>

      <!-- 空态 -->
      <el-empty
        v-else-if="!pets.length"
        description="暂时没有可推荐的宠物，去列表看看吧"
        class="empty-block"
      >
        <router-link to="/manager/pets">
          <el-button type="primary" plain>浏览全部宠物</el-button>
        </router-link>
      </el-empty>

      <!-- 宠物卡片 -->
      <div v-else class="pet-grid">
        <PetCard v-for="pet in pets" :key="pet.id" :pet="pet" />
      </div>
    </section>

    <!-- 成功案例 -->
    <section class="home-block stories">
      <div class="block-head">
        <div>
          <h2>它们已经回家了</h2>
          <p>每一段领养故事，都是一次双向奔赴</p>
        </div>
      </div>

      <el-carousel height="220px" :interval="5000" indicator-position="outside" class="story-carousel">
        <el-carousel-item v-for="story in stories" :key="story.name">
          <div class="story-card">
            <div class="story-avatar">{{ story.emoji }}</div>
            <div class="story-content">
              <p class="story-quote">“{{ story.quote }}”</p>
              <div class="story-meta">
                <strong>{{ story.user }}</strong>
                <span>领养了 {{ story.pet }} · {{ story.city }}</span>
              </div>
            </div>
            <div class="story-badge">真实领养家庭</div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </section>

    <!-- 底部 CTA -->
    <section class="home-block bottom-cta">
      <div class="cta-inner">
        <div class="cta-emoji">🐾</div>
        <h2>准备好给它一个家了吗？</h2>
        <p>花 3 分钟提交申请，剩下的交给我们和志愿者</p>
        <div class="cta-actions">
          <router-link to="/manager/pets">
            <el-button type="primary" size="large" round>开始领养</el-button>
          </router-link>
          <router-link to="/manager/guide">
            <el-button size="large" round class="cta-outline">先看领养指南</el-button>
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

import HomeHero from '@/components/HomeHero.vue'
import PetCard from '@/components/PetCard.vue'
import FlowSteps from '@/components/FlowSteps.vue'
import StatBoard from '@/components/StatBoard.vue'
import { getRecommendPetsApi } from '@/api/pet'
import { getOverviewApi } from '@/api/stats'

const pets = ref([])
const stats = ref({ pet_total: 0, adopted_total: 0, org_total: 0 })
const loading = ref(false)

// 成功案例静态数据
const stories = [
  {
    emoji: '🐱',
    quote: '奶糖到家第一晚就睡在我枕边，现在每天叫我起床。感谢志愿者耐心地帮我匹配。',
    user: '林女士',
    pet: '布偶猫「奶糖」',
    city: '杭州'
  },
  {
    emoji: '🐶',
    quote: '本来担心上班没人陪它，AI 助手推荐了性格独立的柴犬，现在一切都刚刚好。',
    user: '陈先生',
    pet: '柴犬「阿福」',
    city: '上海'
  },
  {
    emoji: '🐈',
    quote: '领养流程比想象中透明，健康档案、疫苗记录都能查到，家访也很专业。',
    user: '周同学',
    pet: '狸花猫「花卷」',
    city: '武汉'
  }
]

// 加载首页数据：推荐宠物 + 数据看板
const loadHomeData = async () => {
  loading.value = true
  try {
    const [petRes, statRes] = await Promise.all([
      getRecommendPetsApi(4),
      getOverviewApi()
    ])

    if (petRes.code === 200) {
      pets.value = petRes.data || []
    }

    if (statRes.code === 200) {
      stats.value = statRes.data || stats.value
    }
  } catch (error) {
    console.error('首页数据加载失败:', error)
    ElMessage.error('首页数据加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadHomeData()
})
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  gap: 22px;
  max-width: 1180px;
  margin: 0 auto;
  padding-bottom: 12px;
}

.home-block {
  margin-top: 2px;
}

.block-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.block-head h2 {
  margin: 0 0 4px;
  font-size: 22px;
  color: var(--text-main, #1f2937);
}

.block-head p {
  margin: 0;
  font-size: 13px;
  color: var(--text-sub, #8892a0);
}

.more-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--brand, #ff7a59);
  text-decoration: none;
  white-space: nowrap;
}

.more-link:hover {
  color: var(--brand-dark, #ef5b3a);
}

/* 精选宠物 */
.pet-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.skeleton-card {
  border-radius: var(--radius-lg, 12px);
  overflow: hidden;
  background: var(--bg-card, #ffffff);
  border: 1px solid var(--border, #eaedf3);
}

.skeleton-cover {
  width: 100%;
  height: 168px;
}

.skeleton-body {
  padding: 14px 16px 18px;
}

.empty-block {
  padding: 24px 0;
  background: var(--bg-card, #ffffff);
  border-radius: var(--radius-lg, 12px);
  border: 1px dashed var(--border, #eaedf3);
}

/* 成功案例 */
.story-carousel {
  border-radius: var(--radius-lg, 12px);
  overflow: hidden;
}

.story-card {
  display: flex;
  align-items: center;
  gap: 28px;
  height: 100%;
  padding: 30px 40px;
  background: linear-gradient(135deg, #fff7f2, #fff1ec);
  border: 1px solid #ffe0d4;
  border-radius: var(--radius-lg, 12px);
}

.story-avatar {
  display: grid;
  place-items: center;
  width: 110px;
  height: 110px;
  border-radius: 50%;
  font-size: 52px;
  background: #ffffff;
  box-shadow: 0 10px 24px rgba(239, 91, 58, 0.14);
  flex: none;
}

.story-content {
  flex: 1;
  min-width: 0;
}

.story-quote {
  margin: 0 0 16px;
  font-size: 15px;
  line-height: 1.9;
  color: var(--text-body, #4b5563);
}

.story-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.story-meta strong {
  font-size: 14px;
  color: var(--text-main, #1f2937);
}

.story-meta span {
  font-size: 12px;
  color: var(--text-sub, #8892a0);
}

.story-badge {
  align-self: flex-start;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  color: var(--brand-dark, #ef5b3a);
  background: #ffffff;
  border: 1px solid #ffd2c4;
  flex: none;
}

/* 底部 CTA */
.bottom-cta {
  padding: 40px 24px;
  border-radius: 20px;
  background: linear-gradient(135deg, #ff9a6c, #ff6b4a);
  color: #ffffff;
  text-align: center;
  box-shadow: 0 16px 36px rgba(255, 107, 74, 0.22);
}

.cta-inner {
  max-width: 560px;
  margin: 0 auto;
}

.cta-emoji {
  font-size: 34px;
  margin-bottom: 10px;
}

.bottom-cta h2 {
  margin: 0 0 10px;
  font-size: 24px;
}

.bottom-cta p {
  margin: 0 0 22px;
  font-size: 14px;
  opacity: 0.92;
}

.cta-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.cta-actions :deep(.el-button--primary) {
  background: #ffffff;
  border-color: #ffffff;
  color: var(--brand-dark, #ef5b3a);
  font-weight: 600;
  padding: 0 30px;
}

.cta-actions :deep(.el-button--primary:hover) {
  background: #fff4ee;
  border-color: #fff4ee;
}

.cta-outline {
  background: transparent;
  border-color: rgba(255, 255, 255, 0.7);
  color: #ffffff;
  padding: 0 26px;
}

.cta-outline:hover {
  background: rgba(255, 255, 255, 0.14);
  border-color: #ffffff;
  color: #ffffff;
}

@media (max-width: 992px) {
  .pet-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .pet-grid {
    grid-template-columns: 1fr;
  }

  .story-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
    padding: 22px;
  }

  .story-avatar {
    width: 72px;
    height: 72px;
    font-size: 34px;
  }

  .story-quote {
    font-size: 13px;
  }

  .block-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>