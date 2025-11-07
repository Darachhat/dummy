<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
    <!-- Header -->
    <div class="relative flex items-center justify-center w-full max-w-lg mb-8">
      <button
        @click="navigateTo('/')"
        class="absolute left-4 p-2 bg-white rounded-full shadow hover:bg-gray-100 transition"
      >
        <ArrowLeft class="w-5 h-5 text-gray-700" />
      </button>
      <h2 class="text-xl font-semibold text-gray-800 text-center">Transaction History</h2>
    </div>

    <!-- Transaction List -->
    <div
      v-if="transactions.length"
      class="bg-white w-full max-w-lg rounded-2xl shadow border border-gray-100 divide-y divide-gray-100"
    >
      <div
        v-for="t in transactions"
        :key="t.transaction_id"
        @click="goDetail(t.transaction_id)"
        class="flex items-center justify-between px-4 py-4 hover:bg-gray-50 transition cursor-pointer"
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
            {{ formatCurrency(t.total_amount || t.amount) }}
          </p>
          <p class="text-xs text-gray-500">TID: {{ t.transaction_id }}</p>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-else
      class="text-gray-500 mt-20 flex flex-col items-center text-center space-y-3"
    >
      <div class="bg-gray-100 rounded-full p-5">
        <ArrowLeft class="w-8 h-8 text-gray-400 rotate-180" />
      </div>
      <p class="text-gray-600">No transactions yet.</p>
      <button
        @click="navigateTo('/payment/start')"
        class="mt-2 px-5 py-2 bg-gradient-to-r from-gray-800 to-gray-900 text-white rounded-lg hover:opacity-90 transition"
      >
        Make a Payment
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowLeft } from 'lucide-vue-next'
import { formatUserDate } from '~/utils/helpers'

const { $api } = useNuxtApp()
const transactions = ref<any[]>([])
const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase

onMounted(async () => {
  try {
    transactions.value = await $api('/transactions/')
  } catch (err) {
    console.error('Failed to load transactions', err)
  }
})

const goDetail = (id: number) => navigateTo(`/transactions/${id}`)

const getLogoUrl = (path: string) => {
  if (!path) return `${BACKEND_URL}/static/logos/default.svg`
  if (path.startsWith('http')) return path
  return `${BACKEND_URL}${path}`
}

const formatCurrency = (amount?: number | string | null, currency = 'USD') => {
  if (amount === null || amount === undefined) return '—'
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  return `${currency} ${num.toLocaleString(undefined, { minimumFractionDigits: 2 })}`
}
</script>
