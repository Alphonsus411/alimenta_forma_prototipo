import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: './tests/frontend/setup.js',
    include: ['tests/frontend/**/*.test.{js,jsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      reportsDirectory: 'coverage',
      thresholds: {
        statements: 90,
        branches: 70,
        functions: 80,
        lines: 90,
      },
    },
  },
})
