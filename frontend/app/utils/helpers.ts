// frontend/app/utils/helpers.ts
export const USD_TO_KHR_RATE = 4000

export function formatCurrency(amount: number | null | undefined, currency = 'USD') {
  const a = Number(amount ?? 0)
  currency = (currency || 'USD').toUpperCase()
  if (currency === 'KHR') {
    // KHR often displayed without currency symbol; show number with 2 decimals
    return new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(a)
  }
  // USD and fallback
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(a)
}

export const convertToUSD = (khr?: number | null): number => {
  if (!khr) return 0
  return khr / USD_TO_KHR_RATE
}

export const convertToKHR = (usd?: number | null): number => {
  if (!usd) return 0
  return usd * USD_TO_KHR_RATE
}

export const formatDate = (dateStr?: string | Date): string => {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

export function formatUserDate(isoString?: string, options?: Intl.DateTimeFormatOptions) {
  if (!isoString) return '—'
  const date = new Date(isoString)
  return date.toLocaleString(undefined, options || {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

// Get user's current local time (used for dashboard greeting)
export function getCurrentUserTime() {
  const now = new Date()
  return now.toLocaleString(undefined, {
    dateStyle: 'full',
    timeStyle: 'medium',
  })
}

// Simple greeting based on local hour
export function getGreeting() {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good afternoon'
  return 'Good evening'
}
export function convertAmount(amount: number | null | undefined, fromCurrency = 'USD', toCurrency = 'USD', usdToKhrRate = USD_TO_KHR_RATE) {
  const a = Number(amount ?? 0)
  const from = (fromCurrency || 'USD').toUpperCase()
  const to = (toCurrency || 'USD').toUpperCase()
  const rate = Number(usdToKhrRate || USD_TO_KHR_RATE)

  if (from === to) return a
  if (from === 'USD' && to === 'KHR') return a * rate
  if (from === 'KHR' && to === 'USD') return a / rate
  // fallback: no conversion
  return a
}