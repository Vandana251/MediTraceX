import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: 'https://meditracex-backend.onrender.com',
        changeOrigin: true,
        secure: true,
      },
      '/health': {
        target: 'https://meditracex-backend.onrender.com',
        changeOrigin: true,
        secure: true,
      },
    },
  },
})
