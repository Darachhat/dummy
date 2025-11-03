<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center py-10 px-4">
    <!-- Header -->
    <div class="flex items-center w-full max-w-md mb-6">
      <button
        @click="navigateTo('/accounts')"
        class="p-2 bg-white rounded-full shadow hover:bg-gray-50"
      >
        <ArrowLeft class="w-5 h-5 text-gray-600" />
      </button>
      <h2 class="text-lg font-semibold text-gray-700 mx-24 px-4">Account Details</h2>
    </div>

    <!-- Account Info -->
    <div v-if="account" class="bg-white w-full max-w-md rounded-2xl shadow p-6 mb-6">
      <p class="text-sm text-gray-500">Account Name</p>
      <h3 class="text-lg font-semibold text-gray-800">{{ account.name }}</h3>
      <p class="text-sm text-gray-500 mt-2">Account Number</p>
      <p class="text-base font-medium text-gray-700">{{ account.number }}</p>
      <p class="text-sm text-gray-500 mt-2">Balance</p>
      <p class="text-xl font-bold text-gray-800">{{ formatCurrency(account.balance) }}</p>
    </div>

    <!-- Transactions -->
    <div class="w-full max-w-md">
      <div class="flex justify-between px-4 mb-2">
        <h3 class="text-base font-semibold text-gray-700">Recent Transactions</h3>
      </div>

      <!-- Safe check for array -->
      <div v-if="transactions && transactions.length" class="bg-white rounded-2xl shadow divide-y divide-gray-100">
        <div
          v-for="t in transactions"
          :key="t.id"
          @click="goTransactionDetail(t.id)"
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
              <p class="text-sm font-semibold text-gray-800">{{ t.service_name || 'Transaction' }}</p>
              <p class="text-xs text-gray-500">Ref: {{ t.reference_number }}</p>
              <p class="text-xs text-gray-400">{{ formatDate(t.created_at) }}</p>
            </div>
          </div>

          <!-- Right -->
          <div class="text-right">
            <p
              :class="[ 'text-sm font-semibold', t.direction === 'debit' ? 'text-red-600' : 'text-green-600' ]"
            >
              {{ t.direction === 'debit' ? '-' : '+' }}{{ formatCurrency(t.amount) }}
            </p>
          </div>
        </div>
      </div>

      <p v-else class="text-gray-500 text-center mt-6">No transactions found.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const { $api } = useNuxtApp()
const route = useRoute()
const account = ref<any>(null)
const transactions = ref<any[]>([])
const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase

onMounted(async () => {
  try {
    const accId = Number(route.params.id)
    // Load account
    account.value = await $api(`/accounts/${accId}`)
    // Load transactions for that account
    transactions.value = await $api(`/accounts/${accId}/transactions`)
  } catch (err) {
    console.error('Failed to load account details:', err)
  }
})

const goTransactionDetail = (id: number) => navigateTo(`/transactions/${id}`)

const getLogoUrl = (path: string) => {
  if (!path) return `${BACKEND_URL}/static/logos/default.png`
  return path.startsWith('http') ? path : `${BACKEND_URL}${path}`
}

const formatCurrency = (amount: number | null) => {
  if (amount == null) return '—'
  return `$${Number(amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}`
}

const formatDate = (iso?: string) => {
  if (!iso) return '—'
  return new Date(iso).toLocaleString()
}
</script>
