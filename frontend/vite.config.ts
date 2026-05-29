import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import UnoCSS from 'unocss/vite'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { NaiveUiResolver } from 'unplugin-vue-components/resolvers'
import { live2dTexturePlugin } from './vite-plugin-live2d-texture'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiBase = env.VITE_API_BASE_URL ?? 'http://localhost:8000'

  return {
    plugins: [
      vue(),
      UnoCSS(),
      live2dTexturePlugin(),
      AutoImport({
        imports: ['vue', 'vue-router', 'pinia', '@vueuse/core'],
        dts: 'src/types/auto-imports.d.ts',
        eslintrc: { enabled: true },
      }),
      Components({
        resolvers: [NaiveUiResolver()],
        dts: 'src/types/components.d.ts',
      }),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      host: '127.0.0.1',
      port: 5173,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Cross-Origin-Resource-Policy': 'cross-origin',
      },
      proxy: {
        '/api': {
          target: apiBase,
          changeOrigin: true,
        },
        '/health': {
          target: apiBase,
          changeOrigin: true,
        },
      },
    },
  }
})
