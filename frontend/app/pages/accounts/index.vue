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
      <h2 class="text-xl font-semibold text-gray-800 text-center">My Accounts</h2>
    </div>

    <!-- Accounts List -->
    <div
      v-if="accounts.length"
      class="bg-white rounded-2xl shadow border border-gray-100 w-full max-w-lg divide-y divide-gray-100"
    >
      <div
        v-for="a in accounts"
        :key="a.id"
        @click="goDetail(a.id)"
        class="flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition cursor-pointer"
      >
        <!-- Left -->
        <div>
          <p class="text-base font-semibold text-gray-800">{{ a.name }}</p>
          <p class="text-xs text-gray-500">{{ a.number }}</p>
        </div>

        <!-- Right -->
        <div class="text-right">
          <p class="text-base font-bold text-gray-900">
            {{ formatCurrency(a.balance, a.currency) }}
          </p>
          <p class="text-xs text-gray-500">{{ a.currency }}</p>
        </div>
      </div>
    </div>

    <!-- Empty or Loading -->
    <div
      v-else
      class="text-gray-500 mt-20 flex flex-col items-center text-center space-y-3"
    >
      <div class="bg-gray-100 rounded-full p-5">
        <ArrowLeft class="w-8 h-8 text-gray-400 rotate-180" />
      </div>

      <p v-if="loading" class="text-gray-600">Loading accounts...</p>
      <p v-else class="text-gray-600">No accounts found.</p>

      <button
        @click="navigateTo('/accounts/new')"
        class="mt-3 px-5 py-2 bg-gradient-to-r from-gray-800 to-gray-900 text-white rounded-lg hover:opacity-90 transition"
      >
        Add Account
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowLeft } from 'lucide-vue-next'
import { useCurrency } from '~/composables/useCurrency'


const { $api } = useNuxtApp()
const accounts = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const me = await $api('/me')
    accounts.value = me.accounts || []
  } catch (err) {
    console.error('Failed to load accounts', err)
  } finally {
    loading.value = false
  }
})

const goDetail = (id: number) => navigateTo(`/accounts/${id}`)

const { format } = useCurrency()

const formatCurrency = (val?: number | string | null, currency = 'USD') => {
  return format(val, currency)
}
</script>
