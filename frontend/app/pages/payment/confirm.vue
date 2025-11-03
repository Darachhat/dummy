<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center py-10">
    <!-- Header -->
    <div class="flex items-center w-full max-w-md mb-6">
      <button
        @click="navigateTo('/payment/invoice')"
        class="p-2 bg-white rounded-full shadow hover:bg-gray-50"
      >
        <ArrowLeft class="w-5 h-5 text-gray-600" />
      </button>
      <h2 class="text-lg mx-auto font-semibold text-gray-700">Confirmation</h2>
    </div>

    <!-- Confirmation Card -->
    <div class="bg-white rounded-2xl shadow w-full max-w-md p-6 space-y-4 text-center">
      <!-- Logo -->
      <div v-if="payment?.service?.logo_url" class="flex justify-center mb-2">
        <img
          :src="getLogoUrl(payment.service.logo_url)"
          alt="Service Logo"
          class="w-20 h-20 object-contain rounded-full"
        />
      </div>

      <h3 class="text-lg font-semibold text-gray-700">
        Bill to {{ payment?.service?.name || '' }}
      </h3>

      <div class="border-t border-gray-200 my-4"></div>

      <!-- Payment Info -->
      <div class="text-left text-sm space-y-2">
        <div class="flex justify-between">
          <span class="text-gray-500">From Account</span>
          <span class="font-medium text-gray-800">{{ payment?.from_account?.number }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Customer Name</span>
          <span class="font-medium text-gray-800">{{ payment?.customer_name || '—' }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Reference No.</span>
          <span class="font-medium text-gray-800">{{ payment?.reference_number }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Invoice Amount</span>
          <span class="font-medium text-gray-800">
            {{ formatCurrency(payment?.invoice_amount) }} {{ payment?.invoice_currency }}
          </span>
        </div>

        <div v-if="payment?.ledger_amount" class="flex justify-between text-xs text-gray-500">
          <span>Converted Amount</span>
          <span>
            ≈ {{ formatCurrency(payment.ledger_amount) }} {{ payment.ledger_currency }}
          </span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Fee</span>
          <span class="font-medium text-gray-800">
            {{ formatCurrency(payment?.fee) }} {{ payment?.ledger_currency }}
          </span>
        </div>

        <div class="border-t border-gray-200 my-3"></div>

        <div class="flex justify-between text-base font-semibold">
          <span>Total</span>
          <span>
            {{ formatCurrency(payment?.total_amount) }} {{ payment?.ledger_currency }}
          </span>
        </div>
      </div>
    </div>

    <!-- PIN Input -->
    <div class="bg-white rounded-2xl shadow w-full max-w-md p-6 text-center mt-6">
      <p class="text-sm text-gray-600 mb-4">Enter your 4-digit PIN</p>

      <div class="flex justify-center space-x-3 mb-6">
        <input
          v-for="i in 4"
          :key="i"
          ref="pinInputs"
          type="password"
          maxlength="1"
          inputmode="numeric"
          class="w-12 h-12 text-center border border-gray-300 rounded-lg text-lg font-semibold focus:ring-2 focus:ring-blue-500 focus:outline-none"
          @input="handleInput(i - 1, $event)"
          @keydown.backspace="handleBackspace(i - 1, $event)"
        />
      </div>

      <button
        :disabled="pin.join('').length < 4"
        @click="confirmPayment"
        class="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
      >
        CONFIRM PAYMENT
      </button>

      <p v-if="error" class="text-red-600 text-sm mt-3">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const { $api } = useNuxtApp()
const payment = useState<any>('payment')
const pin = ref<string[]>(['', '', '', ''])
const pinInputs = ref<HTMLInputElement[]>([])
const error = ref('')

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

const handleInput = (index: number, e: Event) => {
  const target = e.target as HTMLInputElement
  pin.value[index] = target.value
  if (target.value && index < 3) pinInputs.value[index + 1]?.focus()
}

const handleBackspace = (index: number, e: KeyboardEvent) => {
  const target = e.target as HTMLInputElement
  if (!target.value && index > 0) pinInputs.value[index - 1]?.focus()
}

const confirmPayment = async () => {
  try {
    const code = pin.value.join('')
    const res = await $api(`/payments/${payment.value.id}/confirm?pin=${code}`, { method: 'POST' })
    payment.value = { ...payment.value, ...res, status: 'confirmed' }
    navigateTo('/payment/success')
  } catch (err: any) {
    console.error(err)
    error.value = err.response?._data?.detail || 'Failed to confirm payment.'
  }
}
</script>
