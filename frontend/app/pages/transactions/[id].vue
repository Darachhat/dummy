<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
    <!-- Header -->
    <div class="relative flex items-center justify-center w-full max-w-lg mb-8">
      <button
        @click="navigateTo('/transactions')"
        class="absolute left-4 p-2 bg-white rounded-full shadow hover:bg-gray-100 transition"
      >
        <ArrowLeft class="w-5 h-5 text-gray-700" />
      </button>
      <h2 class="text-xl font-semibold text-gray-800 text-center">Transaction Detail</h2>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-gray-500 mt-10">Loading transaction details...</div>

    <!-- Transaction Detail Card -->
    <div
      v-else-if="transaction"
      class="bg-white rounded-2xl shadow border border-gray-100 w-full max-w-lg p-6 space-y-5"
    >
      <!-- Service Info -->
      <div class="flex flex-col items-center text-center mb-4">
        <img
          v-if="transaction.service?.logo_url"
          :src="getLogoUrl(transaction.service.logo_url)"
          alt="Service Logo"
          class="w-16 h-16 rounded-full object-contain mb-3"
        />
        <h3 class="text-lg font-semibold text-gray-800">
          {{ transaction.service?.name || 'Transaction' }}
        </h3>
        <p class="text-sm text-gray-500">
          Ref: {{ transaction.reference_number || '—' }}
        </p>
      </div>

      <div class="border-t border-gray-200"></div>

      <!-- Transaction Details -->
      <div class="text-sm text-gray-700 space-y-3 mt-3">
        <div class="flex justify-between">
          <span class="text-gray-500">Customer Name</span>
          <span class="font-medium text-right">{{ transaction.customer_name || '—' }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Account</span>
          <span class="font-medium text-right">
            {{ transaction.account?.number || '—' }}
            <span v-if="transaction.account?.name" class="text-gray-500 text-xs">
              — {{ transaction.account.name }}
            </span>
          </span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Description</span>
          <span class="font-medium text-right">{{ transaction.description || '—' }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Amount</span>
          <span
            class="font-semibold"
            :class="transaction.direction === 'debit' ? 'text-red-600' : 'text-green-600'"
          >
            {{ transaction.direction === 'debit' ? '-' : '+' }}
            {{ formatCurrency(transaction.amount) }}
          </span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Currency</span>
          <span class="font-medium">{{ transaction.currency }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Date</span>
          <span class="font-medium">{{ formatDate(transaction.created_at) }}</span>
        </div>
      </div>

      <div class="border-t border-gray-200 my-3"></div>

      <!-- Actions -->
      <div class="flex flex-col md:flex-row justify-center gap-3">
        <button
          @click="goToAccount(transaction.account?.id)"
          class="flex-1 py-2 bg-gradient-to-r from-gray-800 to-gray-900 text-white rounded-lg hover:opacity-90 transition"
        >
          View Account
        </button>

        <button
          @click="navigateTo('/transactions')"
          class="flex-1 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition"
        >
          Back to History
        </button>
      </div>
    </div>

    <!-- Error -->
    <div v-else class="text-red-600 mt-10">
      Failed to load transaction details.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowLeft } from 'lucide-vue-next'

const { $api } = useNuxtApp()
const route = useRoute()
const transaction = ref<any>(null)
const loading = ref(true)
const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase

onMounted(async () => {
  loading.value = true
  try {
    const rawParam = route.params.id       
    const numericId = Number(rawParam)    
    const me = await $api('/me')
    const accounts = me.accounts || []
    let found = null

    const normalizeTx = (raw: any) => {
      if (!raw) return null
      const serviceName = raw.service?.name ?? raw.service_name ?? raw.payment?.service?.name ?? null
      const serviceLogo = raw.service?.logo_url ?? raw.service_logo_url ?? raw.payment?.service?.logo_url ?? null
      const accountObj = raw.account ?? (raw.account_id ? { id: raw.account_id, number: raw.account_number ?? raw.number, name: raw.account_name ?? null } : null)
      return { ...raw, service: { name: serviceName, logo_url: serviceLogo }, account: accountObj }
    }
    if (!Number.isNaN(numericId) && accounts.length > 0) {
      for (const acc of accounts) {
        try {
          const tx = await $api(`/accounts/${acc.id}/transactions/${numericId}`)
          if (tx) {
            found = normalizeTx(tx)
            console.log('Found transaction by numeric id on account', acc.id, found)
            break
          }
        } catch (err: any) {
          if (err?.response?.status !== 404) console.error(`Error on account ${acc.id} numeric lookup`, err)
        }
      }
    }
    if (!found) {
      const tid = String(rawParam)
      for (const acc of accounts) {
        try {
          const accountTxs = await $api(`/accounts/${acc.id}/transactions`)
          if (Array.isArray(accountTxs) && accountTxs.length) {
            const match = accountTxs.find((x: any) => x.transaction_id === tid || x.reference_number === tid)
            if (match) {
              found = normalizeTx(match)
              found.account = found.account ?? { id: acc.id, number: acc.number ?? acc.account_number, name: acc.name ?? acc.account_name }
              console.log('Found transaction by tid in account', acc.id, found)
              break
            }
          }
        } catch (err: any) {
          if (err?.response?.status !== 404) console.error(`Error fetching transactions for account ${acc.id}`, err)
        }
      }
    }
    if (!found && !Number.isNaN(numericId)) {
      try {
        const globalTx = await $api(`/transactions/${numericId}`)
        if (globalTx) {
          found = normalizeTx(globalTx)
          console.log('Found via global transactions route', found)
        }
      } catch (err: any) {
        if (err?.response?.status !== 404) console.error('Error fetching global transaction', err)
      }
    }

    transaction.value = found
    if (!found) console.warn('Transaction not found for param', rawParam)
  } catch (err) {
    console.error('Failed to load transaction details:', err)
  } finally {
    loading.value = false
  }
})


const getLogoUrl = (path: string) => {
  if (!path) return `${BACKEND_URL}/static/logos/default.svg`
  if (path.startsWith('http')) return path
  return `${BACKEND_URL}${path}`
}

const formatCurrency = (amount?: number | null) => {
  if (!amount) return '—'
  return `$${Number(amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}`
}

const formatDate = (iso?: string) => {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleString()
}

const goToAccount = (accountId?: number) => {
  if (accountId) navigateTo(`/accounts/${accountId}`)
  else navigateTo('/accounts')
}
</script>
