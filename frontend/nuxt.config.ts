// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  ssr: false,
  css: [
    '~/assets/css/global.css',
  ],

  app: {
    head: {
      title: 'Dummy Bank',
      meta: [{ name: 'viewport', content: 'width=device-width, initial-scale=1' }]
    }
  },
  ui: {
    global: true,
    theme: {
      colors: {
        background: '#ffffff',  
        primary: '#0f172a',      
        muted: '#f9fafb',        
        border: '#e5e7eb',      
      },
      radius: 'md',
      font: 'sans',
    },
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
    }
  },

  modules: [
    '@nuxt/ui',
  ],

  build: {
    transpile: ['@tanstack/vue-table'],
  },
})