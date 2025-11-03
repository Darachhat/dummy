<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center py-8">
    <!-- Header -->
    <div class="flex justify-between items-center w-full max-w-md px-4 mb-6">
      <div class="flex items-center gap-2">
        <h2 class="text-lg font-semibold text-gray-700">Welcome back</h2>
      </div>

      <button
        @click="logout"
        class="p-2 bg-red-500 text-white rounded-full shadow hover:bg-red-600 transition"
        title="Logout"
      >
        <LogOut class="w-5 h-5" />
      </button>
    </div>

    <!-- Balance Card -->
    <div class="bg-white rounded-2xl shadow w-full max-w-md p-6 text-center mb-6">
      <p class="text-sm text-gray-500">Account balance</p>
      <h1 class="text-3xl font-bold text-gray-800 mt-1">
        {{ formatCurrency(balance) }}
      </h1>
    </div>

    <!-- Actions -->
    <div class="bg-white rounded-2xl shadow w-full max-w-md flex justify-around py-4 mb-6">
      <div class="flex flex-col items-center">
        <button
          @click="goPayment"
          class="w-12 h-12 bg-gray-600 text-white rounded-full flex items-center justify-center mb-1"
          title="Payment"
        >
          <ArrowUpRight class="w-6 h-6" />
        </button>
        <span class="text-sm text-gray-600">Payment</span>
      </div>

      <div class="flex flex-col items-center">
        <button
          @click="goTransactions"
          class="w-12 h-12 bg-gray-600 text-white rounded-full flex items-center justify-center mb-1"
          title="Transactions"
        >
          <List class="w-6 h-6" />
        </button>
        <span class="text-sm text-gray-600">History</span>
      </div>

      <div class="flex flex-col items-center">
        <button
          @click="goAccounts"
          class="w-12 h-12 bg-gray-600 text-white rounded-full flex items-center justify-center mb-1"
          title="Accounts"
        >
          <User class="w-6 h-6" />
        </button>
        <span class="text-sm text-gray-600">Accounts</span>
      </div>
    </div>

    <!-- Recent Transactions -->
    <div class="w-full max-w-md">
      <div class="flex justify-between px-4 mb-2">
        <h3 class="text-base font-semibold text-gray-700">Recent Transactions</h3>
        <button @click="goTransactions" class="text-sm text-gray-500 hover:text-gray-800">See all</button>
      </div>

      <div v-if="transactions.length" class="bg-white rounded-2xl shadow divide-y divide-gray-100">
        <div
          v-for="t in transactions"
          :key="t.transaction_id"
          @click="goTransactionDetail(t.transaction_id)"
          class="flex items-center justify-between px-4 py-3 hover:bg-gray-50 transition cursor-pointer"
        >
          <!-- Left -->
          <div class="flex items-center space-x-3">
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
              <p class="text-xs text-gray-400">{{ formatDate(t.created_at) }}</p>
            </div>
          </div>

          <!-- Right -->
          <div class="text-right">
            <p
              :class="[ 'text-sm font-semibold', t.direction === 'debit' ? 'text-red-600' : 'text-green-600' ]"
            >
              {{ t.direction === 'debit' ? '-' : '+' }}
              {{ formatCurrency(t.total_amount || t.amount) }}
            </p>
            <p class="text-xs text-gray-500">TID: {{ t.transaction_id }}</p>
          </div>
        </div>
      </div>

      <p v-else class="text-gray-500 text-center mt-6">No recent transactions</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const { $api } = useNuxtApp()
const { logout } = useAuth()
const balance = ref(0)
const transactions = ref<any[]>([])
const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase

onMounted(async () => {
  try {
    const me = await $api('/me')
    balance.value = me.total_balance || 0

    const txs = await $api('/transactions')
    transactions.value = txs.slice(0, 5)
  } catch (err) {
    console.error('Failed to load dashboard', err)
  }
})

const goTransactions = () => navigateTo('/transactions')
const goPayment = () => navigateTo('/payment/start')
const goAccounts = () => navigateTo('/accounts')
const goTransactionDetail = (id: number) => navigateTo(`/transactions/${id}`)

const getLogoUrl = (path: string) => {
  if (!path) return `${BACKEND_URL}/static/logos/default.png`
  if (path.startsWith('http')) return path
  return `${BACKEND_URL}${path}`
}

// 💰 Format decimal currency
const formatCurrency = (val?: number | string | null, currency = 'USD') => {
  if (val === null || val === undefined) return '—'
  const num = typeof val === 'string' ? parseFloat(val) : val
  return `${currency} ${num.toLocaleString(undefined, { minimumFractionDigits: 2 })}`
}

const formatDate = (isoString?: string) => {
  if (!isoString) return '—'
  const date = new Date(isoString)
  return date.toLocaleString()
}
</script>
