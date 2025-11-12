<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
    <!-- Header -->
    <div class="relative flex items-center justify-center w-full max-w-lg mb-8">
      <button
        @click="navigateTo('/accounts')"
        class="absolute left-4 p-2 bg-white rounded-full shadow hover:bg-gray-100 transition"
      >
        <ArrowLeft class="w-5 h-5 text-gray-700" />
      </button>
      <h2 class="text-xl font-semibold text-gray-800 text-center">Account Details</h2>
    </div>

    <!-- Account Info -->
    <div
      v-if="account"
      class="bg-white w-full max-w-lg rounded-2xl shadow p-6 border border-gray-100 mb-6"
    >
      <p class="text-sm text-gray-500">Account Name</p>
      <h3 class="text-lg font-semibold text-gray-800">{{ account.name }}</h3>

      <p class="text-sm text-gray-500 mt-2">Account Number</p>
      <p class="text-base font-medium text-gray-700">{{ account.number }}</p>

      <p class="text-sm text-gray-500 mt-2">Balance</p>
      <p class="text-xl font-bold text-gray-800">{{ formatCurrency(account.balance) }}</p>
    </div>

    <!-- Transactions -->
    <div class="w-full max-w-lg">
      <div class="flex justify-between px-4 mb-3">
        <h3 class="text-base font-semibold text-gray-700">Recent Transactions</h3>
        <p class="text-xs text-gray-400">
          Timezone: {{ Intl.DateTimeFormat().resolvedOptions().timeZone }}
        </p>
      </div>

      <!-- Safe check for array -->
      <div
        v-if="transactions && transactions.length"
        class="bg-white rounded-2xl shadow border border-gray-100 divide-y divide-gray-100"
      >
        <div
          v-for="t in transactions"
          :key="t.id"
          @click="goTransactionDetail(t.id)"
          class="flex items-center justify-between px-4 py-3 hover:bg-gray-50 transition cursor-pointer"
        >
          <!-- Left -->
          <div class="flex items-center gap-3">
            <img
              v-if="t.service_logo_url"
              :src="getLogoUrl(t.service_logo_url)"
              alt="Service Logo"
              class="w-10 h-10 rounded-full object-contain"
            />
            <div>
              <p class="text-sm font-semibold text-gray-800">
                {{ t.service_name || 'Transaction' }}
              </p>
              <p class="text-xs text-gray-500">Ref: {{ t.reference_number }}</p>
              <p class="text-xs text-gray-400">{{ formatUserDate(t.created_at) }}</p>
            </div>
          </div>

          <!-- Right -->
          <div class="text-right">
            <p
              :class="[
                'text-sm font-semibold',
                t.direction === 'debit' ? 'text-red-600' : 'text-green-600'
              ]"
            >
              {{ t.direction === 'debit' ? '-' : '+' }}
              {{ formatCurrency(t.amount) }}
            </p>
          </div>
        </div>
      </div>

      <p v-else class="text-gray-500 text-center mt-8">
        No transactions found.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowLeft } from 'lucide-vue-next'
import { formatUserDate } from '~/utils/helpers'

const { $api } = useNuxtApp()
const route = useRoute()
const account = ref<any>(null)
const transactions = ref<any[]>([])
const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase

onMounted(async () => {
  try {
    const rawId = route.params.id
    const accId = Number(rawId)
    if (Number.isNaN(accId)) {
      console.warn('Invalid account id in route:', rawId)
      return navigateTo('/accounts')
    }

    console.debug('Loading account', accId)
    const acc = await $api(`/accounts/${accId}`)
    account.value = acc ?? null

    // fetch transactions
    let txs: any = []
    try {
      const res = await $api(`/accounts/${accId}/transactions`)
      txs = Array.isArray(res) ? res : (res?.items ?? [])
      console.debug(`/accounts/${accId}/transactions ->`, txs)
    } catch (err) {
      console.warn(`Failed to fetch /accounts/${accId}/transactions`, err)
      txs = []
    }
    transactions.value = (txs || []).map((t: any) => {
      const id = t.id ?? t.transaction_id ?? null
      const rawAmount = t.amount ?? t.total_amount ?? t.totalAmount ?? 0
      const amountNum = typeof rawAmount === 'string' ? parseFloat(rawAmount) : rawAmount
      const created = t.created_at ?? t.createdAt ?? t.createdAtIso ?? null

      return {
        ...t,
        id,
        amount: Number.isFinite(Number(amountNum)) ? Number(amountNum) : 0,
        created_at: created,
      }
    })
  } catch (err) {
    console.error('Failed to load account details:', err)
    navigateTo('/accounts')
  }
})

const goTransactionDetail = (id: number | string) => {
  if (typeof id === 'number' && !Number.isNaN(id)) {
    navigateTo(`/transactions/${id}`)
    return
  }
  const maybeNum = Number(id)
  if (!Number.isNaN(maybeNum)) {
    navigateTo(`/transactions/${maybeNum}`)
    return
  }
  navigateTo(`/transactions/${encodeURIComponent(String(id))}`)
}


const getLogoUrl = (path: string) => {
  if (!path) return `${BACKEND_URL}/static/logos/default.png`
  return path.startsWith('http') ? path : `${BACKEND_URL}${path}`
}

const formatCurrency = (amount: number | null) => {
  if (amount == null) return '—'
  return `$${Number(amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}`
}
</script>
