<template>
  <div class="guide-page">
    <!-- 页头 -->
    <section class="guide-hero">
      <div class="hero-icon">📖</div>
      <div class="hero-text">
        <h1>领养指南</h1>
        <p>领养不是把它带回家，而是对它的一生负责。花 5 分钟读完，再做决定。</p>
      </div>
    </section>

    <!-- 领养条件 -->
    <section class="guide-section">
      <div class="section-head">
        <h2>一、领养条件</h2>
        <p>满足以下条件，才能通过志愿者审核</p>
      </div>

      <div class="condition-grid">
        <div v-for="item in conditions" :key="item.title" class="condition-card">
          <div class="condition-icon">{{ item.icon }}</div>
          <h3>{{ item.title }}</h3>
          <p>{{ item.desc }}</p>
        </div>
      </div>
    </section>

    <!-- 领养流程 -->
    <section class="guide-section">
      <div class="section-head">
        <h2>二、领养流程</h2>
        <p>完整流程通常需要 3 - 14 天</p>
      </div>

      <div class="flow-list">
        <div v-for="(step, index) in flowSteps" :key="step.title" class="flow-row">
          <div class="flow-index">{{ index + 1 }}</div>
          <div class="flow-content">
            <div class="flow-title-row">
              <h3>{{ step.title }}</h3>
              <el-tag size="small" effect="plain" round>{{ step.time }}</el-tag>
            </div>
            <p>{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 材料清单 -->
    <section class="guide-section">
      <div class="section-head">
        <h2>三、材料清单</h2>
        <p>提前准备，能明显缩短审核时间</p>
      </div>

      <div class="material-layout">
        <div class="material-card">
          <h3>必备材料</h3>
          <ul class="material-list">
            <li v-for="item in requiredMaterials" :key="item">
              <el-icon class="check-icon"><CircleCheck /></el-icon>
              <span>{{ item }}</span>
            </li>
          </ul>
        </div>

        <div class="material-card">
          <h3>视情况补充</h3>
          <ul class="material-list">
            <li v-for="item in optionalMaterials" :key="item">
              <el-icon class="dot-icon"><InfoFilled /></el-icon>
              <span>{{ item }}</span>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <!-- 常见问题 -->
    <section class="guide-section">
      <div class="section-head faq-head">
        <div>
          <h2>四、常见问题</h2>
          <p>点击问题展开答案，也可以直接问 AI 助手</p>
        </div>
        <el-button text type="primary" :icon="ChatDotRound" @click="handleAskAi">
          问 AI 助手
        </el-button>
      </div>

      <!-- FAQ 加载态 -->
      <el-skeleton v-if="faqLoading" animated :rows="6" class="faq-skeleton" />

      <!-- FAQ 错误态 -->
      <el-alert
        v-else-if="faqError"
        type="error"
        :closable="false"
        show-icon
        :title="faqError"
        class="faq-alert"
      >
        <template #default>
          <el-button link type="primary" @click="loadFaq">重新加载</el-button>
        </template>
      </el-alert>

      <!-- FAQ 空态 -->
      <el-empty v-else-if="!faqGroups.length" description="暂无常见问题" />

      <!-- FAQ 分组折叠面板 -->
      <div v-else class="faq-groups">
        <div v-for="group in faqGroups" :key="group.category" class="faq-group">
          <h3 class="group-title">{{ group.category }}</h3>
          <el-collapse accordion class="faq-collapse">
            <el-collapse-item
              v-for="faq in group.items"
              :key="faq.id"
              :name="faq.id"
              :title="faq.question"
            >
              <p class="faq-answer">{{ faq.answer }}</p>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </section>

    <!-- 责任告知 -->
    <section class="guide-section responsibility">
      <div class="section-head">
        <h2>五、责任告知</h2>
        <p>请在提交申请前，逐条确认</p>
      </div>

      <el-alert
        type="warning"
        :closable="false"
        show-icon
        title="领养是一份十余年的承诺"
        class="responsibility-alert"
      >
        <ul class="responsibility-list">
          <li v-for="item in responsibilities" :key="item">{{ item }}</li>
        </ul>
      </el-alert>

      <div class="bottom-actions">
        <router-link to="/manager/pets">
          <el-button type="primary" size="large" round>我准备好了，去看宠物</el-button>
        </router-link>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ChatDotRound, CircleCheck, InfoFilled } from '@element-plus/icons-vue'

import { getGuideFaqGroupsApi } from '@/api/guide'

const router = useRouter()
const faqGroups = ref([])
const faqLoading = ref(false)
const faqError = ref('')

// 领养条件
const conditions = [
  {
    icon: '🎂',
    title: '年满 18 周岁',
    desc: '具备完全民事行为能力，能独立签署领养协议并承担饲养责任。'
  },
  {
    icon: '🏠',
    title: '稳定住所',
    desc: '自有或长期租赁住房，租房需房东书面同意；阳台与窗户必须封网。'
  },
  {
    icon: '👨‍👩‍👧',
    title: '全家同意',
    desc: '所有共同居住人同意养宠，无对宠物过敏或明确反对的成员。'
  },
  {
    icon: '💉',
    title: '科学喂养',
    desc: '承诺按时疫苗、驱虫、绝育，生病及时就医，不喂劣质粮、不散养。'
  }
]

// 领养流程
const flowSteps = [
  {
    title: '浏览与收藏',
    time: '随时',
    desc: '通过物种、品种、城市、年龄筛选宠物，查看健康档案与性格描述，收藏心仪的毛孩子。'
  },
  {
    title: '提交领养申请',
    time: '约 3 分钟',
    desc: '在详情页点击“申请领养”，填写居住环境、家庭成员意见、每日陪伴时间与申请理由。'
  },
  {
    title: '志愿者沟通',
    time: '48 小时内',
    desc: '志愿者通过电话或微信了解情况，必要时安排视频看房或上门家访。'
  },
  {
    title: '签署协议',
    time: '1 - 3 天',
    desc: '确认领养条件后签署电子协议，约定回访方式、医疗责任与退养条款。'
  },
  {
    title: '接它回家',
    time: '约定时间',
    desc: '自备航空箱、牵引绳与过渡粮，前两周保持环境安静，帮助宠物适应新家。'
  }
]

// 材料清单
const requiredMaterials = [
  '本人身份证正反面照片',
  '居住证明（房产证或租赁合同）',
  '房东同意养宠的书面说明（租房）',
  '家庭成员知情同意书',
  '近三个月收入或在校证明'
]

const optionalMaterials = [
  '既往养宠经历证明（照片、疫苗本）',
  '宠物医院合作意向或常去医院信息',
  '封窗、防护网安装照片',
  '若为合租，室友同意说明'
]

// 责任告知
const responsibilities = [
  '不弃养、不虐待、不私自转送，确需退养时第一时间联系原救助站。',
  '每年至少一次全面体检，按时接种疫苗并进行体内外驱虫。',
  '外出使用牵引绳或航空箱，猫咪必须封窗，避免走失与坠楼。',
  '配合领养后第 1 周、第 1 个月、第 3 个月的回访。',
  '如搬家、结婚、怀孕等情况发生，提前与救助站沟通安置方案。'
]

// 加载 FAQ 并按分类聚合
const loadFaq = async () => {
  faqLoading.value = true
  faqError.value = ''
  try {
    const res = await getGuideFaqGroupsApi()
    if (res.code === 200) {
      faqGroups.value = res.data || []
    } else {
      faqError.value = res.message || 'FAQ 加载失败'
    }
  } catch (err) {
    console.error('FAQ 加载失败:', err)
    faqError.value = '网络异常，FAQ 加载失败'
  } finally {
    faqLoading.value = false
  }
}

// 打开 AI 助手：跳转到内嵌对话的智能匹配页
const handleAskAi = () => {
  router.push('/manager/match')
}

onMounted(() => {
  loadFaq()
})
</script>

<style scoped>
.guide-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

/* 页头 */
.guide-hero {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 28px 32px;
  border-radius: 18px;
  background: linear-gradient(135deg, #fff4ee, #ffe8df);
  border: 1px solid #ffe0d4;
}

.hero-icon {
  display: grid;
  place-items: center;
  width: 64px;
  height: 64px;
  border-radius: 18px;
  font-size: 30px;
  background: #ffffff;
  box-shadow: 0 8px 20px rgba(239, 91, 58, 0.12);
  flex: none;
}

.hero-text h1 {
  margin: 0 0 6px;
  font-size: 24px;
  color: var(--text-main, #1f2937);
}

.hero-text p {
  margin: 0;
  font-size: 13px;
  color: var(--text-body, #4b5563);
}

/* 通用区块 */
.guide-section {
  padding: 24px 26px;
  border-radius: var(--radius-lg, 12px);
  background: var(--bg-card, #ffffff);
  border: 1px solid var(--border, #eaedf3);
}

.section-head {
  margin-bottom: 18px;
}

.section-head h2 {
  margin: 0 0 5px;
  font-size: 18px;
  color: var(--text-main, #1f2937);
}

.section-head p {
  margin: 0;
  font-size: 12px;
  color: var(--text-sub, #8892a0);
}

/* 领养条件 */
.condition-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.condition-card {
  padding: 18px;
  border-radius: var(--radius-md, 10px);
  background: #fffaf7;
  border: 1px solid #ffe6dc;
}

.condition-icon {
  font-size: 26px;
  margin-bottom: 10px;
}

.condition-card h3 {
  margin: 0 0 6px;
  font-size: 14px;
  color: var(--text-main, #1f2937);
}

.condition-card p {
  margin: 0;
  font-size: 12px;
  line-height: 1.8;
  color: var(--text-sub, #8892a0);
}

/* 流程 */
.flow-list {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.flow-row {
  display: flex;
  gap: 16px;
  padding: 14px 0;
}

.flow-row + .flow-row {
  border-top: 1px dashed var(--border, #eaedf3);
}

.flow-index {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  font-size: 14px;
  font-weight: 700;
  color: #ffffff;
  background: linear-gradient(135deg, #ff9a6c, #ff6b4a);
  flex: none;
}

.flow-content {
  flex: 1;
  min-width: 0;
}

.flow-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}

.flow-title-row h3 {
  margin: 0;
  font-size: 14px;
  color: var(--text-main, #1f2937);
}

.flow-content p {
  margin: 0;
  font-size: 12px;
  line-height: 1.8;
  color: var(--text-sub, #8892a0);
}

/* 材料 */
.material-layout {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.material-card {
  padding: 18px;
  border-radius: var(--radius-md, 10px);
  background: var(--bg-muted, #f4f6fa);
}

.material-card h3 {
  margin: 0 0 12px;
  font-size: 14px;
  color: var(--text-main, #1f2937);
}

.material-list {
  display: flex;
  flex-direction: column;
  gap: 9px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.material-list li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 12px;
  line-height: 1.7;
  color: var(--text-body, #4b5563);
}

.check-icon {
  color: #22c55e;
  margin-top: 2px;
  flex: none;
}

.dot-icon {
  color: #f59e0b;
  margin-top: 2px;
  flex: none;
}

/* FAQ */
.faq-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
}

.faq-skeleton {
  padding: 10px 0;
}

.faq-alert {
  border-radius: var(--radius-md, 10px);
}

.faq-groups {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.group-title {
  margin: 0 0 8px;
  padding-left: 10px;
  border-left: 3px solid var(--brand, #ff7a59);
  font-size: 13px;
  color: var(--text-body, #4b5563);
}

.faq-collapse {
  border-top: none;
  border-bottom: none;
}

.faq-collapse :deep(.el-collapse-item__header) {
  font-size: 13px;
  color: var(--text-main, #1f2937);
  background: transparent;
}

.faq-collapse :deep(.el-collapse-item__wrap) {
  background: transparent;
}

.faq-answer {
  margin: 0;
  padding: 2px 4px 12px;
  font-size: 13px;
  line-height: 1.9;
  color: var(--text-body, #4b5563);
}

/* 责任告知 */
.responsibility-alert {
  border-radius: var(--radius-md, 10px);
}

.responsibility-list {
  margin: 8px 0 0;
  padding-left: 18px;
  font-size: 12px;
  line-height: 1.9;
}

.bottom-actions {
  display: flex;
  justify-content: center;
  margin-top: 22px;
}

.bottom-actions :deep(.el-button--primary) {
  padding: 0 32px;
  border: none;
  background: linear-gradient(135deg, #ff9a6c, #ff6b4a);
}

@media (max-width: 992px) {
  .condition-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .material-layout {
    grid-template-columns: 1fr;
  }

  .faq-head {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 560px) {
  .condition-grid {
    grid-template-columns: 1fr;
  }

  .guide-section {
    padding: 18px;
  }

  .guide-hero {
    padding: 20px;
  }
}
</style>