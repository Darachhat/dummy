<script setup lang="ts">
import { ref, onMounted } from 'vue'
const route = useRoute()
const id = route.params.id
const transaction = ref(null)

onMounted(async () => {
  transaction.value = await $fetch(`/admin/transactions/${id}`)
})
</script>

<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Transaction Details</h1>
    <div v-if="transaction">
      <p><b>ID:</b> {{ transaction.id }}</p>
      <p><b>Amount:</b> {{ transaction.amount }}</p>
      <p><b>Status:</b> {{ transaction.status }}</p>
      <p><b>Date:</b> {{ transaction.created_at }}</p>
    </div>
    <div v-else>
      <p>Loading transaction details...</p>
    </div>
  </div>
</template>
