<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold">Transaction History</h1>

    <div class="mt-4">
      <label class="text-sm">Filter by account ID (optional)</label>
      <input v-model.number="accountId" type="number" placeholder="e.g. 1" class="border p-2 rounded w-full mt-1" />
    </div>

    <div class="mt-4 space-y-2">
      <div v-for="t in items" :key="t.id" class="border rounded p-3 flex justify-between">
        <div>
          <div class="font-medium">{{ t.description }}</div>
          <div class="text-sm text-gray-500">{{ t.reference_number }} — {{ new Date(t.created_at).toLocaleString() }}</div>
        </div>
        <div :class="t.direction === 'debit' ? 'text-red-600' : 'text-green-600'">
          {{ t.direction === 'debit' ? '-' : '+' }}
          {{ (t.amount_cents / 100).toFixed(2) }} {{ t.currency }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { $api } = useNuxtApp()
const items = ref<any[]>([])
const accountId = ref<number | null>(null)

const load = async () => {
  items.value = await $api('/transactions', {
    query: accountId.value ? { account_id: accountId.value } : {}
  })
}
onMounted(load)
watch(accountId, load)
</script>
