import { defineConfig } from 'vite'
export default defineConfig({
  server: { port: 4173, host: '0.0.0.0', proxy: { '/api': { target: 'http://127.0.0.1:8123', changeOrigin: true } } },
  build: { outDir: 'dist', sourcemap: false, chunkSizeWarningLimit: 750 }
})