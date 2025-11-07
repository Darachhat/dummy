export const USD_TO_KHR_RATE = 4000

export const formatCurrency = (n?: number | null, currency = ''): string => {
  if (n === null || n === undefined) return '—'
  return `${currency ? currency + ' ' : ''}${n.toLocaleString(undefined, {
    minimumFractionDigits: 2,
  })}`
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