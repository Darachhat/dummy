// frontend/app/plugins/api.ts
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

  const $api = async (path: string, opts: any = {}) => {
    const body = opts.body
    const isFormData =
      typeof FormData !== 'undefined' && body instanceof FormData

    const headers: Record<string, string> = {
      ...(opts.headers || {}),
    }

    // ONLY set JSON content-type when not sending FormData
    if (!isFormData && body !== undefined && body !== null) {
      headers['Content-Type'] = 'application/json'
    }

    // Attach token if available
    if (token.value) {
      headers['Authorization'] = `Bearer ${token.value}`
    }

    const options: any = {
      method: opts.method || 'GET',
      headers,
    }

    // Let $fetch handle encoding: object -> JSON, FormData -> multipart
    if (body !== undefined) {
      options.body = isFormData ? body : body
    }

    try {
      const url = path.startsWith('http') ? path : `${base}${path}`
      return await $fetch(url, options)
    } catch (e: any) {
      const status = e?.response?.status

      if (status === 401) {
        if (process.client) {
          localStorage.removeItem('token')
          token.value = null
          navigateTo('/login')
        }
      }

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
