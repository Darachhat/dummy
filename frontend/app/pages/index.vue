<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center py-8">
    <!-- Header -->
<!-- Header -->
<div class="flex justify-between items-center w-full max-w-md px-4 mb-6">
  <div class="flex items-center gap-2">
    <h2 class="text-lg font-semibold text-gray-700">Welcome back</h2>
  </div>

  <div class="flex gap-2">
    <button
      class="p-2 bg-white rounded-full shadow hover:bg-gray-100 transition"
      title="Notifications"
    >
      <Bell class="w-5 h-5 text-gray-600" />
    </button>
    <button
      @click="logout"
      class="p-2 bg-red-500 text-white rounded-full shadow hover:bg-red-600 transition"
      title="Logout"
    >
      <LogOut class="w-5 h-5" />
    </button>
  </div>
</div>



    <!-- Balance Card -->
    <div class="bg-white rounded-2xl shadow w-full max-w-md p-6 text-center mb-6">
      <p class="text-sm text-gray-500">Account balance</p>
      <h1 class="text-3xl font-bold text-gray-800 mt-1">
        ${{ (balance / 100).toFixed(2) }}
      </h1>
      <p class="text-xs text-gray-400 mt-1">{{ accountNumber }}</p>
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
      title="Account Details"
    >
      <User class="w-6 h-6" />
    </button>
    <span class="text-sm text-gray-600">Accounts</span>
  </div>
</div>


    <!-- Transactions -->
    <div class="w-full max-w-md">
      <div class="flex justify-between px-4 mb-2">
        <h3 class="text-base font-semibold text-gray-700">Transactions</h3>
        <button @click="goTransactions" class="text-sm text-gray-500 hover:text-gray-800">See all</button>
      </div>

      <div v-if="transactions.length" class="space-y-2">
        <div
          v-for="tx in transactions"
          :key="tx.id"
          class="bg-white rounded-xl shadow flex justify-between items-center px-4 py-3"
        >
          <div>
            <p class="font-medium text-gray-800">{{ tx.name }}</p>
            <p class="text-xs text-gray-500">{{ tx.date }}</p>
          </div>
          <p
            :class="tx.direction === 'debit' ? 'text-red-600' : 'text-green-600'"
            class="font-semibold"
          >
            {{ tx.direction === 'debit' ? '-' : '+' }}${{ tx.amount.toFixed(2) }}
          </p>
        </div>
      </div>

      <p v-else class="text-gray-500 text-center mt-6">
        No recent transactions
      </p>
    </div>

  <!-- Bottom Nav -->
<div class="fixed bottom-0 left-0 right-0 bg-white shadow flex justify-around py-3 rounded-t-2xl">
  <NuxtLink to="/" class="flex flex-col items-center text-black">
    <Home class="w-5 h-5" />
    <span class="text-xs">Home</span>
  </NuxtLink>
  <NuxtLink to="/payment/start" class="flex flex-col items-center text-gray-500">
    <ArrowUpRight class="w-5 h-5" />
    <span class="text-xs">Payment</span>
  </NuxtLink>
  <NuxtLink to="/transactions" class="flex flex-col items-center text-gray-500">
    <List class="w-5 h-5" />
    <span class="text-xs">History</span>
  </NuxtLink>
  <NuxtLink to="/accounts" class="flex flex-col items-center text-gray-500">
    <User class="w-5 h-5" />
    <span class="text-xs">Accounts</span>
  </NuxtLink>
</div>

  </div>
</template>

<script setup lang="ts">
const { $api } = useNuxtApp()
const balance = ref(0)
const { logout } = useAuth()
const accountNumber = ref('')
const transactions = ref<any[]>([])

onMounted(async () => {
  const me = await $api('/me')
  balance.value = me.total_balance_cents
  accountNumber.value = me.accounts[0]?.number || '---'

  const txs = await $api('/transactions')
  transactions.value = txs.map((t: any) => ({
    id: t.id,
    name: t.reference_number,
    amount: t.amount_cents / 100,
    date: new Date(t.created_at).toLocaleDateString(),
    direction: t.direction
  }))
})

const goTransactions = () => navigateTo('/transactions')
const goPayment = () => navigateTo('/payment/start')
const goAccounts = () => navigateTo('/accounts')
</script>
