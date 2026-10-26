<template>
  <section class="hero">
    <!-- 装饰元素 -->
    <span class="paw paw-1" aria-hidden="true">🐾</span>
    <span class="paw paw-2" aria-hidden="true">🐾</span>
    <span class="paw paw-3" aria-hidden="true">🐾</span>

    <div class="hero-inner">
      <div class="hero-copy">
        <el-tag class="hero-badge" effect="light" round>领养代替购买</el-tag>
        <h1 class="hero-title">
          让每一次相遇<br />
          <span class="highlight">都是回家的开始</span>
        </h1>
        <p class="hero-desc">
          暖爪连接救助站、志愿者与爱心家庭，用透明健康档案和 AI 智能匹配，
          帮每一只毛孩子找到真正适合它的家。
        </p>

        <div class="hero-actions">
          <router-link to="/manager/pets">
            <el-button type="primary" size="large" class="cta-primary" :icon="Search">
              去领养
            </el-button>
          </router-link>
          <router-link to="/manager/match">
            <el-button size="large" class="cta-ghost" :icon="ChatDotRound">
              AI 智能匹配
            </el-button>
          </router-link>
        </div>

        <div class="hero-trust">
          <span>✓ 健康档案公开</span>
          <span>✓ 全流程免费</span>
          <span>✓ 领养后回访</span>
        </div>
      </div>

      <div class="hero-visual">
        <div class="visual-card">
          <div class="visual-emoji">🐶</div>
          <div class="visual-info">
            <strong>可乐</strong>
            <span>金毛 · 3岁 · 成都</span>
          </div>
          <span class="visual-tag">等待领养</span>
        </div>
        <div class="visual-card visual-card-2">
          <div class="visual-emoji">🐱</div>
          <div class="visual-info">
            <strong>奶糖</strong>
            <span>布偶猫 · 8个月 · 杭州</span>
          </div>
          <span class="visual-tag tag-blue">性格黏人</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ChatDotRound, Search } from '@element-plus/icons-vue'

// “AI 智能匹配”直接跳转 /manager/match，AI 对话内嵌在智能匹配页中
</script>

<style scoped>
.hero {
  position: relative;
  overflow: hidden;
  padding: 56px 40px;
  border-radius: 20px;
  background: linear-gradient(135deg, #fff4ee 0%, #ffe8df 45%, #fff9f5 100%);
  border: 1px solid #ffe0d4;
}

.hero::after {
  content: '';
  position: absolute;
  right: -120px;
  top: -120px;
  width: 360px;
  height: 360px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 122, 89, 0.18), transparent 70%);
}

.hero-inner {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 40px;
  max-width: 1180px;
  margin: 0 auto;
}

.hero-copy {
  flex: 1;
  min-width: 0;
}

.hero-badge {
  --el-tag-bg-color: rgba(255, 255, 255, 0.85);
  --el-tag-text-color: var(--brand-dark, #ef5b3a);
  --el-tag-border-color: #ffd2c4;
  margin-bottom: 18px;
  font-weight: 600;
}

.hero-title {
  margin: 0 0 18px;
  font-size: 40px;
  line-height: 1.3;
  color: var(--text-main, #1f2937);
  letter-spacing: 1px;
}

.hero-title .highlight {
  background: linear-gradient(135deg, #ff9a6c, #ff6b4a);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-desc {
  max-width: 520px;
  margin: 0 0 26px;
  font-size: 15px;
  line-height: 1.9;
  color: var(--text-body, #4b5563);
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.cta-primary {
  height: 46px;
  padding: 0 30px;
  border: none;
  border-radius: var(--radius-pill, 999px);
  font-size: 15px;
  font-weight: 600;
  background: linear-gradient(135deg, #ff9a6c, #ff6b4a);
  box-shadow: 0 8px 20px rgba(255, 107, 74, 0.3);
}

.cta-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(255, 107, 74, 0.4);
}

.cta-ghost {
  height: 46px;
  padding: 0 26px;
  border-radius: var(--radius-pill, 999px);
  border-color: #ffd2c4;
  color: var(--brand-dark, #ef5b3a);
  background: #ffffff;
}

.cta-ghost:hover {
  border-color: var(--brand, #ff7a59);
  background: var(--brand-weak, #fff1ec);
}

.hero-trust {
  display: flex;
  gap: 20px;
  margin-top: 22px;
  font-size: 12px;
  color: var(--text-sub, #8892a0);
  flex-wrap: wrap;
}

/* 右侧视觉卡 */
.hero-visual {
  position: relative;
  flex: none;
  width: 330px;
  height: 250px;
}

.visual-card {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 12px;
  width: 260px;
  padding: 14px 16px;
  border-radius: 16px;
  background: #ffffff;
  box-shadow: 0 14px 32px rgba(239, 91, 58, 0.14);
  top: 30px;
  left: 0;
  animation: float-card 5s ease-in-out infinite;
}

.visual-card-2 {
  top: 130px;
  left: 55px;
  animation-delay: 1.2s;
}

.visual-emoji {
  display: grid;
  place-items: center;
  width: 54px;
  height: 54px;
  border-radius: 14px;
  font-size: 28px;
  background: var(--brand-weak, #fff1ec);
  flex: none;
}

.visual-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.visual-info strong {
  font-size: 15px;
  color: var(--text-main, #1f2937);
}

.visual-info span {
  margin-top: 3px;
  font-size: 12px;
  color: var(--text-sub, #8892a0);
}

.visual-tag {
  margin-left: auto;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 11px;
  color: var(--brand-dark, #ef5b3a);
  background: var(--brand-weak, #fff1ec);
  white-space: nowrap;
}

.tag-blue {
  color: #2563eb;
  background: #eff6ff;
}

/* 装饰爪印 */
.paw {
  position: absolute;
  font-size: 26px;
  opacity: 0.22;
  transform: rotate(-18deg);
}

.paw-1 {
  top: 18%;
  left: 46%;
}

.paw-2 {
  bottom: 12%;
  left: 6%;
  font-size: 20px;
  transform: rotate(12deg);
}

.paw-3 {
  top: 12%;
  left: 3%;
  font-size: 16px;
}

@keyframes float-card {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .visual-card {
    animation: none;
  }
}

@media (max-width: 992px) {
  .hero-visual {
    display: none;
  }

  .hero {
    padding: 40px 24px;
  }

  .hero-title {
    font-size: 32px;
  }
}

@media (max-width: 560px) {
  .hero-title {
    font-size: 26px;
  }

  .hero-actions :deep(.el-button) {
    width: 100%;
  }
}
</style>
