<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center py-10 px-4">
    <!-- Header -->
    <div class="flex items-center justify-between w-full max-w-md mb-6">
      <div class="flex items-center">
        <button
          @click="navigateTo('/')"
          class="p-2 bg-white rounded-full shadow hover:bg-gray-50"
        >
          <ArrowLeft class="w-5 h-5 text-gray-600" />
        </button>
        <h2 class="text-lg font-semibold text-gray-700 ml-3">My Accounts</h2>
      </div>

    </div>

    <!-- Accounts List -->
    <div
      v-if="accounts.length"
      class="bg-white rounded-2xl shadow w-full max-w-md divide-y divide-gray-100"
    >
      <div
        v-for="a in accounts"
        :key="a.id"
        @click="goDetail(a.id)"
        class="flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition cursor-pointer"
      >
        <div>
          <p class="text-sm font-semibold text-gray-800">{{ a.name }}</p>
          <p class="text-xs text-gray-500">{{ a.number }}</p>
        </div>

        <div class="text-right">
          <p class="text-base font-bold text-gray-800">
            {{ formatCurrency(a.balance, a.currency) }}
          </p>
          <p class="text-xs text-gray-500">{{ a.currency }}</p>
        </div>
      </div>
    </div>

    <!-- Empty / Loading -->
    <div v-else class="text-gray-500 mt-10">
      <p v-if="loading">Loading accounts...</p>
      <p v-else>No accounts found</p>
    </div>
  </div>
</template>

<script setup lang="ts">
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

const formatCurrency = (amount?: number | null, currency = 'USD') => {
  if (amount == null) return '—'
  return `${currency} ${Number(amount).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`
}
</script>
