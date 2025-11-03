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
          <option v-for="a in accounts" :key="a.id" :value="a.id">
            {{ a.number }} — {{ a.name }}
          </option>
        </select>

        <!-- Balance -->
        <p v-if="accountBalance !== null" class="text-sm text-gray-500 mt-1">
          Balance: {{ formatCurrency(accountBalance) }}
        </p>
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
        :disabled="!invoice || !selectedAccountId || !hasSufficientBalance"
        class="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        @click="submitPayment"
      >
        PAY
      </button>

      <!-- Warnings -->
      <p v-if="selectedAccountId && !hasSufficientBalance" class="text-red-600 text-sm text-center mt-2">
        ⚠️ Insufficient balance in your selected account.
      </p>

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
  return path.startsWith('http') ? path : `${BACKEND_URL}${path}`
}

// --- State ---
const paymentSelection = useState<any>('paymentSelection')
const accounts = ref<any[]>([])
const selectedAccountId = ref<number | null>(null)
const accountBalance = ref<number | null>(null)

const reference = ref('')
const amount = ref<number | null>(null)
const invoice = ref<any>(null)
const error = ref('')
const fee = ref(10.0) // fixed fee in USD

// --- Computed ---
const amountDisplay = computed(() => {
  if (amount.value === null) return ''
  return formatCurrency(amount.value)
})

// --- Fetch accounts ---
onMounted(async () => {
  try {
    const me = await $api('/me')
    accounts.value = me.accounts || []
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
  accountBalance.value = acc ? acc.balance : null
}

// --- Format currency ---
const formatCurrency = (val: number | null, currency = 'USD') => {
  if (!val) return '—'
  return `${currency} ${val.toLocaleString(undefined, { minimumFractionDigits: 2 })}`
}

// --- Lookup invoice ---
const lookupInvoice = async () => {
  if (!reference.value) return
  try {
    const res = await $api(`/payments/lookup?reference_number=${reference.value}`)
    invoice.value = res
    amount.value = Number(res.amount) || 0
    error.value = ''
  } catch (err) {
    invoice.value = null
    amount.value = null
    error.value = 'Invalid reference number.'
  }
}

// --- Balance check ---
const hasSufficientBalance = computed(() => {
  if (!selectedAccountId.value || amount.value === null) return true
  const acc = accounts.value.find(a => a.id === Number(selectedAccountId.value))
  if (!acc) return true
  return acc.balance >= amount.value + fee.value
})

// --- Submit ---
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
      amount: res.amount,
      fee: res.fee,
      total_amount: res.total_amount,
      currency: res.currency || 'USD',
      service: paymentSelection.value.service,
      from_account: acc
    }

    navigateTo('/payment/confirm')
  } catch (err) {
    console.error('Failed to start payment', err)
    error.value = 'Failed to start payment.'
  }
}
</script>
