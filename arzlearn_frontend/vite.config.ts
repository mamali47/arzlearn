import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
  },
  build: {
    // مرورگرهای هدف: هرچه جدیدتر، خروجی کوچک‌تر و سریع‌تر.
    target: 'es2020',
    cssCodeSplit: true,
    sourcemap: false,
    // هشدار حجم را روی عددی می‌گذاریم که واقعاً معنادار باشد
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        /**
         * جدا کردن کتابخانه‌های ثابت از کد خودمان.
         *
         * چرا برای سئو مهم است: این فایل‌ها هش ثابتی می‌گیرند و بین
         * دیپلوی‌ها عوض نمی‌شوند، پس کاربر برگشتی دوباره دانلودشان نمی‌کند
         * و LCP صفحات بعدی خیلی سریع‌تر می‌شود.
         */
        manualChunks: {
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-http': ['axios'],
        },
      },
    },
  },
})
