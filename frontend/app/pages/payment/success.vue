<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center justify-center text-center px-4 py-10">
    <!-- Success Header -->
    <div class="bg-white rounded-2xl shadow w-full max-w-lg mb-6 p-8">
      <div class="flex justify-center items-center mb-6 relative">
        <div class="bg-green-100 rounded-full w-20 h-20 flex items-center justify-center">
          <Check class="w-10 h-10 text-green-600" />
        </div>
      </div>

      <h1 class="text-2xl font-bold text-gray-800 mb-2">Payment Successful!</h1>
      <p class="text-gray-600">Your payment was processed successfully.</p>
    </div>

    <!-- Payment Summary -->
    <div class="bg-white shadow rounded-2xl border border-gray-100 p-6 w-full max-w-lg text-left">
      <div class="flex items-center gap-3 mb-5">
        <img
          v-if="payment?.service?.logo_url"
          :src="getLogoUrl(payment.service.logo_url)"
          alt="Service Logo"
          class="w-10 h-10 rounded-full object-contain"
        />
        <div>
          <h3 class="text-lg font-semibold text-gray-800">
            {{ payment?.service?.name || 'Service' }}
          </h3>
          <p class="text-sm text-gray-500">Transaction Receipt</p>
        </div>
      </div>

      <div class="space-y-3 text-sm">

        <div class="flex justify-between">
          <span class="text-gray-500">From Account</span>
          <span class="font-medium text-gray-800">{{ payment?.from_account?.number }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">CDC. Ref. No.</span>
          <span class="font-medium text-gray-800">{{ payment?.reference_number }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Customer Name</span>
          <span class="font-medium text-gray-800">{{ payment?.customer_name }}</span>
        </div>
        <div class="w-full flex items-center justify-center my-3">
          <div class="dotted-divider w-full"></div>
        </div>


        <div class="flex justify-between">
          <span class="text-gray-500">Amount</span>
          <span class="font-medium text-gray-800">
             {{ formatCurrency(payment?.invoice_amount, payment?.invoice_currency) }}
          </span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Fee</span>
          <span class="font-medium text-gray-800">
            {{ formatCurrency(payment?.fee) }}
          </span>
        </div>

       <div class="w-full flex items-center justify-center my-3">
        <div class="dotted-divider w-full"></div>
      </div>


        <div class="flex justify-between text-base font-semibold">
  <span>Total Paid</span>
  <span class="text-gray-900">{{ formatCurrency(payment?.total_amount, payment?.currency || 'USD') }}</span>
</div>
         <div class="w-full flex items-center justify-center my-3">
            <div class="dotted-divider w-full"></div>
          </div>


        <div class="flex justify-between ">
          <span>Bank TID</span>
          <span class="text-gray-500">
            {{ payment?.transaction_id || 'N/A' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex flex-col gap-3 w-full max-w-lg mt-8">
      <button
        @click="navigateTo('/')"
        class="w-full py-2 bg-gradient-to-r from-gray-800 to-gray-900 text-white rounded-lg hover:opacity-90 transition"
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
import { Check } from 'lucide-vue-next'
import { formatCurrency } from '~/utils/helpers'

const payment = useState<any>('payment')
const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase

const getLogoUrl = (path: string) =>
  !path
    ? `${BACKEND_URL}/static/logos/default.png`
    : path.startsWith('http')
    ? path
    : `${BACKEND_URL}${path}`
</script>
