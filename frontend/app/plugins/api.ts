// frontend/plugins/api.ts
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const base = config.public.apiBase
  const token = useState<string | null>('token', () => {
    // 🔁 Restore token from localStorage on load
    if (process.client) {
      return localStorage.getItem('token')
    }
    return null
  })

  // 🔒 Watch token and persist it
  if (process.client) {
    watch(token, (val) => {
      if (val) localStorage.setItem('token', val)
      else localStorage.removeItem('token')
    })
  }

  const $api = async (path: string, opts: any = {}) => {
    opts.headers = opts.headers || {}
    if (token.value) {
      opts.headers.Authorization = `Bearer ${token.value}`
    }
    try {
  return await $fetch(base + path, opts)
} catch (e: any) {
  if (e.response?.status === 401) {
    localStorage.removeItem('token')
    navigateTo('/login')
  }
  throw e
}

  }

  return { provide: { api: $api, token } }
})
