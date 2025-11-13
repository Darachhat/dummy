// frontend\app\plugins\api.ts
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const base = config.public.apiBase

  // Keep token reactive and persistent across page reloads
  const token = useState<string | null>('token', () => {
    if (process.client) {
      return localStorage.getItem('token')
    }
    return null
  })

  // Keep localStorage in sync with reactive token
  if (process.client) {
    watch(token, (val) => {
      if (val) localStorage.setItem('token', val)
      else localStorage.removeItem('token')
    })
  }

  // Main API handler
  const $api = async (path: string, opts: any = {}) => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(opts.headers || {}),
    }

    // Attach token if available
    if (token.value) {
      headers['Authorization'] = `Bearer ${token.value}`
    }

    const options = {
      method: opts.method || 'GET',
      headers,
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    }

    try {
      // Ensure consistent path structure
      const url = path.startsWith('http') ? path : `${base}${path}`
      return await $fetch(url, options)
    } catch (e: any) {
      const status = e?.response?.status

      // Handle unauthorized → redirect to login
      if (status === 401) {
        if (process.client) {
          localStorage.removeItem('token')
          token.value = null
          navigateTo('/login')
        }
      }

      // Optional: handle 403 Forbidden (for admin pages)
      if (status === 403 && process.client) {
        console.warn('Access denied — admin only')
        navigateTo('/')
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
