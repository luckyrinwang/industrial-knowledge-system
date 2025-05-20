import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

// 从环境变量获取端口，或使用默认值
const frontendPort = process.env.FRONTEND_PORT || 3000;
const backendPort = process.env.BACKEND_PORT || 5000;
const backendUrl = process.env.BACKEND_URL || `http://localhost:${backendPort}`;

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    host: '0.0.0.0',
    port: frontendPort,
    proxy: {
      '/api': {
        target: backendUrl,
        changeOrigin: true
      },
      '/files': {
        target: backendUrl,
        changeOrigin: true
      },
      '/uploads': {
        target: backendUrl,
        changeOrigin: true
      }
    }
  }
}); 