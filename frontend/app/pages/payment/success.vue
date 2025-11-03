<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center justify-center text-center px-6 py-10">
    <div class="bg-white rounded-2xl shadow w-full max-w-md mb-3">
      <!-- Logo + Check -->
      <div class="flex p-6 justify-center items-center space-x-3">
        <img
          v-if="payment?.service?.logo_url"
          :src="getLogoUrl(payment.service.logo_url)"
          alt="Service Logo"
          class="w-14 h-14 rounded-full object-contain"
        />
        <Check class="w-14 h-14 text-green-600" />
      </div>

      <h1 class="text-2xl font-bold text-gray-800 mb-2">Payment Successful!</h1>
      <p class="text-gray-600 mb-6">Your payment was processed successfully.</p>
    </div>

    <!-- Bill Details -->
    <div class="bg-white shadow rounded-2xl p-6 w-full max-w-md text-left space-y-2">
      <h3 class="text-lg font-semibold text-gray-700 mb-3">
        Bill to {{ payment?.service_name || 'Service' }}
      </h3>

      <div class="flex justify-between text-sm">
        <span class="text-gray-500">Reference No.</span>
        <span class="font-medium">{{ payment?.reference_number }}</span>
      </div>

      <div class="flex justify-between text-sm">
        <span class="text-gray-500">Customer Name</span>
        <span class="font-medium">{{ payment?.customer_name || '—' }}</span>
      </div>

      <div class="flex justify-between text-sm">
        <span class="text-gray-500">Invoice Amount</span>
        <span class="font-medium">
          {{ formatCurrency(payment?.invoice_amount) }} {{ payment?.invoice_currency }}
        </span>
      </div>

      <div v-if="payment?.ledger_amount" class="flex justify-between text-xs text-gray-500">
        <span>Converted Amount</span>
        <span>
          ≈ {{ formatCurrency(payment.ledger_amount) }} {{ payment.ledger_currency }}
        </span>
      </div>

      <div class="flex justify-between text-sm">
        <span class="text-gray-500">Fee</span>
        <span class="font-medium">
          {{ formatCurrency(payment?.fee) }} {{ payment?.ledger_currency }}
        </span>
      </div>

      <div class="border-t border-gray-200 my-3"></div>

      <div class="flex justify-between text-base font-semibold">
        <span>Total Paid</span>
        <span>{{ formatCurrency(payment?.total_amount) }} {{ payment?.ledger_currency }}</span>
      </div>

      <div class="flex justify-between text-sm mt-2">
        <span class="text-gray-500">Transaction ID</span>
        <span class="font-medium">{{ payment?.transaction_id || '—' }}</span>
      </div>
    </div>

    <!-- Buttons -->
    <div class="flex flex-col gap-3 w-full max-w-md mt-8">
      <button
        @click="navigateTo('/')"
        class="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        Back to Home
      </button>
      <button
        @click="navigateTo('/transactions')"
        class="w-full py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition"
      >
        View Transactions
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
const payment = useState<any>('payment')
const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase

const getLogoUrl = (path: string) => {
  if (!path) return `${BACKEND_URL}/static/logos/default.png`
  return path.startsWith('http') ? path : `${BACKEND_URL}${path}`
}

const formatCurrency = (n?: number | null) => {
  if (!n) return '—'
  return n.toLocaleString(undefined, { minimumFractionDigits: 2 })
}
</script>
