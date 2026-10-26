<template>
  <section class="stat-board">
    <div v-for="item in items" :key="item.key" class="stat-item">
      <div class="stat-icon">{{ item.icon }}</div>
      <div class="stat-content">
        <div class="stat-value">
          {{ display[item.key] }}
          <span class="stat-unit">{{ item.unit }}</span>
        </div>
        <div class="stat-label">{{ item.label }}</div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onBeforeUnmount, reactive, watch } from 'vue'

const props = defineProps({
  stats: {
    type: Object,
    default: () => ({ pet_total: 0, adopted_total: 0, org_total: 0 })
  }
})

// 展示值，通过 requestAnimationFrame 做数字滚动
const display = reactive({
  pet_total: 0,
  adopted_total: 0,
  org_total: 0
})

const items = [
  { key: 'pet_total', label: '在架待领养', unit: '只', icon: '🐾' },
  { key: 'adopted_total', label: '累计成功领养', unit: '次', icon: '🏡' },
  { key: 'org_total', label: '合作救助站', unit: '家', icon: '🤝' }
]

let rafId = 0

const animate = () => {
  cancelAnimationFrame(rafId)

  const targets = {
    pet_total: Number(props.stats?.pet_total) || 0,
    adopted_total: Number(props.stats?.adopted_total) || 0,
    org_total: Number(props.stats?.org_total) || 0
  }

  // 用户偏好减少动画时直接赋值
  if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) {
    Object.assign(display, targets)
    return
  }

  const duration = 800
  const start = performance.now()

  const step = (now) => {
    const progress = Math.min((now - start) / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)

    display.pet_total = Math.round(targets.pet_total * eased)
    display.adopted_total = Math.round(targets.adopted_total * eased)
    display.org_total = Math.round(targets.org_total * eased)

    if (progress < 1) {
      rafId = requestAnimationFrame(step)
    }
  }

  rafId = requestAnimationFrame(step)
}

watch(() => props.stats, animate, { deep: true, immediate: true })

onBeforeUnmount(() => {
  cancelAnimationFrame(rafId)
})
</script>

<style scoped>
.stat-board {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  padding: 22px 26px;
  border-radius: var(--radius-lg, 12px);
  background: var(--bg-card, #ffffff);
  border: 1px solid var(--border, #eaedf3);
  box-shadow: 0 8px 22px rgba(31, 41, 55, 0.04);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 4px 12px;
}

.stat-item + .stat-item {
  border-left: 1px dashed var(--border, #eaedf3);
}

.stat-icon {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 14px;
  font-size: 24px;
  background: var(--brand-weak, #fff1ec);
  flex: none;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-main, #1f2937);
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}

.stat-unit {
  margin-left: 4px;
  font-size: 12px;
  font-weight: 400;
  color: var(--text-sub, #8892a0);
}

.stat-label {
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-sub, #8892a0);
}

@media (max-width: 768px) {
  .stat-board {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .stat-item + .stat-item {
    border-left: none;
    border-top: 1px dashed var(--border, #eaedf3);
    padding-top: 12px;
  }
}
</style>