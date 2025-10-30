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
    <div class="bg-white rounded-2xl shadow w-full max-w-md p-6 space-y-4 border border-gray-100">
      <!-- Account Selection -->
      <div>
        <label class="block text-sm text-gray-600 mb-1">My Account</label>
        <select
          v-model.number="selectedAccountId"
          @change="updateAccountBalance"
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

        <!-- Account Balance Display -->
        <p v-if="accountBalance !== null" class="text-sm text-gray-500 mt-1">
          Balance: {{ formatCurrency(accountBalance, selectedCurrency) }}
        </p>
      </div>

      <!-- Reference Number -->
      <div>
        <label class="block text-sm text-gray-600 mb-1">CDC Ref. No.</label>
        <input
          v-model="reference"
          @input="lookupInvoice"
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
        :disabled="!invoice || !selectedAccountId"
        class="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        @click="submitPayment"
      >
        PAY
      </button>

      <!-- Error Message -->
      <p v-if="error" class="text-red-600 text-sm text-center mt-2">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase
const { $api } = useNuxtApp()

const getLogoUrl = (path: string) => {
  if (!path) return `${BACKEND_URL}/static/logos/default.png`
  if (path.startsWith('http')) return path
  return `${BACKEND_URL}${path}`
}

// --- State ---
const paymentSelection = useState<any>('paymentSelection')
const accounts = ref<any[]>([])
const selectedAccountId = ref<number | null>(null)
const accountBalance = ref<number | null>(null)
const selectedCurrency = ref('USD')

const reference = ref('')
const amount = ref<number | null>(null)
const invoice = ref<any>(null)
const error = ref('')

// --- Computed display ---
const amountDisplay = computed(() => {
  if (amount.value === null || !invoice.value) return ''
  const currency = invoice.value.currency || 'USD'
  return formatCurrency(amount.value, currency)
})

// --- Fetch accounts ---
onMounted(async () => {
  try {
    const me = await $api('/me')
    accounts.value = me.accounts
    if (accounts.value.length > 0) {
      selectedAccountId.value = accounts.value[0].id
      updateAccountBalance()
    }
  } catch (err) {
    console.error('Failed to load accounts', err)
  }
})

// --- Update balance ---
const updateAccountBalance = () => {
  const acc = accounts.value.find(a => a.id === Number(selectedAccountId.value))
  accountBalance.value = acc ? acc.balance_cents : null
  selectedCurrency.value = acc ? acc.currency : 'USD'
}

// --- Format currency ---
const formatCurrency = (cents: number | null, currency = 'USD') => {
  if (cents === null) return '—'
  const val = (cents / 100).toLocaleString(undefined, { minimumFractionDigits: 2 })
  return `${currency} ${val}`
}

// --- Lookup invoice 
const lookupInvoice = async () => {
  if (!reference.value) return
  try {
    const res = await $api(`/payments/lookup?reference_number=${reference.value}`)
    invoice.value = res
    amount.value = res.amount_cents ?? res.amount ?? null

    error.value = ''
  } catch {
    invoice.value = null
    amount.value = null
    error.value = 'Invalid reference number.'
  }
}

// --- Submit payment ---
const submitPayment = async () => {
  try {
    const res = await $api(
      `/payments/start?account_id=${selectedAccountId.value}&reference_number=${reference.value}&service_id=${paymentSelection.value.service_id}`,
      { method: 'POST' }
    )

    const acc = accounts.value.find(a => a.id === Number(selectedAccountId.value))

    const payment = useState('payment')
   payment.value = {
  id: res.payment_id,
  reference_number: res.reference_number,
  customer_name: res.customer_name,
  amount_cents: res.amount ?? res.amount_cents,
  fee_cents: res.fee_cents ?? 0,
  total_amount_cents: res.total_amount_cents ??
    ((res.amount ?? res.amount_cents) + (res.fee_cents ?? 0)),
  currency: res.currency || 'USD',
  service: paymentSelection.value.service,
  from_account: {
    id: acc?.id || selectedAccountId.value,
    number: acc?.number || '',
    name: acc?.name || '',
    balance_cents: acc?.balance_cents || 0,
  }
}

    navigateTo('/payment/confirm')
  } catch (err) {
    console.error('Failed to start payment', err)
    error.value = 'Failed to start payment.'
  }
}
</script>
