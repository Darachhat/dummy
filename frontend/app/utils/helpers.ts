export const getLogoUrl = (path?: string, base?: string) => {
  if (!path) return `${base}/static/logos/default.svg`
  if (path.startsWith('http')) return path
  return `${base}${path}`
}

export const formatCurrency = (cents?: number | null, currency = 'USD') => {
  if (!cents) return '—'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency
  }).format(cents / 100)
}

export const formatDate = (iso?: string) => {
  if (!iso) return '—'
  return new Date(iso).toLocaleString()
}
