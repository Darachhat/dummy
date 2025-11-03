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
      <h2 class="text-lg font-semibold text-gray-700 mx-24 px-4">Transaction Detail</h2>
    </div>

    <!-- Transaction Detail Card -->
    <div v-if="tx" class="bg-white rounded-2xl shadow w-full max-w-md p-6 space-y-3">
      <div class="flex items-center justify-center mb-4">
        <img
          v-if="tx.service_logo_url"
          :src="getLogoUrl(tx.service_logo_url)"
          alt="Service Logo"
          class="w-16 h-16 rounded-full object-contain"
        />
      </div>

      <h3 class="text-lg font-semibold text-center text-gray-800">
        {{ tx.service_name || 'Transaction' }}
      </h3>

      <div class="border-t border-gray-200 my-4"></div>

      <!-- Transaction Fields -->
      <div class="space-y-2 text-sm">
        <div class="flex justify-between">
          <span class="text-gray-500">Transaction ID</span>
          <span class="font-medium text-gray-800">{{ tx.transaction_id }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Reference Number</span>
          <span class="font-medium text-gray-800">{{ tx.reference_number || '—' }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Customer Name</span>
          <span class="font-medium text-gray-800">{{ tx.customer_name || '—' }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Description</span>
          <span class="font-medium text-gray-800 text-right">
            {{ tx.description || '—' }}
          </span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Amount</span>
          <span class="font-medium text-gray-800">{{ formatCurrency(tx.amount) }}</span>
        </div>

        <div v-if="tx.fee" class="flex justify-between">
          <span class="text-gray-500">Fee</span>
          <span class="font-medium text-gray-800">{{ formatCurrency(tx.fee) }}</span>
        </div>

        <div class="flex justify-between border-t border-gray-200 pt-2 mt-2">
          <span class="font-semibold text-gray-700">Total Amount</span>
          <span class="font-semibold text-gray-800">
            {{ formatCurrency(tx.total_amount || tx.amount) }}
          </span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Direction</span>
          <span
            :class="[
              'font-medium',
              tx.direction === 'debit' ? 'text-red-600' : 'text-green-600'
            ]"
          >
            {{ tx.direction }}
          </span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Currency</span>
          <span class="font-medium text-gray-800">{{ tx.currency || 'USD' }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Date</span>
          <span class="font-medium text-gray-800">{{ formatDate(tx.created_at) }}</span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-gray-500 mt-10">Transaction not found.</div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const { $api } = useNuxtApp()
const tx = ref<any>(null)
const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase

onMounted(async () => {
  try {
    tx.value = await $api(`/transactions/${route.params.id}`)
  } catch (err) {
    console.error('Failed to load transaction detail', err)
  }
})

const getLogoUrl = (path: string) => {
  if (!path) return `${BACKEND_URL}/static/logos/default.png`
  return path.startsWith('http') ? path : `${BACKEND_URL}${path}`
}

const formatCurrency = (amount?: number | string | null, currency = 'USD') => {
  if (amount === null || amount === undefined) return '—'
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  return `${currency} ${num.toLocaleString(undefined, { minimumFractionDigits: 2 })}`
}

const formatDate = (iso?: string) => {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleString()
}
</script>
