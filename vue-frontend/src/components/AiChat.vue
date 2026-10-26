<template>
  <div class="ai-shell">
      <!-- 头部 -->
      <header class="ai-header">
        <div class="ai-brand">
          <div class="ai-avatar">🐾</div>
          <div class="ai-brand-text">
            <strong>暖爪 AI 匹配助手</strong>
            <span>
              <i class="dot" :class="{ 'is-busy': sending }"></i>
              {{ sending ? '正在思考…' : '在线' }}
            </span>
          </div>
        </div>
        <el-button text :icon="RefreshRight" @click="handleReset">新对话</el-button>
      </header>

      <!-- 消息区 -->
      <div ref="bodyRef" class="ai-body">
        <div
          v-for="message in messages"
          :key="message.id"
          class="message-row"
          :class="message.role"
        >
          <div v-if="message.role === 'assistant'" class="bubble-avatar">🐾</div>

          <div class="message-main">
            <!-- 思考过程 -->
            <el-collapse
              v-if="message.role === 'assistant' && hasThinking(message)"
              class="thinking"
            >
              <el-collapse-item name="thinking">
                <template #title>
                  <span class="thinking-title">
                    <el-icon><MagicStick /></el-icon>
                    思考过程
                  </span>
                </template>

                <div v-if="message.thinking.intent" class="thinking-row">
                  <span class="thinking-label">意图</span>
                  <el-tag size="small" effect="plain">{{ intentLabel(message.thinking.intent) }}</el-tag>
                </div>

                <div v-if="message.thinking.retrieval" class="thinking-row">
                  <span class="thinking-label">检索</span>
                  <div class="thinking-content">
                    <p class="retrieval-query">“{{ message.thinking.retrieval.query }}”</p>
                    <ul v-if="message.thinking.retrieval.sources?.length" class="source-list">
                      <li v-for="(source, index) in message.thinking.retrieval.sources" :key="index">
                        <span class="source-title">{{ source.title }}</span>
                        <span v-if="source.score" class="source-score">
                          {{ (source.score * 100).toFixed(0) }}%
                        </span>
                        <p class="source-snippet">{{ source.snippet }}</p>
                      </li>
                    </ul>
                    <p v-else class="source-empty">知识库未命中，已准备转人工</p>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>

            <!-- 工具调用卡片 -->
            <div v-if="message.thinking.tools.length" class="tool-list">
              <div
                v-for="(tool, index) in message.thinking.tools"
                :key="`${tool.name}-${index}`"
                class="tool-card"
              >
                <div class="tool-head">
                  <span class="tool-icon">{{ toolIcon(tool.name) }}</span>
                  <span class="tool-name">{{ toolLabel(tool.name) }}</span>
                  <el-icon v-if="tool.status === 'running'" class="is-loading tool-status">
                    <Loading />
                  </el-icon>
                  <el-icon v-else class="tool-status is-done">
                    <CircleCheck />
                  </el-icon>
                </div>
                <p v-if="tool.args && Object.keys(tool.args).length" class="tool-args">
                  {{ formatArgs(tool.args) }}
                </p>
                <p v-if="tool.summary" class="tool-summary">{{ tool.summary }}</p>
              </div>
            </div>

            <!-- 回复气泡 -->
            <div v-if="message.content" class="bubble" :class="{ 'is-error': message.status === 'error' }">
              {{ message.content }}
              <span v-if="message.status === 'streaming'" class="caret">▍</span>
            </div>

            <!-- 加载占位 -->
            <div v-else-if="message.status === 'streaming'" class="bubble typing">
              <span></span><span></span><span></span>
            </div>

            <!-- 错误提示 -->
            <div v-if="message.error" class="error-tip">
              <el-icon><WarningFilled /></el-icon>
              {{ message.error }}
            </div>

            <!-- 二次确认 -->
            <div v-if="message.confirm" class="confirm-card">
              <p class="confirm-title">
                {{ message.confirm.message || '确认提交领养申请吗？' }}
              </p>
              <p v-if="message.confirm.pet_name" class="confirm-meta">
                宠物：{{ message.confirm.pet_name }}
              </p>
              <p v-if="message.confirm.reason" class="confirm-reason">
                申请理由：{{ message.confirm.reason }}
              </p>
              <div class="confirm-actions">
                <el-button size="small" @click="handleConfirm(false)">取消</el-button>
                <el-button type="primary" size="small" @click="handleConfirm(true)">
                  确认提交
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 欢迎语与快捷问题 -->
        <div v-if="messages.length === 1" class="suggestions">
          <span class="suggestions-label">你可以这样问</span>
          <button
            v-for="item in suggestions"
            :key="item"
            type="button"
            class="suggestion-chip"
            @click="handleSend(item)"
          >
            {{ item }}
          </button>
        </div>
      </div>

      <!-- 输入区 -->
      <footer class="ai-composer">
        <el-input
          v-model="input"
          type="textarea"
          :rows="2"
          resize="none"
          maxlength="2000"
          :placeholder="hasPendingConfirm ? '请先在上方确认或取消申请' : '问问领养条件，或让我帮你找一只猫…'"
          @keydown.enter.exact.prevent="handleSend()"
        />
        <div class="composer-actions">
          <span class="composer-tip">Enter 发送 / Shift + Enter 换行</span>
          <el-button v-if="sending" size="small" @click="handleStop">
            <el-icon><VideoPause /></el-icon>
            停止
          </el-button>
          <el-button
            type="primary"
            size="small"
            :disabled="!input.trim() || sending || hasPendingConfirm"
            @click="handleSend()"
          >
            发送
          </el-button>
        </div>
      </footer>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import {
  CircleCheck,
  Loading,
  MagicStick,
  RefreshRight,
  VideoPause,
  WarningFilled
} from '@element-plus/icons-vue'

import { chatStream, confirmStream } from '@/api/ai'

const props = defineProps({
  sessionId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['session-created', 'messages-change', 'new-session'])

const bodyRef = ref(null)
const input = ref('')
const messages = ref([])
const sessionId = ref(props.sessionId || '')
const sending = ref(false)
const controller = ref(null)

// 存在待确认申请时，禁止继续发送新消息
const hasPendingConfirm = computed(() =>
  messages.value.some((message) => Boolean(message.confirm))
)

let timeoutId = 0
let messageSeq = 0

/** 创建一条消息，避免每个位置重复写 thinking/confirm 结构 */
const createMessage = (role, content = '', status = 'done') => ({
  id: `m-${++messageSeq}`,
  role,
  content,
  status,
  error: '',
  confirm: null,
  thinking: { intent: '', retrieval: null, tools: [] }
})

const suggestions = [
  '我一个人住，适合养猫还是狗？',
  '杭州有哪些性格温顺的猫？',
  '每天只能陪 2 小时，适合养什么狗？',
  '帮我申请奶糖'
]

const TOOL_LABELS = {
  search_pets: '搜索宠物',
  get_pet_detail: '查询宠物详情',
  check_adoption_eligibility: '资格校验',
  submit_adoption_intent: '提交领养申请',
  get_platform_stats: '查询平台数据'
}

const INTENT_LABELS = {
  chat: '闲聊',
  search: '找宠物',
  apply: '申请领养',
  faq: '知识问答'
}

const toolLabel = (name) => TOOL_LABELS[name] || name
const intentLabel = (intent) => INTENT_LABELS[intent] || intent

const toolIcon = (name) => {
  const map = {
    search_pets: '🔍',
    get_pet_detail: '📋',
    check_adoption_eligibility: '✅',
    submit_adoption_intent: '📝',
    get_platform_stats: '📊'
  }
  return map[name] || '🛠'
}

const formatArgs = (args) => {
  const parts = Object.entries(args)
    .filter(([, value]) => value !== null && value !== undefined && value !== '')
    .map(([key, value]) => `${key}=${value}`)
  return parts.join(' · ')
}

const hasThinking = (message) =>
  Boolean(message.thinking.intent || message.thinking.retrieval)

// 生成会话ID
const createSessionId = () => {
  if (window.crypto?.randomUUID) return window.crypto.randomUUID()
  return `s-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`
}

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  const el = bodyRef.value
  if (el) el.scrollTop = el.scrollHeight
}

// 60 秒超时
const clearTimer = () => {
  if (timeoutId) {
    clearTimeout(timeoutId)
    timeoutId = 0
  }
}

const resetTimer = (onTimeout) => {
  clearTimer()
  timeoutId = window.setTimeout(() => {
    onTimeout()
  }, 60000)
}

// 初始化欢迎消息
const initMessages = () => {
  if (messages.value.length) return
  messages.value.push(
    createMessage(
      'assistant',
      '你好呀，我是暖爪 AI 匹配助手 🐾 告诉我你的城市、居住空间和作息，我来帮你找合适的毛孩子。'
    )
  )
}

// 事件分发
const handleEvent = (event, message) => {
  const { event: name, data } = event

  switch (name) {
    case 'meta':
      if (data.session_id) {
        sessionId.value = data.session_id
        emit('session-created', data.session_id)
      }
      break

    case 'intent':
      message.thinking.intent = data.intent || ''
      break

    case 'retrieval':
      message.thinking.retrieval = data
      break

    case 'tool_start':
      message.thinking.tools.push({
        name: data.tool,
        args: data.args || {},
        status: 'running',
        summary: ''
      })
      break

    case 'tool_end': {
      const tool = [...message.thinking.tools]
        .reverse()
        .find((item) => item.name === data.tool && item.status === 'running')
      if (tool) {
        tool.status = 'done'
        tool.summary = data.result_summary || ''
      }
      break
    }

    case 'token':
      message.content += data.content || ''
      break

    case 'confirm':
      message.confirm = data
      message.status = 'waiting'
      break

    case 'done':
      if (message.status === 'streaming') message.status = 'done'
      break

    case 'error':
      message.status = 'error'
      message.error = data.message || 'AI 服务异常'
      break

    default:
      break
  }

  scrollToBottom()
}

// 发送消息
const handleSend = async (preset) => {
  const text = (typeof preset === 'string' ? preset : input.value).trim()
  if (!text || sending.value || hasPendingConfirm.value) return

  if (!sessionId.value) sessionId.value = createSessionId()

  input.value = ''

  messages.value.push({
    id: `m-${++messageSeq}`,
    role: 'user',
    content: text,
    status: 'done',
    error: '',
    confirm: null,
    thinking: { intent: '', retrieval: null, tools: [] }
  })

  // 关键：助手消息必须是 reactive 对象
  // 如果先 push 普通对象、再修改原对象，模板不会收到更新，
  // 表现就是“等全部生成完才一次性出现”，而不是逐字渲染。
  const assistant = reactive({
    id: `m-${++messageSeq}`,
    role: 'assistant',
    content: '',
    status: 'streaming',
    error: '',
    confirm: null,
    thinking: { intent: '', retrieval: null, tools: [] }
  })
  messages.value.push(assistant)

  sending.value = true
  controller.value = new AbortController()

  resetTimer(() => {
    controller.value?.abort()
    if (assistant.status === 'streaming') {
      assistant.status = 'error'
      assistant.error = '响应超时（60 秒），请重试或换一种问法'
    }
  })

  try {
    await chatStream({
      message: text,
      sessionId: sessionId.value,
      signal: controller.value.signal,
      onEvent: (event) => {
        resetTimer(() => {
          controller.value?.abort()
          if (assistant.status === 'streaming') {
            assistant.status = 'error'
            assistant.error = '响应超时（60 秒），请重试或换一种问法'
          }
        })
        handleEvent(event, assistant)
      }
    })

    if (assistant.status === 'streaming') assistant.status = 'done'
  } catch (error) {
    if (error.name === 'AbortError') {
      if (assistant.status !== 'error') {
        assistant.status = 'stopped'
        if (!assistant.content) assistant.content = '已停止生成。'
      }
    } else {
      assistant.status = 'error'
      assistant.error = error.message || '网络异常，请检查后端服务'
    }
  } finally {
    clearTimer()
    sending.value = false
    controller.value = null
    emitMessagesChange()
    scrollToBottom()
  }
}

// 二次确认
const handleConfirm = async (confirmed) => {
  const assistant = [...messages.value].reverse().find((item) => item.confirm)
  if (!assistant || sending.value) return

  assistant.confirm = null
  assistant.status = 'streaming'
  assistant.error = ''

  sending.value = true
  controller.value = new AbortController()

  resetTimer(() => {
    controller.value?.abort()
    if (assistant.status === 'streaming') {
      assistant.status = 'error'
      assistant.error = '响应超时（60 秒），请重试'
    }
  })

  try {
    await confirmStream({
      sessionId: sessionId.value,
      confirmed,
      signal: controller.value.signal,
      onEvent: (event) => {
        resetTimer(() => {
          controller.value?.abort()
          if (assistant.status === 'streaming') {
            assistant.status = 'error'
            assistant.error = '响应超时（60 秒），请重试'
          }
        })
        handleEvent(event, assistant)
      }
    })

    if (assistant.status === 'streaming') assistant.status = 'done'
  } catch (error) {
    if (error.name === 'AbortError') {
      if (assistant.status !== 'error') assistant.status = 'stopped'
    } else {
      assistant.status = 'error'
      assistant.error = error.message || '确认请求失败，请稍后重试'
    }
  } finally {
    clearTimer()
    sending.value = false
    controller.value = null
    emitMessagesChange()
    scrollToBottom()
  }
}

// 停止生成
const handleStop = () => {
  controller.value?.abort()
}

// 新对话：中止当前请求并重置会话
const handleReset = () => {
  controller.value?.abort()
  controller.value = null
  sending.value = false
  clearTimer()
  input.value = ''
  messages.value = []
  messageSeq = 0
  sessionId.value = createSessionId()
  initMessages()
  scrollToBottom()
  emit('new-session')
}

/** 切换到某个历史会话：清空当前对话并载入历史消息 */
const loadMessages = (list = [], key = '') => {
  controller.value?.abort()
  controller.value = null
  sending.value = false
  clearTimer()
  input.value = ''
  messageSeq = 0
  sessionId.value = key || createSessionId()

  messages.value = (list || [])
    .filter((item) => item && item.content)
    .map((item) => createMessage(item.role, item.content))

  if (!messages.value.length) {
    initMessages()
  }

  scrollToBottom()
}

/** 导出可序列化的消息，供父组件写入历史 */
const getMessages = () =>
  messages.value.map(({ role, content }) => ({ role, content }))

/** 每轮结束通知父组件保存 */
const emitMessagesChange = () => {
  emit('messages-change', getMessages())
}

onMounted(() => {
  initMessages()
  scrollToBottom()
})

// 供智能匹配页调用：发送消息、切换历史会话、读取当前消息
defineExpose({
  sendMessage: (text) => handleSend(text),
  loadMessages,
  getMessages
})
</script>

<style scoped>
.ai-shell {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  border-radius: 16px;
  border: 1px solid var(--border, #eaedf3);
  background: var(--bg-page, #f6f7fb);
}

/* 头部 */
.ai-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: #ffffff;
  border-bottom: 1px solid var(--border, #eaedf3);
  flex: none;
}

.ai-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ai-avatar {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  font-size: 20px;
  color: #fff;
  background: linear-gradient(135deg, #ff9a6c, #ff6b4a);
  box-shadow: 0 6px 14px rgba(255, 107, 74, 0.3);
}

.ai-brand-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ai-brand-text strong {
  font-size: 14px;
  color: var(--text-main, #1f2937);
}

.ai-brand-text span {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: var(--text-sub, #8892a0);
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #22c55e;
}

.dot.is-busy {
  background: #f59e0b;
  animation: pulse 1s ease-in-out infinite;
}

/* 消息区 */
.ai-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 16px 14px 8px;
  scroll-behavior: smooth;
}

.message-row {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.message-row.user {
  justify-content: flex-end;
}

.bubble-avatar {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 9px;
  font-size: 14px;
  background: var(--brand-weak, #fff1ec);
  flex: none;
  margin-top: 2px;
}

.message-main {
  max-width: 86%;
  min-width: 0;
}

.message-row.user .message-main {
  max-width: 80%;
}

.bubble {
  padding: 10px 13px;
  border-radius: 12px;
  background: #ffffff;
  border: 1px solid var(--border, #eaedf3);
  font-size: 13px;
  line-height: 1.8;
  color: var(--text-body, #4b5563);
  white-space: pre-wrap;
  word-break: break-word;
}

.message-row.user .bubble {
  background: linear-gradient(135deg, #ff9a6c, #ff6b4a);
  border-color: transparent;
  color: #ffffff;
}

.bubble.is-error {
  border-color: #fecaca;
  background: #fff5f5;
  color: #b91c1c;
}

.caret {
  display: inline-block;
  margin-left: 1px;
  color: var(--brand, #ff7a59);
  animation: blink 0.9s steps(1) infinite;
}

.typing {
  display: flex;
  gap: 4px;
  padding: 13px;
}

.typing span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ffb59f;
  animation: bounce 1.2s infinite;
}

.typing span:nth-child(2) {
  animation-delay: 0.15s;
}

.typing span:nth-child(3) {
  animation-delay: 0.3s;
}

/* 思考过程 */
.thinking {
  margin-bottom: 8px;
  border: 1px dashed #ffd8cc;
  border-radius: 10px;
  background: #fffaf7;
  overflow: hidden;
}

.thinking :deep(.el-collapse-item__header) {
  height: 34px;
  padding: 0 10px;
  background: transparent;
  border-bottom: none;
  font-size: 12px;
  color: var(--text-sub, #8892a0);
}

.thinking :deep(.el-collapse-item__wrap) {
  background: transparent;
  border-bottom: none;
}

.thinking :deep(.el-collapse-item__content) {
  padding: 0 12px 10px;
  font-size: 12px;
}

.thinking-title {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--brand-dark, #ef5b3a);
}

.thinking-row {
  display: flex;
  gap: 8px;
  margin-top: 6px;
}

.thinking-label {
  flex: none;
  width: 32px;
  color: var(--text-muted, #b3bbc8);
}

.thinking-content {
  flex: 1;
  min-width: 0;
}

.retrieval-query {
  margin: 0 0 4px;
  color: var(--text-body, #4b5563);
}

.source-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.source-list li {
  padding: 6px 8px;
  border-radius: 8px;
  background: #ffffff;
  border: 1px solid #ffe6dc;
}

.source-title {
  font-weight: 600;
  color: var(--text-main, #1f2937);
}

.source-score {
  margin-left: 6px;
  font-size: 10px;
  color: #22c55e;
}

.source-snippet {
  margin: 3px 0 0;
  font-size: 11px;
  line-height: 1.6;
  color: var(--text-sub, #8892a0);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.source-empty {
  margin: 0;
  font-size: 11px;
  color: #b45309;
}

/* 工具卡片 */
.tool-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 8px;
}

.tool-card {
  padding: 9px 11px;
  border-radius: 10px;
  background: #ffffff;
  border: 1px solid var(--border, #eaedf3);
}

.tool-head {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tool-icon {
  font-size: 13px;
}

.tool-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-main, #1f2937);
}

.tool-status {
  margin-left: auto;
  color: #f59e0b;
}

.tool-status.is-done {
  color: #22c55e;
}

.tool-args {
  margin: 4px 0 0;
  font-size: 11px;
  color: var(--text-sub, #8892a0);
  word-break: break-all;
}

.tool-summary {
  margin: 4px 0 0;
  font-size: 11px;
  color: #15803d;
}

/* 错误提示 */
.error-tip {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 6px;
  font-size: 11px;
  color: #b91c1c;
}

/* 二次确认 */
.confirm-card {
  margin-top: 8px;
  padding: 12px 14px;
  border-radius: 12px;
  background: #fffaf7;
  border: 1px solid #ffd2c4;
}

.confirm-title {
  margin: 0 0 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main, #1f2937);
}

.confirm-meta,
.confirm-reason {
  margin: 0 0 6px;
  font-size: 11px;
  line-height: 1.7;
  color: var(--text-sub, #8892a0);
  word-break: break-word;
}

.confirm-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

/* 快捷问题 */
.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 4px 4px 12px 36px;
}

.suggestions-label {
  width: 100%;
  font-size: 11px;
  color: var(--text-muted, #b3bbc8);
}

.suggestion-chip {
  padding: 6px 11px;
  border-radius: 999px;
  border: 1px solid #ffd2c4;
  background: #ffffff;
  font-size: 12px;
  color: var(--brand-dark, #ef5b3a);
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-chip:hover {
  background: var(--brand-weak, #fff1ec);
  border-color: var(--brand, #ff7a59);
}

/* 输入区 */
.ai-composer {
  flex: none;
  padding: 10px 14px 12px;
  background: #ffffff;
  border-top: 1px solid var(--border, #eaedf3);
}

.ai-composer :deep(.el-textarea__inner) {
  border-radius: 10px;
  background: var(--bg-page, #f6f7fb);
  box-shadow: none;
  border: 1px solid transparent;
  font-size: 13px;
  resize: none;
}

.ai-composer :deep(.el-textarea__inner:focus) {
  background: #ffffff;
  border-color: var(--brand, #ff7a59);
  box-shadow: 0 0 0 3px rgba(255, 122, 89, 0.12);
}

.composer-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

.composer-tip {
  margin-right: auto;
  font-size: 10px;
  color: var(--text-muted, #b3bbc8);
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}

@keyframes bounce {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  30% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

@keyframes pulse {
  50% {
    opacity: 0.4;
  }
}

@media (prefers-reduced-motion: reduce) {
  .caret,
  .typing span,
  .dot.is-busy {
    animation: none;
  }
}
</style>