# 暖爪 · 智能宠物领养平台（前端）

Vue3 + Vite + Element Plus 实现的管理端 / 用户端界面，包含首页、宠物列表与详情、
领养指南、账号设置以及 AI 智能匹配对话页。

## 启动

```bash
npm install
npm run dev
```

默认访问 `http://127.0.0.1:5173`，`vite.config.js` 已把 `/api` 与 `/uploads`
代理到 `http://127.0.0.1:8080`，因此本地开发无需配置跨域。

## 构建

```bash
npm run build
npm run preview
```

## 目录说明

```text
src/
  api/         # 按业务拆分的接口封装
  assets/      # 全局样式
  components/  # AiChat、ChatHistory、PetCard、FlowSteps、StatBoard 等
  hooks/       # usePetList 等组合式函数
  router/      # 路由与登录守卫
  utils/       # axios 实例、token 存取、历史会话本地存储
  views/       # 页面级组件
```

AI 对话使用 `fetch + ReadableStream` 消费 SSE，因为 `EventSource` 无法携带
`Authorization` 请求头与 POST 请求体；相关实现见 `src/api/ai.js`。

## 环境变量

参考 `.env.example`，通常保持 `VITE_API_BASE_URL` 为空即可。
