<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center py-10 px-4">
    <!-- Header -->
    <div class="flex items-center w-full max-w-md mb-6">
      <button
        @click="navigateTo('/transactions')"
        class="p-2 bg-white rounded-full shadow hover:bg-gray-50"
      >
        <ArrowLeft class="w-5 h-5 text-gray-600" />
      </button>
      <h2 class="text-lg font-semibold text-gray-700 mx-20 px-4">Transaction Detail</h2>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-gray-500 mt-10">Loading transaction details...</div>

    <!-- Transaction Card -->
    <div
      v-else-if="transaction"
      class="bg-white rounded-2xl shadow w-full max-w-md p-6 space-y-4"
    >
      <!-- Logo -->
      <div class="flex items-center justify-center mb-2">
        <img
          v-if="transaction.service?.logo_url"
          :src="getLogoUrl(transaction.service.logo_url)"
          alt="Service Logo"
          class="w-16 h-16 object-contain rounded-full"
        />
      </div>

      <h3 class="text-lg font-semibold text-gray-800 text-center">
        {{ transaction.service?.name || 'Transaction' }}
      </h3>

      <div class="border-t border-gray-200 my-3"></div>

      <div class="text-sm text-gray-700 space-y-2">
        <div class="flex justify-between">
          <span class="text-gray-500">Reference No.</span>
          <span class="font-medium">{{ transaction.reference_number || '—' }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Customer Name</span>
          <span class="font-medium">{{ transaction.customer_name || '—' }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Description</span>
          <span class="font-medium text-right">{{ transaction.description || '—' }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Account</span>
          <span class="font-medium text-right">
            {{ transaction.account?.number || '—' }}
            <span class="text-gray-500 text-xs" v-if="transaction.account?.name">
              — {{ transaction.account.name }}
            </span>
          </span>
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

      <!-- ✅ Smart Back Button -->
      <div class="flex justify-center gap-3">
        <button
          @click="goToAccount(transaction.account?.id)"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          View Account
        </button>

        <button
          @click="navigateTo('/transactions')"
          class="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300 transition"
        >
          Back to History
        </button>
      </div>
    </div>

    <!-- Error State -->
    <div v-else class="text-red-600 mt-10">Failed to load transaction details.</div>
  </div>
</template>

<script setup lang="ts">
const { $api } = useNuxtApp()
const route = useRoute()
const transaction = ref<any>(null)
const loading = ref(true)
const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase

onMounted(async () => {
  try {
    const transactionId = Number(route.params.id)

    // Fetch all user accounts first
    const me = await $api('/me')
    const accounts = me.accounts || []

    let found = null

    for (const acc of accounts) {
      try {
        const tx = await $api(`/accounts/${acc.id}/transactions/${transactionId}`)
        if (tx) {
          found = tx
          break
        }
      } catch (err: any) {

        if (err?.response?.status !== 404) {
          console.error(`Error checking account ${acc.id}:`, err)
        }
      }
    }
    if (!found) {
      console.warn('Transaction not found in any account.')
    }
    transaction.value = found
  } catch (err) {
    console.error('Failed to load transaction details:', err)
  } finally {
    loading.value = false
  }
})


const getLogoUrl = (path: string) => {
  if (!path) return `${BACKEND_URL}/static/logos/default.png`
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
