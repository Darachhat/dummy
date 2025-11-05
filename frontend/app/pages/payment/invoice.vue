<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center py-8">
    <div class="flex items-center w-full max-w-md mb-6 px-4">
      <button @click="navigateTo('/payment/start')" class="p-2 bg-white rounded-full shadow hover:bg-gray-50">
        <ArrowLeft class="w-5 h-5 text-gray-600" />
      </button>
      <h2 class="mx-auto text-lg font-semibold text-gray-700">Bill Invoice</h2>
    </div>

    <div class="bg-white rounded-2xl shadow w-full max-w-md p-6 space-y-4 border border-gray-100">
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
        <p v-if="accountBalance !== null" class="text-sm text-gray-500 mt-1">
          Balance: {{ formatCurrency(accountBalance) }}
        </p>
      </div>

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

      <div>
        <label class="block text-sm text-gray-600 mb-1">Amount</label>
        <div class="flex items-center justify-between border border-gray-200 rounded-lg px-3 py-2 bg-gray-100 text-gray-700">
          <span>{{ amountDisplay }}</span>
          <span class="text-sm text-gray-500">{{ invoice?.currency || 'USD' }}</span>
        </div>
      </div>

      <button
        :disabled="!invoice || !selectedAccountId || !hasSufficientBalance"
        class="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        @click="submitPayment"
      >
        PAY
      </button>

      <p v-if="selectedAccountId && !hasSufficientBalance" class="text-red-600 text-sm text-center mt-2">
        ⚠️ Insufficient balance in your selected account.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
const { $api } = useNuxtApp()
const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase
const { show } = useToast()

const paymentSelection = useState<any>('paymentSelection')
const accounts = ref<any[]>([])
const selectedAccountId = ref<number | null>(null)
const accountBalance = ref<number | null>(null)
const reference = ref('')
const amount = ref<number | null>(null)
const invoice = ref<any>(null)
const fee = ref(10.0)

const amountDisplay = computed(() => (amount.value ? formatCurrency(amount.value) : ''))

onMounted(async () => {
  try {
    const me = await $api('/me')
    accounts.value = me.accounts || []
    if (accounts.value.length) {
      selectedAccountId.value = accounts.value[0].id
      updateAccountBalance()
    }
  } catch {
    show('Failed to load accounts', 'error')
  }
})

const updateAccountBalance = () => {
  const acc = accounts.value.find(a => a.id === Number(selectedAccountId.value))
  accountBalance.value = acc ? acc.balance : null
}

const formatCurrency = (val: number | null, currency = 'USD') => {
  if (!val) return '—'
  return `${currency} ${val.toLocaleString(undefined, { minimumFractionDigits: 2 })}`
}

const lookupInvoice = async () => {
  if (!reference.value) return
  try {
    const res = await $api(`/payments/lookup?reference_number=${reference.value}`)
    invoice.value = res
    amount.value = Number(res.amount) || 0
    show('Invoice loaded successfully', 'success')
  } catch (err: any) {
    invoice.value = null
    amount.value = null
    show(err.response?.status === 423 ? 'Bill locked, try again later' : 'Invalid reference number.', 'error')
  }
}

const hasSufficientBalance = computed(() => {
  if (!selectedAccountId.value || amount.value === null) return true
  const acc = accounts.value.find(a => a.id === Number(selectedAccountId.value))
  return acc && acc.balance >= amount.value + fee.value
})

const submitPayment = async () => {
  try {
    const res = await $api(
      `/payments/start?account_id=${selectedAccountId.value}&reference_number=${reference.value}&service_id=${paymentSelection.value.service_id}`,
      { method: 'POST' }
    )

    const payment = useState('payment')
    payment.value = {
      id: res.payment_id,
      reference_number: res.reference_number,
      customer_name: res.customer_name,
      amount: Number(res.amount),
      fee: Number(res.fee),
      total_amount: Number(res.total_amount),
      currency: res.currency,
      invoice_amount: Number(res.invoice_amount),
      invoice_currency: res.invoice_currency,
      usd_to_khr_rate: Number(res.usd_to_khr_rate),
      service: paymentSelection.value.service,
      from_account: accounts.value.find(a => a.id === Number(selectedAccountId.value))
    }

    navigateTo('/payment/confirm')
  } catch (err) {
    console.error('Failed to start payment', err)
    show('Failed to start payment.', 'error')
  }
}


</script>
