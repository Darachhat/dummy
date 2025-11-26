// frontend/app/plugins/api.ts  (patch - replace $api implementation)
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const base = config.public.apiBase

  const token = useState<string | null>('token', () => {
    if (process.client) return localStorage.getItem('token')
    return null
  })

  // GLOBAL loading state + concurrent counter
  const globalLoadingCounter = useState<number>('globalLoadingCounter', () => 0)
  const globalLoading = useState<boolean>('globalLoading', () => false)

  function incLoading() {
    globalLoadingCounter.value = (globalLoadingCounter.value || 0) + 1
    globalLoading.value = globalLoadingCounter.value > 0
  }
  function decLoading() {
    globalLoadingCounter.value = Math.max(0, (globalLoadingCounter.value || 0) - 1)
    globalLoading.value = globalLoadingCounter.value > 0
  }

  const $api = async (path: string, opts: any = {}) => {
    const body = opts.body
    const isFormData =
      typeof FormData !== 'undefined' && body instanceof FormData

    const headers: Record<string, string> = {
      ...(opts.headers || {}),
    }

    if (!isFormData && body !== undefined && body !== null) {
      headers['Content-Type'] = 'application/json'
    }

    if (token.value) {
      headers['Authorization'] = `Bearer ${token.value}`
    }

    const options: any = {
      method: opts.method || 'GET',
      headers,
    }

    if (body !== undefined) {
      options.body = isFormData ? body : body
    }

    // Start global loading for every request except when caller opts out
    const skipGlobal = !!opts.skipGlobalLoading
    if (!skipGlobal) incLoading()

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
    } finally {
      if (!skipGlobal) decLoading()
    }
  }

  return {
    provide: {
      api: $api,
      token,
      // expose global loading if needed elsewhere
      globalLoading,
    },
  }
})
