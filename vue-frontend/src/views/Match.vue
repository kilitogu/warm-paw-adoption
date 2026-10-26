<template>
  <div class="match-page">
    <!-- 左侧：历史会话 -->
    <ChatHistory
      :sessions="sessions"
      :active-id="activeId"
      @new="handleNewSession"
      @select="handleSelect"
      @rename="handleRename"
      @delete="handleDelete"
    />

    <!-- 右侧：对话窗口 -->
    <section class="chat-panel">
      <AiChat
        ref="chatRef"
        @messages-change="handleMessagesChange"
        @new-session="handleNewSession"
        @session-created="handleSessionCreated"
      />
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import AiChat from '@/components/AiChat.vue'
import ChatHistory from '@/components/ChatHistory.vue'
import {
  buildTitle,
  createSession,
  loadSessions,
  saveSessions
} from '@/utils/chatHistory'

const sessions = ref([])
const activeId = ref('')
const chatRef = ref(null)

const activeSession = computed(
  () => sessions.value.find((item) => item.id === activeId.value) || null
)

/** 写回 localStorage，并按更新时间重排/截断 */
const persist = () => {
  sessions.value = saveSessions(sessions.value)
}

/** 激活某个会话，把消息载入右侧对话 */
const activate = (session) => {
  if (!session) return
  activeId.value = session.id
  nextTick(() => {
    chatRef.value?.loadMessages(session.messages || [], session.sessionKey)
  })
}

/** 新建会话并激活 */
const handleNewSession = () => {
  const session = createSession()
  sessions.value.unshift(session)
  persist()
  activate(session)
}

const handleSelect = (id) => {
  const session = sessions.value.find((item) => item.id === id)
  if (session) activate(session)
}

/** 每轮结束：更新消息、标题、时间 */
const handleMessagesChange = (messages) => {
  const session = activeSession.value
  if (!session) return

  session.messages = messages
  session.title = buildTitle(messages)
  session.updatedAt = Date.now()
  persist()
}

/** 后端返回新的 session_id 时同步到当前会话 */
const handleSessionCreated = (sessionKey) => {
  const session = activeSession.value
  if (!session || !sessionKey) return
  session.sessionKey = sessionKey
  session.updatedAt = Date.now()
  persist()
}

/** 重命名 */
const handleRename = async (session) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入新的会话标题', '重命名会话', {
      inputValue: session.title,
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputValidator: (val) => (val && val.trim() ? true : '标题不能为空')
    })

    session.title = value.trim().slice(0, 30)
    session.updatedAt = Date.now()
    persist()
    ElMessage.success('已重命名')
  } catch (error) {
    // 用户取消，不处理
  }
}

/** 删除 */
const handleDelete = async (session) => {
  try {
    await ElMessageBox.confirm(
      `确定删除「${session.title}」吗？删除后无法恢复。`,
      '删除会话',
      {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消'
      }
    )
  } catch (error) {
    return
  }

  sessions.value = sessions.value.filter((item) => item.id !== session.id)
  persist()

  if (activeId.value === session.id) {
    if (sessions.value.length) {
      activate(sessions.value[0])
    } else {
      handleNewSession()
    }
  }

  ElMessage.success('已删除')
}

onMounted(() => {
  sessions.value = loadSessions()

  if (!sessions.value.length) {
    handleNewSession()
    return
  }

  activate(sessions.value[0])
})
</script>

<style scoped>
.match-page {
  display: grid;
  grid-template-columns: 290px minmax(0, 1fr);
  grid-template-rows: minmax(0, 1fr);
  gap: 16px;
  max-width: 1180px;
  margin: 0 auto;
  height: calc(100vh - 150px);
  min-height: 620px;
}

.chat-panel {
  min-width: 0;
  min-height: 0;
  height: 100%;
  overflow: hidden;
}

@media (max-width: 992px) {
  .match-page {
    grid-template-columns: 1fr;
    height: auto;
    min-height: 0;
  }

  .chat-panel {
    height: 70vh;
    min-height: 560px;
  }
}

@media (max-width: 560px) {
  .chat-panel {
    height: 72vh;
    min-height: 520px;
  }
}
</style>
