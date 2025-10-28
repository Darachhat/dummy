<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center justify-center text-center px-6 py-10">
   <div class="bg-white rounded-2xl shadow w-full max-w-md mb-3">
       <!-- Logo + Check -->
    <div class="flex  p-6 justify-center items-center space-x-3 mb-4">
      <img
        v-if="payment?.service?.logo_url"
        :src="getLogoUrl(payment.service.logo_url)"
        alt="Service Logo"
        class="w-14 h-14 rounded-full object-contain"
      />
      <Check class="w-14 h-14 text-green-600" />
    </div>

    <!-- Success Heading -->
    <h1 class="text-2xl font-bold text-gray-800 mb-2">Payment Successful!</h1>
    <p class="text-gray-600 mb-6">Your payment was processed successfully.</p>

   </div>
    <!-- Bill Details Card -->
    <div class="bg-white shadow rounded-2xl p-6 w-full max-w-md text-left space-y-1">
      <h3 class="text-lg font-semibold text-gray-700 mb-3">
        Bill to {{ payment?.service?.name || 'Service' }}
      </h3>

      <div class="flex justify-between">
        <span class="text-gray-500">From Account</span>
        <span class="font-medium text-gray-800">{{ payment?.from_account?.number || '—' }}</span>
      </div>

      <div class="flex justify-between">
        <span class="text-gray-500">CDC Ref. No.</span>
        <span class="font-medium text-gray-800">{{ payment?.reference_number || '—' }}</span>
      </div>

      <div class="flex justify-between">
        <span class="text-gray-500">Customer Name</span>
        <span class="font-medium text-gray-800">{{ payment?.customer_name || '—' }}</span>
      </div>

      <div class="flex justify-between">
        <span class="text-gray-500">Amount</span>
        <span class="font-medium text-gray-800">{{ formatCurrency(payment?.amount_cents) }}</span>
      </div>

      <div class="flex justify-between">
        <span class="text-gray-500">Fee</span>
        <span class="font-medium text-gray-800">{{ formatCurrency(payment?.fee_cents) }}</span>
      </div>

      <div class="border-t border-gray-200 my-3"></div>

      <div class="flex justify-between text-base font-semibold">
        <span>Total Amount</span>
        <span>{{ formatCurrency(payment?.total_amount_cents || payment?.amount_cents) }}</span>
      </div>

      <div class="flex justify-between text-sm mt-2">
  <span class="text-gray-500">Bank TID</span>
  <span class="font-medium text-gray-800">{{ payment?.transaction_id || '—' }}</span>
</div>

    </div>

    <!-- Buttons -->
    <div class="flex flex-col gap-3 w-full max-w-md mt-8">
      <button
        @click="goHome"
        class="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        Back to Home
      </button>
      <button
        @click="goTransactions"
        class="w-full py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition"
      >
        View Transactions
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
const payment = useState<any>('payment')
const BACKEND_URL = 'http://127.0.0.1:8000'

const getLogoUrl = (path: string) => {
  if (!path) return `${BACKEND_URL}/static/logos/default.png`
  if (path.startsWith('http')) return path
  return `${BACKEND_URL}${path}`
}

const formatCurrency = (cents?: number | null) => {
  if (!cents) return '—'
  return `${(cents / 100).toLocaleString()} USD`
}

const goHome = () => navigateTo('/')
const goTransactions = () => navigateTo('/transactions')
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
