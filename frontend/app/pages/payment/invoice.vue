<!-- src/pages/payment/invoice.vue -->
<template>
  <AppPage :back-to="'/payment/start'">
    <template #header-center>
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
    </template>

    <!-- Invoice Card -->
    <div class="bg-white rounded-2xl shadow w-full p-6 space-y-5 border border-gray-100">
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
          Balance:
          <span>{{ formatCurrency(accountBalance, accountCurrency || 'USD') }}</span>
          <span class="ml-2 text-xs text-gray-400">
            ({{ accountCurrency || 'USD' }})
          </span>
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
          <span>{{ formatCurrency(amount, invoice?.currency || 'KHR') }}</span>
          <span class="text-sm text-gray-500">
            {{ (invoice?.currency || 'KHR').toUpperCase() }}
          </span>
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

      <p
        v-if="selectedAccountId && invoice && !hasSufficientBalance"
        class="text-red-600 text-sm text-center mt-2"
      >
        Insufficient balance in your selected account.
      </p>
    </div>
  </AppPage>
</template>

<script setup lang="ts">
import AppPage from '~/components/AppPage.vue'
import { useLogoUrl } from '~/composables/useLogoUrl'
import { convertAmount, formatCurrency } from '~/utils/helpers'
import { useMyToast } from '~/composables/useMyToast'


const { $api } = useNuxtApp()
const toast = useMyToast()
const paymentSelection = useState<any>('paymentSelection')

const accounts = ref<any[]>([])
const selectedAccountId = ref<number | null>(null)
const accountBalance = ref<number | null>(null)
const reference = ref('')
const amount = ref<number | null>(null)
const invoice = ref<any>(null)
const fee = ref(10.0)
const invoiceAlreadyPaid = ref(false)
const accountCurrency = ref<string | null>(null)

const { getLogoUrl } = useLogoUrl()

onMounted(async () => {
  try {
    const me = await $api('/me')
    accounts.value = (me.accounts || []).map((a: any) => ({
      ...a,
      balance: Number(a.balance ?? 0),
      currency: (a.currency || 'USD').toUpperCase(),
    }))
    if (accounts.value.length) {
      selectedAccountId.value = accounts.value[0].id
      updateAccountBalance()
    }
  } catch (e) {
    console.error('Failed to load accounts', e)
    toast.show('Failed to load accounts', 'error')
  }
})

const updateAccountBalance = () => {
  const acc = accounts.value.find((a) => a.id === Number(selectedAccountId.value))
  if (acc) {
    accountBalance.value = Number(acc.balance ?? 0)
    accountCurrency.value = (acc.currency || 'USD').toUpperCase()
  } else {
    accountBalance.value = null
    accountCurrency.value = null
  }
}

const lookupInvoice = async () => {
  if (!reference.value) return
  try {
    const res = await $api(`/payments/lookup?reference_number=${reference.value}`)
    invoice.value = res
    amount.value = Number(res.amount)
    invoiceAlreadyPaid.value = false
    toast.show('Invoice loaded successfully', 'success')
  } catch (err: any) {
    invoice.value = null
    amount.value = null

    if (err.response?.status === 423) {
      invoiceAlreadyPaid.value = true
      toast.show('This invoice has already been paid.', 'warning')
      setTimeout(() => {
        reference.value = ''
        invoiceAlreadyPaid.value = false
      }, 2500)
    } else {
      invoiceAlreadyPaid.value = false
      toast.show('Invalid reference number or failed to fetch invoice.', 'error')
    }
  }
}

const hasSufficientBalance = computed(() => {
  if (!selectedAccountId.value || !invoice.value) return true
  const acc = accounts.value.find((a) => a.id === Number(selectedAccountId.value))
  if (!acc) return false

  const acctCurrency = (acc.currency || 'USD').toUpperCase()
  const invoiceCurrency = (invoice.value.currency || 'KHR').toUpperCase()
  const usdToKhrRate = Number(invoice.value.usd_to_khr_rate || 4000)

  const invoiceAmt = Number(invoice.value.amount || 0)
  const invoiceConverted = convertAmount(
    invoiceAmt,
    invoiceCurrency,
    acctCurrency,
    usdToKhrRate,
  )

  const feeConverted = convertAmount(
    Number(fee.value || 0),
    'USD',
    acctCurrency,
    usdToKhrRate,
  )

  const totalNeeded = invoiceConverted + feeConverted
  return Number(acc.balance ?? 0) >= totalNeeded
})

const submitPayment = async () => {
  try {
    const res = await $api(
      `/payments/start?account_id=${selectedAccountId.value}&reference_number=${reference.value}&service_id=${paymentSelection.value.service_id}`,
      { method: 'POST' },
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
      from_account: accounts.value.find(
        (a) => a.id === Number(selectedAccountId.value),
      ),
      invoice_currency: invoice.value.currency,
      invoice_amount: amount.value,
    }

    navigateTo('/payment/confirm')
  } catch {
    toast.show('Failed to start payment', 'error')
  }
}
</script>
