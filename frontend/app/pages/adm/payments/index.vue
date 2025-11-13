<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Payment Management</h1>
    <table class="min-w-full bg-white border rounded-xl">
      <thead class="bg-gray-100">
        <tr>
          <th class="py-2 px-4 text-left">ID</th>
          <th class="py-2 px-4 text-left">Amount</th>
          <th class="py-2 px-4 text-left">Currency</th>
          <th class="py-2 px-4 text-left">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in payments" :key="p.id" class="border-t hover:bg-gray-50">
          <td class="py-2 px-4">{{ p.id }}</td>
          <td class="py-2 px-4">{{ p.amount }}</td>
          <td class="py-2 px-4">{{ p.currency }}</td>
          <td class="py-2 px-4">
            <button class="text-red-500" @click="deletePayment(p.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
const payments = ref([])

onMounted(async () => {
  payments.value = await $fetch('/adm/payments')
})

const deletePayment = async (id: number) => {
  if (confirm('Are you sure?')) {
    await $fetch(`/adm/payments/${id}`, { method: 'DELETE' })
    payments.value = payments.value.filter(p => p.id !== id)
  }
}
</script>
