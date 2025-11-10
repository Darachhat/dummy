<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Transaction Management</h1>
    <table class="min-w-full bg-white border rounded-xl">
      <thead class="bg-gray-100">
        <tr>
          <th class="py-2 px-4 text-left">ID</th>
          <th class="py-2 px-4 text-left">Amount</th>
          <th class="py-2 px-4 text-left">Status</th>
          <th class="py-2 px-4 text-left">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="t in transactions" :key="t.id" class="border-t hover:bg-gray-50">
          <td class="py-2 px-4">{{ t.id }}</td>
          <td class="py-2 px-4">{{ t.amount }}</td>
          <td class="py-2 px-4">{{ t.status }}</td>
          <td class="py-2 px-4">
            <button class="text-red-500" @click="deleteTransaction(t.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
const transactions = ref([])

onMounted(async () => {
  transactions.value = await $fetch('/admin/transactions')
})

const deleteTransaction = async (id: number) => {
  if (confirm('Are you sure?')) {
    await $fetch(`/admin/transactions/${id}`, { method: 'DELETE' })
    transactions.value = transactions.value.filter(t => t.id !== id)
  }
}
</script>
