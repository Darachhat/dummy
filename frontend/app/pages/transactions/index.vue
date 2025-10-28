<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center py-10 px-4">
    <!-- Header -->
    <div class="flex items-center w-full max-w-md mb-6">
      <button
        @click="navigateTo('/')"
        class="p-2 bg-white rounded-full shadow hover:bg-gray-50"
      >
        <ArrowLeft class="w-5 h-5 text-gray-600" />
      </button>
      <h2 class="text-lg font-semibold text-gray-700 mx-auto">Transaction History</h2>
    </div>

    <!-- Transaction List -->
    <div
      v-if="transactions.length"
      class="bg-white w-full max-w-md rounded-2xl shadow divide-y divide-gray-100"
    >
      <div
        v-for="t in transactions"
        :key="t.transaction_id"
        @click="goDetail(t.transaction_id)"
        class="flex items-center justify-between px-4 py-3 hover:bg-gray-50 transition cursor-pointer"
      >
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

        <div class="text-right">
          <p
            :class="[
              'text-sm font-semibold',
              t.direction === 'debit' ? 'text-red-600' : 'text-green-600'
            ]"
          >
            {{ t.direction === 'debit' ? '-' : '+' }}{{ formatCurrency(t.total_amount_cents || t.amount_cents) }}
          </p>
          <p class="text-xs text-gray-500">TID: {{ t.transaction_id }}</p>
        </div>
      </div>
    </div>

    <div v-else class="text-gray-500 mt-10">No transactions yet.</div>
  </div>
</template>

<script setup lang="ts">
const { $api } = useNuxtApp()
const transactions = ref<any[]>([])
const BACKEND_URL = 'http://127.0.0.1:8000'

onMounted(async () => {
  try {
    transactions.value = await $api('/transactions')
  } catch (err) {
    console.error('Failed to load transactions', err)
  }
})

const goDetail = (id: number) => navigateTo(`/transactions/${id}`)

const getLogoUrl = (path: string) => {
  if (!path) return `${BACKEND_URL}/static/logos/default.png`
  if (path.startsWith('http')) return path
  return `${BACKEND_URL}${path}`
}

const formatCurrency = (cents?: number | null) => {
  if (!cents) return '—'
  return `${(cents / 100).toLocaleString()} USD`
}

const formatDate = (iso?: string) => {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleString()
}
</script>
