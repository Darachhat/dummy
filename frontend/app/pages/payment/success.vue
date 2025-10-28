<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center justify-center text-center px-6">
    <div class="bg-green-100 rounded-full p-6 mb-6 animate-bounce-slow">
      <Check class="w-14 h-14 text-green-600" />
    </div>

    <h1 class="text-2xl font-bold text-gray-800 mb-2">Payment Successful!</h1>
    <p class="text-gray-600 mb-6">Your payment was processed successfully.</p>

    <div class="bg-white shadow rounded-2xl p-6 w-full max-w-md text-left mb-8">
      <p class="text-sm text-gray-500">Reference</p>
      <p class="text-lg font-semibold">{{ payment?.reference_number }}</p>

      <p class="text-sm text-gray-500 mt-4">Amount</p>
      <p class="text-2xl font-bold">${{ (payment?.amount_cents / 100).toFixed(2) }}</p>

      <p class="text-sm text-gray-500 mt-4">Date</p>
      <p class="text-gray-700">{{ formattedDate }}</p>
    </div>

    <div class="flex flex-col gap-3 w-full max-w-md">
      <button @click="goHome" class="w-full py-2 bg-black text-white rounded-lg hover:bg-gray-900">Back to Home</button>
      <button @click="goTransactions" class="w-full py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
        View Transactions
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
const payment = useState<any>('payment')
const goHome = () => navigateTo('/')
const goTransactions = () => navigateTo('/transactions')
const formattedDate = computed(() => new Date().toLocaleString())
</script>

<style scoped>
@keyframes bounce-slow {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}
.animate-bounce-slow {
  animation: bounce-slow 1.8s infinite;
}
</style>
