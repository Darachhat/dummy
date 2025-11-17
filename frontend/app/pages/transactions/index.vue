<!-- src/pages/transactions/index.vue (example path) -->
<template>
  <AppPage title="Transaction History" back-to="/">
    <!-- Transaction List -->
    <div
      v-if="transactions.length"
      class="bg-white w-full rounded-2xl shadow border border-gray-100 divide-y divide-gray-100"
    >
      <div
        v-for="t in transactions"
        :key="t.id"
        @click="goDetail(t.id ?? t.transaction_id)"
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
  </AppPage>
</template>

<script setup lang="ts">
import { ArrowLeft } from 'lucide-vue-next'
import AppPage from '~/components/AppPage.vue'
import { formatUserDate } from '~/utils/helpers'
import { useCurrency } from '~/composables/useCurrency'
import { useLogoUrl } from '~/composables/useLogoUrl'

const { $api } = useNuxtApp()
const transactions = ref<any[]>([])

const { getLogoUrl } = useLogoUrl()
const { format } = useCurrency()

onMounted(async () => {
  try {
    const res = await $api('/transactions/')
    transactions.value = Array.isArray(res) ? res : (res.items ?? [])
  } catch (err) {
    console.error('Failed to load transactions', err)
  }
})

const goDetail = (id: number | string) => {
  const finalId = typeof id === 'number' && !Number.isNaN(id) ? id : Number(id)
  if (!Number.isNaN(finalId) && finalId !== 0) {
    navigateTo(`/transactions/${finalId}`)
  } else {
    navigateTo(`/transactions/${encodeURIComponent(String(id))}`)
  }
}

const formatCurrency = (val?: number | string | null, currency = 'USD') =>
  format(val, currency)
</script>
