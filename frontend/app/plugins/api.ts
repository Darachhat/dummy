// frontend/plugins/api.ts
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const base =config.public.apiBase ||process.env.NUXT_PUBLIC_API_BASE

  // Restore token from localStorage on startup
  const token = useState<string | null>('token', () => {
    if (process.client) {
      return localStorage.getItem('token')
    }
    return null
  })

  // Watch for token changes
  if (process.client) {
    watch(token, (val) => {
      if (val) localStorage.setItem('token', val)
      else localStorage.removeItem('token')
    })
  }

  const $api = async (path: string, opts: any = {}) => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(opts.headers || {}),
    }

    if (token.value) {
      headers['Authorization'] = `Bearer ${token.value}`
    }

    const options = {
      method: opts.method || 'GET',
      headers,
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    }

    try {
      return await $fetch(`${base}${path}`, options)
    } catch (e: any) {
      if (e?.response?.status === 401) {
        localStorage.removeItem('token')
        token.value = null
        navigateTo('/login')
      }
      throw e
    }
  }

  return {
    provide: {
      api: $api,
      token,
    },
  }
})
