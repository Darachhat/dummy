// composables/useLogoUrl.ts
export function useLogoUrl() {
  const config = useRuntimeConfig()
  const base = (config.public.apiBase || '') as string

  function getLogoUrl(
    path?: string | null,
    fallback: string = '/static/logos/default.svg'
  ) {
    if (!path) return `${base}${fallback}`
    return path.startsWith('http') ? path : `${base}${path}`
  }

  return { getLogoUrl }
}
