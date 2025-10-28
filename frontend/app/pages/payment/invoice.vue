<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center py-8">
    <!-- Header -->
    <div class="flex gap-10 items-center w-full max-w-md px-4 mb-6">
       <button
        @click="navigateTo('/payment/start')"
        class="p-2 bg-white rounded-full shadow hover:bg-gray-50"
      >
        <ArrowLeft class="w-5 h-5 text-gray-600" />
      </button>
      <div class="flex items-center space-x-3">

     <img
  v-if="paymentSelection?.service?.logo_url"
  :src="getLogoUrl(paymentSelection.service.logo_url)"
  alt="Service Logo"
  class="w-12 h-12 rounded-full object-contain"
/>

        <h2 class="text-lg font-semibold text-gray-700">
          Bill to {{ paymentSelection?.service?.name || '' }}
        </h2>
      </div>

    </div>

    <!-- Bill Form -->
    <div
      class="bg-white rounded-2xl shadow w-full max-w-md p-6 space-y-4 border border-gray-100"
    >
      <!-- Account Selection -->
      <div>
        <label class="block text-sm text-gray-600 mb-1">My Account</label>
        <select
          v-model="selectedAccount"
          class="w-full border border-gray-300 rounded-lg px-3 py-2"
        >
          <option disabled value="">Select account</option>
          <option
            v-for="a in accounts"
            :key="a.id"
            :value="a.id"
          >
            {{ a.number }} — {{ a.name }}
          </option>
        </select>
      </div>

      <!-- Reference Number -->
      <div>
        <label class="block text-sm text-gray-600 mb-1">CDC Ref. No.</label>
        <input
          v-model="reference"
          @blur="lookupInvoice"
          type="text"
          placeholder="Enter Reference"
          class="w-full border border-gray-300 rounded-lg px-3 py-2"
        />
      </div>

      <!-- Amount -->
      <div>
        <label class="block text-sm text-gray-600 mb-1">Amount</label>
        <input
          type="text"
          :value="amountDisplay"
          disabled
          class="w-full border border-gray-200 rounded-lg px-3 py-2 bg-gray-100 text-gray-700"
        />
      </div>

      <!-- Pay Button -->
      <button
        type="submit"
        :disabled="!invoice || !selectedAccount"
        class="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        @click="submitPayment"
      >
        PAY
      </button>

      <!-- Error Message -->
      <p v-if="error" class="text-red-600 text-sm text-center mt-2">
        {{ error }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
const BACKEND_URL = 'http://127.0.0.1:8000'

const getLogoUrl = (path: string) => {
  if (!path) return `${BACKEND_URL}/static/logos/default.png`
  if (path.startsWith('http')) return path
  return `${BACKEND_URL}${path}`
}

const { $api } = useNuxtApp()

// Restore selected service from state
const paymentSelection = useState<any>('paymentSelection')
const accounts = ref<any[]>([])
const reference = ref('')
const amount = ref<number | null>(null)
const invoice = ref<any>(null)
const selectedAccount = ref('')
const error = ref('')

// Display amount as formatted string
const amountDisplay = computed(() =>
  amount.value !== null ? `$${(amount.value / 100).toFixed(2)}` : ''
)

// Fetch user's accounts
onMounted(async () => {
  try {
    const me = await $api('/me')
    accounts.value = me.accounts
  } catch (err) {
    console.error('Failed to load accounts', err)
  }
})

// Lookup invoice details
const lookupInvoice = async () => {
  if (!reference.value) return
  try {
    const res = await $api(`/payments/lookup?reference_number=${reference.value}`)
    invoice.value = res
    amount.value = res.amount_cents
    error.value = ''
  } catch {
    invoice.value = null
    amount.value = null
    error.value = 'Invalid reference number.'
  }
}

// Start payment
const submitPayment = async () => {
  try {
    const res = await $api(
      `/payments/start?account_id=${selectedAccount.value}&reference_number=${reference.value}&service_id=${paymentSelection.value.service_id}`,
      { method: 'POST' }
    )

    useState('payment', () => ({
      id: res.payment_id,
      reference_number: res.reference_number,
      amount_cents: res.amount_cents,
      service: paymentSelection.value.service
    }))

    navigateTo('/payment/pincode')
  } catch (err) {
    console.error('Failed to start payment', err)
    error.value = 'Failed to start payment.'
  }
}
</script>
