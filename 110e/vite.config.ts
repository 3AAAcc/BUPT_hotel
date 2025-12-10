// @ts-nocheck
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3002,
    host: '0.0.0.0', // 允许局域网访问
    proxy: {
      '/api': {
        // 后端服务端口 8000
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        // 去掉前缀 /api，直接透传给后端
        rewrite: (path: string) => path.replace(/^\/api/, '')
      }
    }
  }
})
