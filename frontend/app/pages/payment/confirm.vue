<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
    <!-- Header -->
    <div class="relative flex items-center justify-center w-full max-w-lg mb-8">
      <button
        @click="navigateTo('/payment/invoice')"
        class="absolute left-4 p-2 bg-white rounded-full shadow hover:bg-gray-100 transition"
      >
        <ArrowLeft class="w-5 h-5 text-gray-700" />
      </button>
      <h2 class="text-xl font-semibold text-gray-800 text-center">Confirm Payment</h2>
    </div>

    <!-- Confirmation Card -->
    <div class="bg-white rounded-2xl shadow w-full max-w-lg p-6 space-y-5 text-center border border-gray-100">
      <!-- Service Logo -->
      <div v-if="payment?.service?.logo_url" class="flex justify-center mb-3">
        <img
          :src="getLogoUrl(payment.service.logo_url)"
          alt="Service Logo"
          class="w-20 h-20 object-contain rounded-full"
        />
      </div>

      <!-- Service Name -->
      <h3 class="text-lg font-semibold text-gray-800">
        Bill to {{ payment?.service?.name || 'Service' }}
      </h3>

      <!-- Bill Info -->
      <div class="text-left text-sm space-y-4">
        <div class="flex justify-between">
          <span class="text-gray-500">From Account</span>
          <span class="font-medium text-gray-800">{{ payment?.from_account?.number }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Customer Name</span>
          <span class="font-medium text-gray-800">{{ payment?.customer_name }}</span>
        </div>
        <div class="dotted-divider"></div>

        <div class="flex justify-between">
          <span class="text-gray-500">CDC. Ref. No.</span>
          <span class="font-medium text-gray-800">{{ payment?.reference_number }}</span>
        </div>

        <div class="flex justify-between items-start">
          <span class="text-gray-500">Amount</span>
          <div class="text-right">
            <p class="font-medium text-gray-800">
              {{ formatCurrency(payment?.invoice_amount) }} {{ payment?.invoice_currency }}
            </p>
            <p v-if="payment?.invoice_currency === 'KHR'" class="text-xs text-gray-500">
              ≈ {{ formatCurrency(convertToUSD(payment?.invoice_amount)) }} USD
            </p>
          </div>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Fee</span>
          <span class="font-medium text-gray-800">{{ formatCurrency(payment?.fee) }} USD</span>
        </div>
        <div class="dotted-divider"></div>


        <div class="flex justify-between text-base font-semibold">
          <span>Total Amount</span>
          <div class="text-right">
            <p>{{ formatCurrency(payment?.total_amount) }} USD</p>
            <p v-if="payment?.invoice_currency === 'KHR'" class="text-xs text-gray-500">
              ≈ {{ formatCurrency(payment?.invoice_amount + (payment?.fee * USD_TO_KHR_RATE)) }} KHR
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- PIN Input -->
    <div class="bg-white rounded-2xl shadow w-full max-w-lg p-6 text-center mt-8 border border-gray-100">
      <p class="text-sm text-gray-600 mb-4">Enter your 4-digit PIN to confirm payment</p>

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
        :disabled="pin.join('').length < 4 || confirming"
        @click="confirmPayment"
        class="w-full py-2 bg-gradient-to-r from-gray-800 to-gray-900 text-white rounded-lg hover:opacity-90 disabled:opacity-50 transition"
      >
        <span v-if="confirming">Confirming...</span>
        <span v-else>Confirm Payment</span>
      </button>

      <p v-if="error" class="text-red-600 text-sm mt-3">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowLeft } from 'lucide-vue-next'
import { formatCurrency, convertToUSD, USD_TO_KHR_RATE } from '~/utils/helpers'

const { $api } = useNuxtApp()
const payment = useState<any>('payment')
const pin = ref<string[]>(['', '', '', ''])
const pinInputs = ref<HTMLInputElement[]>([])
const confirming = ref(false)
const error = ref('')
const { show } = useToast()
const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase

const getLogoUrl = (path: string) =>
  !path
    ? `${BACKEND_URL}/static/logos/default.svg`
    : path.startsWith('http')
    ? path
    : `${BACKEND_URL}${path}`

const handleInput = (index: number, e: Event) => {
  const el = e.target as HTMLInputElement
  pin.value[index] = el.value
  if (el.value && index < 3) pinInputs.value[index + 1]?.focus()
}

const handleBackspace = (index: number, e: KeyboardEvent) => {
  const el = e.target as HTMLInputElement
  if (!el.value && index > 0) pinInputs.value[index - 1]?.focus()
}

const confirmPayment = async () => {
  if (!payment.value?.id) {
    show('Invalid payment session. Please start again.', 'error')
    navigateTo('/payment/invoice')
    return
  }

  confirming.value = true
  try {
    const code = pin.value.join('')
    const res = await $api(`/payments/${payment.value.id}/confirm?pin=${code}`, {
      method: 'POST',
    })
    payment.value = { ...payment.value, ...res, status: 'confirmed' }
    show('Payment confirmed successfully!', 'success')
    navigateTo('/payment/success')
  } catch (err: any) {
    error.value = err.response?._data?.detail || 'Failed to confirm payment.'
    show(error.value, 'error')
  } finally {
    confirming.value = false
  }
}
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
