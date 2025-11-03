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
      <h2 class="text-lg font-semibold text-gray-700 mx-auto">
        Account Details
      </h2>
    </div>

    <!-- Account Info -->
    <div
      v-if="account"
      class="bg-white rounded-2xl shadow w-full max-w-md p-6 space-y-4"
    >
      <div class="text-center">
        <h3 class="text-2xl font-bold text-gray-800">{{ account.name }}</h3>
        <p class="text-gray-500">{{ account.number }}</p>
      </div>

      <div class="border-t border-gray-200 my-3"></div>

      <div class="space-y-2 text-sm">
        <div class="flex justify-between">
          <span class="text-gray-500">Currency</span>
          <span class="font-medium text-gray-800">{{ account.currency }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-500">Current Balance</span>
          <span class="font-semibold text-gray-800">
            {{ formatCurrency(account.balance) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Transactions -->
    <div v-if="transactions.length" class="w-full max-w-md mt-6">
      <h3 class="text-base font-semibold text-gray-700 mb-2 px-2">
        Recent Transactions
      </h3>
      <div class="bg-white rounded-2xl shadow divide-y divide-gray-100">
        <div
          v-for="t in transactions"
          :key="t.transaction_id"
          class="flex items-center justify-between px-4 py-3 hover:bg-gray-50 transition"
        >
          <div>
            <p class="text-sm font-medium text-gray-800">
              {{ t.service_name || 'Transaction' }}
            </p>
            <p class="text-xs text-gray-500">
              Ref: {{ t.reference_number }}
            </p>
            <p class="text-xs text-gray-400">{{ formatDate(t.created_at) }}</p>
          </div>
          <div class="text-right">
            <p
              :class="[
                'text-sm font-semibold',
                t.direction === 'debit' ? 'text-red-600' : 'text-green-600'
              ]"
            >
              {{ t.direction === 'debit' ? '-' : '+' }}{{ formatCurrency(t.amount) }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <p v-else class="text-gray-500 mt-10">
      No transactions found for this account.
    </p>
  </div>
</template>

<script setup lang="ts">
const { $api } = useNuxtApp()
const route = useRoute()
const account = ref<any>(null)
const transactions = ref<any[]>([])

// Fetch account detail + transactions
onMounted(async () => {
  try {
    const accRes = await $api(`/accounts/${route.params.id}`)
    account.value = accRes

    const txRes = await $api('/transactions')
    transactions.value = txRes.filter(
      (t: any) => t.account_id === Number(route.params.id)
    )
  } catch (err) {
    console.error('Failed to load account details', err)
  }
})

// Formatters
const formatCurrency = (amount?: number | null, currency = 'USD') => {
  if (!amount) return '—'
  return `${currency} ${Number(amount).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`
}

const formatDate = (iso?: string) => {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleString()
}
</script>
