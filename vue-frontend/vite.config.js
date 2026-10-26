import {fileURLToPath, URL} from 'node:url'

import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// 开发与预览共用的反向代理配置
const proxy = {
    // API 接口代理
    '/api': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true
    },
    // 静态文件代理（头像、宠物图片）
    '/uploads': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true
    }
}

// https://vite.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        vueDevTools(),
    ],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url)),
        }
    },
    server: {
        proxy
    },
    preview: {
        port: 4173,
        proxy
    }
})
