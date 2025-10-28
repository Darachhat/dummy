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
      <h2 class="text-lg font-semibold text-gray-700 mx-auto">My Accounts</h2>
    </div>

    <!-- Account List -->
    <div
      v-if="accounts.length"
      class="w-full max-w-md bg-white rounded-2xl shadow divide-y divide-gray-100"
    >
      <div
        v-for="a in accounts"
        :key="a.id"
        @click="goAccountDetail(a.id)"
        class="px-5 py-4 hover:bg-gray-50 transition flex justify-between items-center cursor-pointer"
      >
        <div>
          <p class="text-base font-semibold text-gray-800">{{ a.name }}</p>
          <p class="text-sm text-gray-500">{{ a.number }}</p>
        </div>
        <div class="text-right">
          <p class="text-base font-semibold text-gray-800">
            {{ formatCurrency(a.balance_cents) }}
          </p>
          <p class="text-xs text-gray-500">Available Balance</p>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-gray-500 mt-10 text-center">
      <p>No accounts found.</p>
    </div>

    <!-- Bottom Navigation -->
    <div class="fixed bottom-0 left-0 right-0 bg-white shadow flex justify-around py-3 rounded-t-2xl">
      <NuxtLink to="/" class="flex flex-col items-center text-gray-500 hover:text-black">
        <Home class="w-5 h-5" />
        <span class="text-xs">Home</span>
      </NuxtLink>
      <NuxtLink to="/payment/start" class="flex flex-col items-center text-gray-500 hover:text-black">
        <ArrowUpRight class="w-5 h-5" />
        <span class="text-xs">Payment</span>
      </NuxtLink>
      <NuxtLink to="/transactions" class="flex flex-col items-center text-gray-500 hover:text-black">
        <List class="w-5 h-5" />
        <span class="text-xs">History</span>
      </NuxtLink>
      <NuxtLink to="/accounts" class="flex flex-col items-center text-black">
        <User class="w-5 h-5" />
        <span class="text-xs">Accounts</span>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const { $api } = useNuxtApp()
const accounts = ref<any[]>([])

onMounted(async () => {
  try {
    const me = await $api('/me')
    accounts.value = me.accounts
  } catch (err) {
    console.error('Failed to load accounts', err)
  }
})

const formatCurrency = (cents?: number | null) => {
  if (!cents) return '$0.00'
  return `$${(cents / 100).toLocaleString()}`
}

const goAccountDetail = (id: number) => navigateTo(`/accounts/${id}`)
</script>
