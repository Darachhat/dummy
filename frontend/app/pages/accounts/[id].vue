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
      <h2 class="text-lg font-semibold text-gray-700 mx-auto">Account Details</h2>
    </div>

    <!-- Account Card -->
    <div v-if="account" class="bg-white rounded-2xl shadow w-full max-w-md p-6 mb-6 text-center">
      <h3 class="text-lg font-semibold text-gray-800">{{ account.name }}</h3>
      <p class="text-sm text-gray-500">{{ account.number }}</p>
      <h1 class="text-3xl font-bold text-gray-800 mt-2">
        {{ formatCurrency(account.balance_cents) }}
      </h1>
      <p class="text-xs text-gray-500 mt-1 mb-4">Current Balance</p>

      <button
        @click="showTransfer = true"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        Transfer Between Accounts
      </button>
    </div>

    <!-- Transactions for this account -->
    <div
      v-if="transactions.length"
      class="bg-white rounded-2xl shadow w-full max-w-md divide-y divide-gray-100"
    >
      <div
        v-for="t in transactions"
        :key="t.transaction_id ?? t.id"
        @click="goTransactionDetail(t.transaction_id ?? t.id)"
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
            <p class="text-sm font-semibold text-gray-800">
              {{ t.service_name || 'Transaction' }}
            </p>
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
            {{ t.direction === 'debit' ? '-' : '+' }}{{ formatCurrency(t.total_amount_cents ?? t.amount_cents) }}
          </p>
          <p class="text-xs text-gray-500">TID: {{ t.transaction_id ?? t.id }}</p>
        </div>
      </div>
    </div>

    <p v-else-if="loaded" class="text-gray-500 mt-10">No transactions for this account.</p>
    <p v-else class="text-gray-500 mt-10">Loading…</p>

    <!-- Transfer Modal -->
    <div
      v-if="showTransfer"
      class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-2xl shadow-lg w-full max-w-md p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Transfer Between Accounts</h3>

        <label class="block text-sm text-gray-600 mb-1">From</label>
        <input
          type="text"
          :value="account?.name + ' (' + account?.number + ')'"
          disabled
          class="w-full border border-gray-300 rounded-lg px-3 py-2 mb-3 bg-gray-100"
        />

        <label class="block text-sm text-gray-600 mb-1">To Account</label>
        <select
          v-model="toAccountId"
          class="w-full border border-gray-300 rounded-lg px-3 py-2 mb-3"
        >
          <option disabled value="">Select destination account</option>
          <option
            v-for="a in otherAccounts"
            :key="a.id"
            :value="a.id"
          >
            {{ a.name }} — {{ a.number }}
          </option>
        </select>

        <label class="block text-sm text-gray-600 mb-1">Amount (USD)</label>
        <input
          v-model.number="amount"
          type="number"
          placeholder="Enter amount"
          class="w-full border border-gray-300 rounded-lg px-3 py-2 mb-3"
        />

        <div class="flex justify-end gap-2">
          <button
            @click="showTransfer = false"
            class="px-4 py-2 border rounded-lg text-gray-600 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="submitTransfer"
            :disabled="!toAccountId || !amount"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            Transfer
          </button>
        </div>

        <p v-if="error" class="text-red-600 text-sm mt-3">{{ error }}</p>
        <p v-if="success" class="text-green-600 text-sm mt-3">{{ success }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { $api } = useNuxtApp()
const route = useRoute()

const account = ref<any>(null)
const accounts = ref<any[]>([])
const transactions = ref<any[]>([])
const loaded = ref(false)
const error = ref('')
const success = ref('')
const showTransfer = ref(false)
const toAccountId = ref('')
const amount = ref<number | null>(null)
const BACKEND_URL = 'http://127.0.0.1:8000'

// Load account + transactions
onMounted(async () => {
  try {
    const me = await $api('/me')
    accounts.value = me.accounts
    account.value = accounts.value.find((a: any) => a.id === parseInt(route.params.id as string))

    const txs = await $api('/transactions')
    transactions.value = txs.filter((t: any) => t.account_id === account.value.id)
  } catch (err) {
    console.error('Failed to load account details', err)
  } finally {
    loaded.value = true
  }
})

const otherAccounts = computed(() =>
  accounts.value.filter((a: any) => a.id !== account.value?.id)
)

// Submit transfer
const submitTransfer = async () => {
  if (!toAccountId.value || !amount.value) return
  try {
    await $api(
      `/accounts/transfer?from_id=${account.value.id}&to_id=${toAccountId.value}&amount_cents=${amount.value * 100}`,
      { method: 'POST' }
    )
    success.value = 'Transfer successful!'
    error.value = ''
    showTransfer.value = false
    // refresh balances
    const me = await $api('/me')
    accounts.value = me.accounts
    account.value = accounts.value.find((a: any) => a.id === parseInt(route.params.id as string))
  } catch (err) {
    console.error('Transfer failed', err)
    success.value = ''
    error.value = 'Transfer failed. Please try again.'
  }
}

const goTransactionDetail = (id: number) => navigateTo(`/transactions/${id}`)

const getLogoUrl = (path: string) => {
  if (!path) return `${BACKEND_URL}/static/logos/default.png`
  if (path.startsWith('http')) return path
  return `${BACKEND_URL}${path}`
}

const formatCurrency = (cents?: number | null) => {
  if (!cents) return '$0.00'
  return `$${(cents / 100).toLocaleString()}`
}

const formatDate = (iso?: string) => {
  if (!iso) return '—'
  return new Date(iso).toLocaleString()
}
</script>
