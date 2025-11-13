<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Payment Details</h1>

    <div v-if="payment">
      <p><strong>ID:</strong> {{ payment.id }}</p>
      <p><strong>Amount:</strong> {{ payment.amount }}</p>
      <p><strong>Currency:</strong> {{ payment.currency }}</p>
      <p><strong>Status:</strong> {{ payment.status }}</p>
      <p><strong>Date:</strong> {{ payment.created_at }}</p>
    </div>

    <div v-else>
      <p>Loading payment details...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const route = useRoute()
const payment = ref(null)

onMounted(async () => {
  try {
    payment.value = await $fetch(`/adm/payments/${route.params.id}`)
  } catch (error) {
    console.error('Failed to load payment:', error)
  }
})
</script>
