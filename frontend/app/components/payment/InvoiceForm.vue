<template>
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
      :disabled="!invoice || !selectedAccountId || !hasSufficientBalance || isLoading"
      class="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
      @click="submitPayment"
    >
      <span v-if="!isLoading">PAY</span>
      <span v-else>Processing...</span>
    </button>

    <p v-if="selectedAccountId && !hasSufficientBalance" class="text-red-600 text-sm text-center mt-2">
      ⚠️ Insufficient balance.
    </p>

    <transition name="fade" mode="out-in">
      <p v-if="error" key="error" class="text-red-600 text-sm text-center mt-2">{{ error }}</p>
    </transition>
  </div>
</template>

<script setup lang="ts">
const { $api } = useNuxtApp()
const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase

// Props
const props = defineProps({
  service: Object
})

// Emits
const emit = defineEmits(['payment-started'])

// State
const accounts = ref<any[]>([])
const selectedAccountId = ref<number | null>(null)
const accountBalance = ref<number | null>(null)
const reference = ref('')
const amount = ref<number | null>(null)
const invoice = ref<any>(null)
const error = ref('')
const isLoading = ref(false)
const fee = ref(10.0)

// Computed
const amountDisplay = computed(() => {
  if (amount.value === null) return ''
  return formatCurrency(amount.value)
})
const hasSufficientBalance = computed(() => {
  if (!selectedAccountId.value || amount.value === null) return true
  const acc = accounts.value.find(a => a.id === Number(selectedAccountId.value))
  return acc ? acc.balance >= amount.value + fee.value : true
})

// Methods
const formatCurrency = (val: number | null) => {
  if (!val) return '—'
  return `USD ${val.toLocaleString(undefined, { minimumFractionDigits: 2 })}`
}
const updateAccountBalance = () => {
  const acc = accounts.value.find(a => a.id === Number(selectedAccountId.value))
  accountBalance.value = acc ? acc.balance : null
}

const lookupInvoice = async () => {
  if (!reference.value) return
  try {
    const res = await $api(`/payments/lookup?reference_number=${reference.value}`)
    invoice.value = res
    amount.value = Number(res.amount) || 0
    error.value = ''
  } catch (err: any) {
    invoice.value = null
    amount.value = null
    if (err.response?.status === 423) {
      error.value = 'This bill is being processed. Please try again later.'
    } else if (err.response?.status === 400) {
      error.value = 'Invalid or expired reference number.'
    } else {
      error.value = 'Failed to lookup invoice.'
    }
  }
}

const submitPayment = async () => {
  isLoading.value = true
  try {
    const res = await $api(
      `/payments/start?account_id=${selectedAccountId.value}&reference_number=${reference.value}&service_id=${props.service.id}`,
      { method: 'POST' }
    )
    const acc = accounts.value.find(a => a.id === Number(selectedAccountId.value))
    emit('payment-started', { res, from_account: acc })
  } catch {
    error.value = 'Failed to start payment.'
  } finally {
    isLoading.value = false
  }
}

// Init
onMounted(async () => {
  const me = await $api('/me')
  accounts.value = me.accounts || []
  if (accounts.value.length > 0) {
    selectedAccountId.value = accounts.value[0].id
    updateAccountBalance()
  }
})
</script>
