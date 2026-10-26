/**
 * 历史会话本地存储
 * 作用: 保存会话列表、标题、消息，供智能匹配页左侧历史区域使用
 * 说明: 当前用 localStorage，后续可把读写替换成 /api/ai/sessions 接口
 */
const STORAGE_KEY = 'warm-paw-chat-sessions'
const MAX_SESSIONS = 30

/** 读取全部会话，按更新时间倒序 */
export function loadSessions() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    const list = raw ? JSON.parse(raw) : []
    if (!Array.isArray(list)) return []
    return list.sort((a, b) => (b.updatedAt || 0) - (a.updatedAt || 0))
  } catch (error) {
    console.warn('读取历史会话失败:', error)
    return []
  }
}

/** 保存会话列表，最多保留 30 条 */
export function saveSessions(sessions) {
  const trimmed = [...sessions]
    .sort((a, b) => (b.updatedAt || 0) - (a.updatedAt || 0))
    .slice(0, MAX_SESSIONS)

  localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed))
  return trimmed
}

/** 生成会话 ID */
function createId(prefix) {
  if (window.crypto?.randomUUID) return window.crypto.randomUUID()
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`
}

/** 新建一个空会话 */
export function createSession() {
  const now = Date.now()
  return {
    id: createId('session'),
    // 后端 SSE 使用的 session_id，与前端列表 id 分开
    sessionKey: createId('chat'),
    title: '新对话',
    messages: [],
    createdAt: now,
    updatedAt: now
  }
}

/** 用第一条用户消息生成标题 */
export function buildTitle(messages) {
  const firstUser = (messages || []).find((item) => item.role === 'user')
  if (!firstUser) return '新对话'

  const text = String(firstUser.content || '').replace(/\s+/g, ' ').trim()
  if (!text) return '新对话'
  return text.length > 18 ? `${text.slice(0, 18)}…` : text
}

/** 取最后一条消息做预览 */
export function buildPreview(messages) {
  const last = (messages || []).filter((item) => item.content).slice(-1)[0]
  if (!last) return '还没有对话'

  const text = String(last.content).replace(/\s+/g, ' ').trim()
  return text.length > 28 ? `${text.slice(0, 28)}…` : text
}
