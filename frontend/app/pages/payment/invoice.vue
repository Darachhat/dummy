<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
    <!-- Header -->
    <div class="relative flex items-center justify-center w-full max-w-lg mb-8">
      <button
        @click="navigateTo('/payment/start')"
        class="absolute left-4 p-2 bg-white rounded-full shadow hover:bg-gray-100 transition"
      >
        <ArrowLeft class="w-5 h-5 text-gray-700" />
      </button>

      <div class="flex items-center gap-2">
        <img
          v-if="paymentSelection?.service?.logo_url"
          :src="getLogoUrl(paymentSelection.service.logo_url)"
          alt="Service Logo"
          class="w-7 h-7 rounded-full object-contain"
        />
        <h2 class="text-xl font-semibold text-gray-800 text-center">
          Bill to {{ paymentSelection?.service?.name || 'Service' }}
        </h2>
      </div>
    </div>

    <!-- Invoice Card -->
    <div class="bg-white rounded-2xl shadow w-full max-w-lg p-6 space-y-5 border border-gray-100">
      <!-- Account Selection -->
      <div>
        <label class="block text-sm text-gray-600 mb-1">My Account</label>
        <select
          v-model.number="selectedAccountId"
          @change="updateAccountBalance"
          class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
        >
          <option disabled value="">Select account</option>
          <option v-for="a in accounts" :key="a.id" :value="a.id">
            {{ a.number }} — {{ a.name }}
          </option>
        </select>
        <p v-if="accountBalance !== null" class="text-sm text-gray-500 mt-1">
          Balance: {{ formatCurrency(accountBalance) }} USD
        </p>
      </div>

      <!-- Reference Number -->
      <div>
        <label class="block text-sm text-gray-600 mb-1">CDC Ref. No.</label>
        <input
          v-model="reference"
          @blur="lookupInvoice"
          type="text"
          placeholder="Enter Reference Number"
          class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
        />

        <!-- Already Paid Notice -->
        <transition name="fade">
          <div
            v-if="invoiceAlreadyPaid"
            class="flex items-center justify-center text-yellow-800 bg-yellow-100 border border-yellow-300 rounded-lg p-3 text-sm mt-2"
          >
            This invoice has already been paid. Reference will be reset.
          </div>
        </transition>
      </div>

      <!-- Amount -->
      <div>
        <label class="block text-sm text-gray-600 mb-1">Amount</label>
        <div
          class="flex items-center justify-between border border-gray-200 rounded-lg px-3 py-2 bg-gray-100 text-gray-700"
        >
          <span>{{ formatCurrency(amount) }}</span>
          <span class="text-sm text-gray-500">{{ invoice?.currency || 'KHR' }}</span>
        </div>
      </div>

      <!-- PAY Button -->
      <button
        :disabled="!invoice || !selectedAccountId || !hasSufficientBalance || invoiceAlreadyPaid"
        class="w-full py-2 bg-gradient-to-r from-gray-800 to-gray-900 text-white rounded-lg hover:opacity-90 transition disabled:opacity-50"
        @click="submitPayment"
      >
        Pay Now
      </button>

      <!-- Insufficient balance -->
      <p
        v-if="selectedAccountId && !hasSufficientBalance"
        class="text-red-600 text-sm text-center mt-2"
      >
        Insufficient balance in your selected account.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowLeft } from 'lucide-vue-next'
import { formatCurrency } from '~/utils/helpers'
import { convertToUSD } from '~/utils/helpers'

const { $api } = useNuxtApp()
const { show } = useToast()
const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase
const paymentSelection = useState<any>('paymentSelection')
const accounts = ref<any[]>([])
const selectedAccountId = ref<number | null>(null)
const accountBalance = ref<number | null>(null)
const reference = ref('')
const amount = ref<number | null>(null)
const invoice = ref<any>(null)
const fee = ref(10.0)
const invoiceAlreadyPaid = ref(false)

const getLogoUrl = (path: string) =>
  !path
    ? `${BACKEND_URL}/static/logos/default.svg`
    : path.startsWith('http')
    ? path
    : `${BACKEND_URL}${path}`

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

const lookupInvoice = async () => {
  if (!reference.value) return
  try {
    const res = await $api(`/payments/lookup?reference_number=${reference.value}`)
    invoice.value = res
    amount.value = Number(res.amount)
    invoiceAlreadyPaid.value = false
    show('Invoice loaded successfully', 'success')
  } catch (err: any) {
    invoice.value = null
    amount.value = null

    if (err.response?.status === 423) {
      invoiceAlreadyPaid.value = true
      show('This invoice has already been paid.', 'warning')
      setTimeout(() => {
        reference.value = ''
        invoiceAlreadyPaid.value = false
      }, 2500)
    } else {
      invoiceAlreadyPaid.value = false
      show('Invalid reference number or failed to fetch invoice.', 'error')
    }
  }
}

const hasSufficientBalance = computed(() => {
  if (!selectedAccountId.value || amount.value === null) return true
  const acc = accounts.value.find(a => a.id === Number(selectedAccountId.value))
  const amountUSD = convertToUSD(amount.value)
  return acc && acc.balance >= amountUSD + fee.value
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
      amount: res.amount,
      fee: res.fee,
      total_amount: res.total_amount,
      currency: res.currency,
      service: paymentSelection.value.service,
      from_account: accounts.value.find(a => a.id === Number(selectedAccountId.value)),
      invoice_currency: invoice.value.currency,
      invoice_amount: amount.value,
    }

    navigateTo('/payment/confirm')
  } catch {
    show('Failed to start payment', 'error')
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
