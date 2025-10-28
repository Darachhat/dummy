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
      <h2 class="text-lg font-semibold text-gray-700 mx-auto">Transaction Details</h2>
    </div>

    <!-- Content -->
    <div v-if="tx" class="bg-white rounded-2xl shadow w-full max-w-md p-6 space-y-3">
      <div class="flex justify-center items-center space-x-3 mb-4">
        <img
          v-if="tx.service_logo_url"
          :src="getLogoUrl(tx.service_logo_url)"
          alt="Service Logo"
          class="w-14 h-14 rounded-full object-contain"
        />
        <Check v-if="tx.direction === 'debit'" class="w-10 h-10 text-green-600" />
      </div>

      <h3 class="text-lg font-semibold text-gray-800 text-center">
        {{ tx.service_name || 'Transaction' }}
      </h3>

      <div class="text-sm space-y-1">
        <div class="flex justify-between">
          <span class="text-gray-500">Bank TID</span>
          <span class="font-medium text-gray-800">{{ tx.transaction_id }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">CDC Ref. No.</span>
          <span class="font-medium text-gray-800">{{ tx.reference_number || '—' }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Customer Name</span>
          <span class="font-medium text-gray-800">{{ tx.customer_name || '—' }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Amount</span>
          <span class="font-medium text-gray-800">{{ formatCurrency(tx.amount_cents) }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Fee</span>
          <span class="font-medium text-gray-800">{{ formatCurrency(tx.fee_cents) }}</span>
        </div>

        <div class="border-t border-gray-200 my-3"></div>

        <div class="flex justify-between text-base font-semibold">
          <span>Total Amount</span>
          <span>{{ formatCurrency(tx.total_amount_cents || tx.amount_cents) }}</span>
        </div>

        <div class="border-t border-gray-200 my-3"></div>

        <div class="flex justify-between text-sm">
          <span class="text-gray-500">Transaction Date</span>
          <span class="font-medium text-gray-800">{{ formatDate(tx.created_at) }}</span>
        </div>
      </div>
    </div>

    <p v-else class="text-gray-500 mt-10">Loading transaction...</p>
  </div>
</template>

<script setup lang="ts">
const { $api } = useNuxtApp()
const route = useRoute()
const tx = ref<any>(null)
const BACKEND_URL = 'http://127.0.0.1:8000'

onMounted(async () => {
  try {
    tx.value = await $api(`/transactions/${route.params.id}`)
  } catch (err) {
    console.error('Failed to load transaction', err)
  }
})

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
