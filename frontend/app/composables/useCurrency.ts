// frontend/app/composables/useCurrency.ts
export const useCurrency = () => {
  const format = (amount: number | string | null | undefined, currency = 'USD') => {
    if (amount === null || amount === undefined || amount === '') return '—'

    const n = typeof amount === 'number' ? amount : Number(String(amount).replace(/,/g, ''))
    if (Number.isNaN(n)) return String(amount)

    if (currency === 'USD') {
      return `$${n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    }

    if (currency === 'KHR' || currency === 'RIEL' || currency === '៛') {
      const intVal = Math.round(n)
      return `${intVal.toLocaleString(undefined)} ៛`
    }
    return `${n.toLocaleString(undefined)} ${currency}`
  }

  return { format }
}
