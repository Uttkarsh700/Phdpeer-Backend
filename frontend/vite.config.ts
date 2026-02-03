import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '')

  // Get proxy target from environment variable, fallback to default
  const proxyTarget = env.VITE_DEV_SERVER_PROXY_TARGET || 'http://localhost:8000'
  const devPort = parseInt(env.VITE_DEV_SERVER_PORT || '3000', 10)

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      port: devPort,
      proxy: {
        '/api': {
          target: proxyTarget,
          changeOrigin: true,
          // Only proxy in development
          configure: (proxy, _options) => {
            if (mode === 'production') {
              console.warn('⚠️  Proxy is disabled in production mode')
            }
          },
        },
      },
    },
    build: {
      outDir: 'dist',
      sourcemap: true,
    },
  }
})
