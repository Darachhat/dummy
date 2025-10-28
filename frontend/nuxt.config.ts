// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  ssr: false,

  app: {
    head: {
      title: 'Dummy Bank',
      meta: [{ name: 'viewport', content: 'width=device-width, initial-scale=1' }]
    }
  },

  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8000'
    }
  },

  modules: ['@nuxtjs/tailwindcss']
})