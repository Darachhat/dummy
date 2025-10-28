// frontend/plugins/api.ts
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const base = config.public.apiBase
  const token = useState<string | null>('token', () => null)

  const $api = async (path: string, opts: any = {}) => {
    opts.headers = opts.headers || {}
    if (token.value) {
      opts.headers.Authorization = `Bearer ${token.value}`
    }
    try {
      return await $fetch(base + path, opts)
    } catch (e: any) {
      console.error('API error:', e)
      throw e
    }
  }

  return { provide: { api: $api, token } }
})
