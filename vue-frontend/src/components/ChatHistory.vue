<template>
  <aside class="history-sidebar">
    <!-- 头部 -->
    <div class="history-head">
      <div class="history-brand">
        <div class="brand-logo">🐾</div>
        <div class="brand-text">
          <strong>智能匹配</strong>
          <span>历史会话</span>
        </div>
      </div>
      <el-button type="primary" size="small" :icon="Plus" @click="$emit('new')">
        新对话
      </el-button>
    </div>

    <!-- 会话列表 -->
    <div class="history-list">
      <template v-if="sessions.length">
        <div v-for="group in groups" :key="group.label" class="history-group">
          <p class="group-label">{{ group.label }}</p>

          <div
            v-for="session in group.items"
            :key="session.id"
            class="history-item"
            :class="{ 'is-active': session.id === activeId }"
            @click="$emit('select', session.id)"
          >
            <div class="item-main">
              <div class="item-title-row">
                <span class="item-title">{{ session.title || '新对话' }}</span>
                <span class="item-time">{{ formatTime(session.updatedAt) }}</span>
              </div>
              <p class="item-preview">{{ buildPreview(session.messages) }}</p>
            </div>

            <el-dropdown
              trigger="click"
              class="item-actions"
              @click.stop
              @command="(command) => handleCommand(command, session)"
            >
              <el-button text circle size="small" :icon="MoreFilled" @click.stop />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="rename">重命名</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </template>

      <el-empty v-else description="还没有历史会话" :image-size="72" />
    </div>

    <!-- 底部提示 -->
    <div class="history-foot">
      <p>描述城市、居住空间和作息，AI 会帮你匹配更合适的宠物。</p>
      <span>历史记录保存在本机浏览器</span>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { MoreFilled, Plus } from '@element-plus/icons-vue'

import { buildPreview } from '@/utils/chatHistory'

const props = defineProps({
  sessions: {
    type: Array,
    default: () => []
  },
  activeId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['select', 'new', 'rename', 'delete'])

// 按今天 / 昨天 / 更早分组
const groups = computed(() => {
  const now = new Date()
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
  const yesterdayStart = todayStart - 24 * 60 * 60 * 1000

  const buckets = {
    今天: [],
    昨天: [],
    更早: []
  }

  for (const session of props.sessions) {
    const time = session.updatedAt || 0
    if (time >= todayStart) {
      buckets['今天'].push(session)
    } else if (time >= yesterdayStart) {
      buckets['昨天'].push(session)
    } else {
      buckets['更早'].push(session)
    }
  }

  return Object.entries(buckets)
    .filter(([, items]) => items.length)
    .map(([label, items]) => ({ label, items }))
})

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const isToday =
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate()

  if (isToday) {
    return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
  }

  return `${date.getMonth() + 1}/${date.getDate()}`
}

const handleCommand = (command, session) => {
  if (command === 'rename') emit('rename', session)
  if (command === 'delete') emit('delete', session)
}
</script>

<style scoped>
.history-sidebar {
  display: flex;
  flex-direction: column;
  min-height: 0;
  height: 100%;
  padding: 18px 14px 14px;
  border-radius: 16px;
  border: 1px solid var(--border, #eaedf3);
  background: #ffffff;
}

.history-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border, #eaedf3);
  flex: none;
}

.history-brand {
  display: flex;
  align-items: center;
  gap: 9px;
  min-width: 0;
}

.brand-logo {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border-radius: 11px;
  font-size: 18px;
  color: #ffffff;
  background: linear-gradient(135deg, #ff9a6c, #ff6b4a);
  box-shadow: 0 6px 14px rgba(255, 107, 74, 0.28);
  flex: none;
}

.brand-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.brand-text strong {
  font-size: 14px;
  color: var(--text-main, #1f2937);
}

.brand-text span {
  font-size: 11px;
  color: var(--text-sub, #8892a0);
}

.history-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 12px 2px 8px;
}

.history-group + .history-group {
  margin-top: 10px;
}

.group-label {
  margin: 0 0 6px;
  padding-left: 6px;
  font-size: 10px;
  letter-spacing: 0.5px;
  color: var(--text-muted, #b3bbc8);
}

.history-item {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 9px 9px 9px 11px;
  margin-bottom: 4px;
  border-radius: 10px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: background 0.2s, border-color 0.2s;
}

.history-item:hover {
  background: var(--bg-muted, #f4f6fa);
}

.history-item.is-active {
  background: var(--brand-weak, #fff1ec);
  border-color: #ffd2c4;
}

.item-main {
  flex: 1;
  min-width: 0;
}

.item-title-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.item-title {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-main, #1f2937);
}

.item-time {
  flex: none;
  font-size: 10px;
  color: var(--text-muted, #b3bbc8);
}

.item-preview {
  margin: 4px 0 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 11px;
  color: var(--text-sub, #8892a0);
}

.item-actions {
  flex: none;
  opacity: 0;
  transition: opacity 0.2s;
}

.history-item:hover .item-actions,
.history-item.is-active .item-actions {
  opacity: 1;
}

.history-foot {
  flex: none;
  padding-top: 12px;
  border-top: 1px solid var(--border, #eaedf3);
}

.history-foot p {
  margin: 0 0 5px;
  font-size: 11px;
  line-height: 1.7;
  color: var(--text-sub, #8892a0);
}

.history-foot span {
  font-size: 10px;
  color: var(--text-muted, #b3bbc8);
}

@media (max-width: 992px) {
  .history-sidebar {
    height: auto;
    max-height: 220px;
  }

  .history-list {
    max-height: 120px;
  }

  .history-foot {
    display: none;
  }
}
</style>