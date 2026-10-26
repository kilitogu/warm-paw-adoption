<template>
  <section class="flow-section">
    <div class="section-head">
      <h2>四步，把爱带回家</h2>
      <p>从浏览到接回家，每一步都有志愿者陪伴</p>
    </div>

    <div class="flow-grid">
      <div v-for="(step, index) in steps" :key="step.title" class="flow-item">
        <div class="flow-index">{{ index + 1 }}</div>
        <div class="flow-icon">
          <el-icon :size="24"><component :is="step.icon" /></el-icon>
        </div>
        <h3>{{ step.title }}</h3>
        <p>{{ step.desc }}</p>
        <span v-if="index < steps.length - 1" class="flow-arrow" aria-hidden="true">→</span>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ChatDotRound, EditPen, House, Search } from '@element-plus/icons-vue'

// 领养流程静态数据
const steps = [
  {
    title: '浏览宠物',
    desc: '按物种、品种、城市筛选，查看健康档案与性格描述。',
    icon: Search
  },
  {
    title: '提交申请',
    desc: '填写领养理由与家庭情况，一次最多同时申请 3 只。',
    icon: EditPen
  },
  {
    title: '沟通审核',
    desc: '志愿者 48 小时内联系，进行线上沟通与家访。',
    icon: ChatDotRound
  },
  {
    title: '签订协议',
    desc: '签署领养协议、完成疫苗与绝育确认后接回家。',
    icon: House
  }
]
</script>

<style scoped>
.flow-section {
  padding: 8px 0 4px;
}

.section-head {
  text-align: center;
  margin-bottom: 26px;
}

.section-head h2 {
  margin: 0 0 8px;
  font-size: 24px;
  color: var(--text-main, #1f2937);
}

.section-head p {
  margin: 0;
  font-size: 13px;
  color: var(--text-sub, #8892a0);
}

.flow-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.flow-item {
  position: relative;
  padding: 22px 20px;
  border-radius: var(--radius-lg, 12px);
  background: var(--bg-card, #ffffff);
  border: 1px solid var(--border, #eaedf3);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.flow-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 24px rgba(31, 41, 55, 0.07);
}

.flow-index {
  position: absolute;
  top: 12px;
  right: 14px;
  font-size: 30px;
  font-weight: 800;
  color: #ffe4da;
  line-height: 1;
}

.flow-icon {
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  margin-bottom: 14px;
  border-radius: 12px;
  color: #ffffff;
  background: linear-gradient(135deg, #ff9a6c, #ff6b4a);
  box-shadow: 0 6px 14px rgba(255, 107, 74, 0.28);
}

.flow-item h3 {
  margin: 0 0 8px;
  font-size: 15px;
  color: var(--text-main, #1f2937);
}

.flow-item p {
  margin: 0;
  font-size: 12px;
  line-height: 1.8;
  color: var(--text-sub, #8892a0);
}

.flow-arrow {
  position: absolute;
  top: 50%;
  right: -14px;
  transform: translateY(-50%);
  z-index: 2;
  font-size: 18px;
  color: #ffc3b1;
}

@media (max-width: 992px) {
  .flow-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .flow-arrow {
    display: none;
  }
}

@media (max-width: 560px) {
  .flow-grid {
    grid-template-columns: 1fr;
  }
}
</style>