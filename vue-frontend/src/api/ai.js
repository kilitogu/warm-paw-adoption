import { getToken } from '@/utils/auth'

// 与 request.js 保持一致的基地址策略：走 Vite 代理时为空字符串
const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

/**
 * 解析单个 SSE 事件块
 * 兼容 event: / event: 两种写法与多行 data:
 */
function parseEventBlock(block) {
  const lines = block.split('\n')
  let event = 'message'
  const dataLines = []

  for (const line of lines) {
    const text = line.replace(/\r$/, '')
    if (!text || text.startsWith(':')) continue

    if (text.startsWith('event:')) {
      event = text.slice(6).trim()
    } else if (text.startsWith('data:')) {
      dataLines.push(text.slice(5).replace(/^ /, ''))
    }
  }

  if (!dataLines.length) return null

  const raw = dataLines.join('\n')
  let data
  try {
    data = JSON.parse(raw)
  } catch (error) {
    data = { raw }
  }

  return { event, data }
}

/**
 * 通用流式请求
 * 使用 fetch + ReadableStream，避免 EventSource 无法携带 POST body 与 Authorization
 */
async function streamRequest(url, payload, { onEvent, signal } = {}) {
  const token = getToken()

  const response = await fetch(`${BASE_URL}${url}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: JSON.stringify(payload),
    signal
  })

  if (response.status === 401) {
    throw new Error('登录状态已失效，请重新登录')
  }

  if (!response.ok) {
    const text = await response.text().catch(() => '')
    throw new Error(text || `请求失败（HTTP ${response.status}）`)
  }

  if (!response.body) {
    throw new Error('当前浏览器不支持流式响应')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  const dispatch = (block) => {
    const parsed = parseEventBlock(block)
    if (parsed && typeof onEvent === 'function') {
      onEvent(parsed)
    }
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const blocks = buffer.split(/\r?\n\r?\n/)
    buffer = blocks.pop() || ''

    for (const block of blocks) {
      dispatch(block)
    }
  }

  buffer += decoder.decode()
  if (buffer.trim()) {
    dispatch(buffer)
  }
}

/**
 * 发起对话
 * @param {Object} options { message, sessionId, onEvent, signal }
 */
export function chatStream({ message, sessionId, onEvent, signal }) {
  return streamRequest(
    '/api/ai/chat',
    { message, session_id: sessionId },
    { onEvent, signal }
  )
}

/**
 * 提交二次确认结果
 * @param {Object} options { sessionId, confirmed, onEvent, signal }
 */
export function confirmStream({ sessionId, confirmed, onEvent, signal }) {
  return streamRequest(
    '/api/ai/confirm',
    { session_id: sessionId, confirmed },
    { onEvent, signal }
  )
}