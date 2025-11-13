<!-- pages/adm/users/[id].vue -->
<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="hidden md:flex justify-between items-center">
      <div class="flex items-center gap-3">
        <NuxtLink to="/adm/users" class="px-3 py-1 border rounded-xl hover:bg-gray-50">Back</NuxtLink>
        <h2 class="text-2xl font-bold text-gray-800">{{ form.name }}</h2>
      </div>
      <UButton class="btn-dark" icon="i-lucide-save" :loading="saving" @click="saveUser">Save</UButton>
    </div>

    <!-- Alerts -->
    <UAlert v-if="errorMsg" color="red" :title="errorMsg" icon="i-lucide-alert-triangle" />
    <UAlert v-if="successMsg" color="green" :title="successMsg" icon="i-lucide-check" />

    <!-- USER INFO -->
    <UCard class="border rounded-2xl">
      <template #header>
        <div class="flex items-center justify-between">
          <span class="font-semibold">Edit User Info</span>
          <span class="text-xs text-gray-500">ID: {{ id }}</span>
        </div>
      </template>

      <div class="grid md:grid-cols-2 gap-4">
        <UFormField label="Name">
          <UInput v-model.trim="form.name" color="neutral" placeholder="Full name" @blur="touched = true" />
        </UFormField>

        <UFormField label="Phone">
          <UInput v-model.trim="form.phone" inputmode="tel" color="neutral" placeholder="Phone number" @input="digitsPhone" @blur="touched = true" />
        </UFormField>

        <UFormField label="Role">
          <USelect
            v-model="form.role"
            color="neutral"
            :items="[{ label: 'User', value: 'user' }, { label: 'Admin', value: 'admin' }]"
            placeholder="Select role"
          />
        </UFormField>

        <UFormField label="New Password (optional)">
          <div class="relative">
            <UInput
              :type="showPwd ? 'text' : 'password'"
              v-model.trim="form.password"
              placeholder="Leave blank to keep current"
              color="neutral"
            />
            <UButton
              type="button"
              variant="ghost"
              class="absolute right-1 top-1/2 -translate-y-1/2 text-gray-800 hover:text-gray-700 active:text-gray-900 transition"
              :icon="showPwd ? 'i-lucide-eye-off' : 'i-lucide-eye'"
              @click="showPwd = !showPwd"
            />
          </div>
        </UFormField>
      </div>

      <template #footer>
        <div class="flex justify-end gap-2">
          <UButton class="btn-dark" :loading="saving" @click="saveUser">Save Changes</UButton>
        </div>
      </template>
    </UCard>

    <!-- ACCOUNTS -->
    <UCard class="border rounded-2xl">
      <template #header>
        <div class="flex items-center justify-between">
          <span class="font-semibold">User Accounts</span>
          <div class="flex gap-2">
            <UButton size="sm" class="btn-dark" icon="i-lucide-plus" @click="showAddAccount = true">Add Account</UButton>
          </div>
        </div>
      </template>

      <UTable :data="accounts" :columns="accountColumns" :loading="accPending" class="min-w-full">
        <template #balance-cell="{ row }">
          {{ formatMoney(row.original.balance, row.original.currency || 'USD') }}
        </template>

        <template #actions-cell="{ row }">
          <div class="flex justify-start">
            <UButton
              size="sm"
              variant="outline"
              color="neutral"
              icon="i-lucide-edit"
              label="Edit Balance"
              @click="openEditBalance(row.original)"
            />
          </div>
        </template>

        <template #empty>
          <div class="text-center py-6 text-gray-500">No accounts found</div>
        </template>
      </UTable>
    </UCard>

    <!-- TRANSACTIONS -->
    <UCard class="border rounded-2xl">
      <template #header>
        <div class="flex items-center justify-between">
          <span class="font-semibold">Transactions</span>
        </div>
      </template>

      <UTable :data="txs" :columns="transactionColumns" :loading="txPending" class="min-w-full">
        <template #reference_number-cell="{ row }">
          <div class="truncate max-w-xs">{{ row.original?.reference_number ?? '-' }}</div>
        </template>

        <template #service_name-cell="{ row }">
          <div class="flex items-center gap-2">
            <img
              v-if="row.original?.service_logo_url"
              :src="getLogoUrl(row.original.service_logo_url)"
              class="w-6 h-6 rounded-full object-contain"
            />
            <span>{{ row.original?.service_name ?? '-' }}</span>
          </div>
        </template>

        <template #amount-cell="{ row }">
          <!-- Amount = invoice/original amount with its invoice currency -->
          {{ formatMoney(row.original?.amount, row.original?.currency || 'USD') }}
        </template>

        <template #total_amount-cell="{ row }">
          <!-- Total = USD-debited amount (total_amount) -->
          {{ formatMoney(row.original?.total_amount, 'USD') }}
        </template>

        <template #created_at-cell="{ row }">
          {{ formatDate(row.original?.created_at ?? row.original?.cdc_transaction_datetime) }}
        </template>

        <template #empty>
          <div class="text-center py-6 text-gray-500">No transactions found</div>
        </template>
      </UTable>

      <template #footer>
        <div class="flex justify-between items-center text-sm text-gray-600">
          <span>Showing {{ txs.length }} of {{ txTotal }} — Page {{ txPage }} / {{ txTotalPages }}</span>
          <div class="flex gap-2">
            <UButton size="sm" variant="outline" color="neutral" :disabled="txPage<=1 || txPending" @click="goTx(txPage-1)">Prev</UButton>
            <UButton size="sm" class="btn-dark" :disabled="txPage>=txTotalPages || txPending" @click="goTx(txPage+1)">Next</UButton>
          </div>
        </div>
      </template>
    </UCard>

    <!-- PAYMENTS -->
    <UCard class="border rounded-2xl">
      <template #header>
        <div class="flex items-center justify-between">
          <span class="font-semibold">Payments</span>
        </div>
      </template>

      <UTable :data="pays" :columns="paymentColumns" :loading="payPending" class="min-w-full">
        <template #reference_number-cell="{ row }">
          <div class="truncate max-w-xs">{{ row.original?.reference_number ?? '-' }}</div>
        </template>

        <template #method-cell="{ row }">
          {{ row.original?.method ?? row.original?.payment_method ?? '-' }}
        </template>

        <template #amount-cell="{ row }">
          <!-- Amount: show original/invoice amount + invoice currency -->
          {{ formatMoney(row.original?.amount, row.original?.currency || 'USD') }}
        </template>

        <template #created_at-cell="{ row }">
          {{ formatDate(row.original?.created_at ?? row.original?.cdc_payment_datetime) }}
        </template>

        <template #status-cell="{ row }">
          <UBadge :label="row.original?.status ?? 'unknown'" :color="(row.original?.status === 'paid' || row.original?.status === 'confirmed') ? 'green' : 'orange'" />
        </template>

        <template #actions-cell="{ row }">
          <UButton size="sm" variant="outline" color="neutral" @click="openPaymentDetail(row.original)">Details</UButton>
        </template>

        <template #empty>
          <div class="text-center py-6 text-gray-500">No payments found</div>
        </template>
      </UTable>

      <template #footer>
        <div class="flex justify-between items-center text-sm text-gray-600">
          <span>Showing {{ pays.length }} of {{ payTotal }} — Page {{ payPage }} / {{ payTotalPages }}</span>
          <div class="flex gap-2">
            <UButton size="sm" variant="outline" color="neutral" :disabled="payPage<=1 || payPending" @click="goPay(payPage-1)">Prev</UButton>
            <UButton size="sm" class="btn-dark" :disabled="payPage>=payTotalPages || payPending" @click="goPay(payPage+1)">Next</UButton>
          </div>
        </div>
      </template>
    </UCard>

    <!-- ADD ACCOUNT MODAL -->
    <UModal v-model:open="showAddAccount" title="Add Account">
      <template #body>
        <div class="space-y-4">
          <UFormField label="Name" required>
            <UInput color="neutral" v-model.trim="newAccount.name" placeholder="e.g. Main Wallet" />
          </UFormField>
          <UFormField label="Account Number" required>
            <UInput color="neutral" v-model.trim="newAccount.number" placeholder="e.g. 000-000-000 " />
          </UFormField>
          <div class="grid sm:grid-cols-2 gap-4">
            <UFormField label="Initial Balance" required>
              <UInput color="neutral" v-model.number="newAccount.balance" inputmode="decimal" placeholder="0.00" />
            </UFormField>
            <UFormField label="Currency" required>
              <USelect color="neutral" v-model="newAccount.currency" :items="currencyOptions" placeholder="Select currency" />
            </UFormField>
          </div>
        </div>
      </template>
      <template #footer>
        <div class="flex justify-end gap-2">
          <UButton variant="outline" color="neutral" @click="showAddAccount=false">Cancel</UButton>
          <UButton class="btn-dark" :disabled="!newAccount.name || !newAccount.number" :loading="addingAcc" @click="addAccount">
            Add
          </UButton>
        </div>
      </template>
    </UModal>

    <!-- EDIT BALANCE MODAL -->
    <UModal v-model:open="showEditBalance" :title="`Edit Balance — ${editingAcc?.number || editingAcc?.name || ''}`">
      <template #body>
        <UFormField label="New Balance">
          <UInput color="neutral" v-model.number="editBalanceValue" inputmode="decimal" placeholder="0.00" />
        </UFormField>
      </template>
      <template #footer>
        <div class="flex justify-end gap-2">
          <UButton variant="outline" color="neutral" @click="showEditBalance=false">Cancel</UButton>
          <UButton class="btn-dark" :loading="savingAcc" @click="saveBalance">Save</UButton>
        </div>
      </template>
    </UModal>

    <!-- PAYMENT DETAIL MODAL -->
    <UModal v-model:open="showPaymentDetail" title="Payment Details" class="max-w-2xl">
      <template #header>
        <div class="flex items-center justify-between w-full">
          <div class="flex items-center gap-3">
            <div class="text-sm text-gray-600">Reference</div>
            <div class="font-medium text-lg break-all">{{ selectedPayment?.reference_number ?? '-' }}</div>
          </div>

          <div class="flex items-center gap-3">
            <UBadge :label="selectedPayment?.status ?? 'unknown'" :color="statusVariant" />
            <div v-if="selectedPayment?.service_name" class="flex items-center gap-2">
              <img
                v-if="selectedPayment?.service_logo_url"
                :src="getLogoUrl(selectedPayment.service_logo_url)"
                alt="service"
                class="w-8 h-8 rounded-md object-contain border"
              />
              <div class="text-sm text-gray-700">{{ selectedPayment?.service_name }}</div>
            </div>
          </div>
        </div>
      </template>

      <template #body>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div class="space-y-2">
            <label class="text-xs text-gray-500">Session ID</label>
            <div class="flex items-center gap-2">
              <div class="truncate text-slate-700">{{ selectedPayment?.session_id ?? '-' }}</div>
              <UButton size="sm" variant="ghost" color="neutral" icon="i-lucide-copy" :disabled="!selectedPayment?.session_id" @click="copyField(selectedPayment?.session_id, 'Session ID')" />
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-xs text-gray-500">Acknowledgement ID</label>
            <div class="flex items-center gap-2">
              <div class="truncate text-slate-700">{{ selectedPayment?.acknowledgement_id ?? '-' }}</div>
              <UButton size="sm" color="neutral" variant="ghost" icon="i-lucide-copy" :disabled="!selectedPayment?.acknowledgement_id" @click="copyField(selectedPayment?.acknowledgement_id, 'Acknowledgement ID')" />
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-xs text-gray-500">CDC Transaction Datetime</label>
            <div class="flex items-center gap-2">
              <div class="truncate text-slate-700">{{ selectedPayment?.cdc_transaction_datetime ?? selectedPayment?.created_at ?? '-' }}</div>
              <UButton size="sm" variant="ghost" color="neutral" icon="i-lucide-copy" :disabled="!(selectedPayment?.cdc_transaction_datetime || selectedPayment?.created_at)" @click="copyField(selectedPayment?.cdc_transaction_datetime ?? selectedPayment?.created_at, 'CDC local')" />
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-xs text-gray-500">CDC Transaction Datetime UTC</label>
            <div class="flex items-center gap-2">
              <div class="truncate text-slate-700">{{ selectedPayment?.cdc_transaction_datetime_utc ?? '-' }}</div>
              <UButton size="sm" variant="ghost" color="neutral" icon="i-lucide-copy" :disabled="!selectedPayment?.cdc_transaction_datetime_utc" @click="copyField(selectedPayment?.cdc_transaction_datetime_utc, 'CDC UTC')" />
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-xs text-gray-500">Reversal Transaction ID</label>
            <div class="flex items-center gap-2">
              <div class="truncate text-slate-700">{{ selectedPayment?.reversal_transaction_id ?? '-' }}</div>
              <UButton size="sm" variant="ghost" color="neutral" icon="i-lucide-copy" :disabled="!selectedPayment?.reversal_transaction_id" @click="copyField(selectedPayment?.reversal_transaction_id, 'Reversal Tx')" />
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-xs text-gray-500">Reversal Acknowledgement ID</label>
            <div class="flex items-center gap-2">
              <div class="truncate text-slate-700">{{ selectedPayment?.reversal_acknowledgement_id ?? '-' }}</div>
              <UButton size="sm" variant="ghost" color="neutral" icon="i-lucide-copy" :disabled="!selectedPayment?.reversal_acknowledgement_id" @click="copyField(selectedPayment?.reversal_acknowledgement_id, 'Reversal Ack')" />
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-xs text-gray-500">Confirmed At</label>
            <div class="text-slate-700">{{ selectedPayment?.confirmed_at ?? '-' }}</div>
          </div>

          <div class="space-y-2">
            <label class="text-xs text-gray-500">Created At</label>
            <div class="text-slate-700">{{ selectedPayment?.created_at ?? '-' }}</div>
          </div>

          <div class="col-span-1 sm:col-span-2 pt-2">
            <label class="text-xs text-gray-500">Raw </label>
            <div class="mt-1 p-3 bg-gray-50 rounded-md text-xs text-gray-700 break-words max-h-36 overflow-auto">
              <pre class="whitespace-pre-wrap text-xs m-0">{{ JSON.stringify(selectedPayment?.original ?? selectedPayment ?? {}, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </template>

      <template #footer>
        <div class="flex items-center justify-between w-full">
          <div class="flex gap-2">
            <UButton variant="outline" color="neutral" @click="copyField(selectedPayment?.reference_number, 'Reference')" :disabled="!selectedPayment?.reference_number">
              <i class="i-lucide-copy mr-2"></i> Copy Reference
            </UButton>
            <UButton variant="outline" color="neutral" @click="openTransaction(selectedPayment?.id ?? selectedPayment?.transaction_id)" :disabled="!selectedPayment?.transaction_id">
              <i class="i-lucide-external-link mr-2"></i> Open Transaction
            </UButton>
          </div>

          <div class="flex gap-2">
            <UButton variant="ghost" color="neutral" @click="showPaymentDetail = false">Close</UButton>
            <UButton class="btn-dark" @click="showPaymentDetail = false">Done</UButton>
          </div>
        </div>
      </template>
    </UModal>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin' })

const route = useRoute()
const id = computed(() => String(route.params.id))
const { $api } = useNuxtApp()
const toast = useMyToast()

/* ---------- State ---------- */
const original = ref<any>(null)
const form = reactive({ name: '', phone: '', role: 'user', password: '' })
const touched = ref(false)
const showPwd = ref(false)
const saving = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

/* Accounts */
const accounts = ref<any[]>([])
const accPending = ref(false)
const showAddAccount = ref(false)
const addingAcc = ref(false)
const newAccount = reactive({ name: '', number: '', balance: 0, currency: 'USD', type: 'wallet' })
const currencyOptions = ref<string[]>(['USD'])
const showEditBalance = ref(false)
const editingAcc = ref<any | null>(null)
const editBalanceValue = ref<number | null>(null)
const savingAcc = ref(false)
const accountColumns = [
  { accessorKey: 'name', header: 'Account Name' },
  { accessorKey: 'number', header: 'Account Number' },
  { accessorKey: 'currency', header: 'Currency' },
  { accessorKey: 'balance', header: 'Balance' },
  { id: 'actions', header: 'Actions' },
]

/* Transactions */
const txs = ref<any[]>([])
const txPending = ref(false)
const txPage = ref(1)
const txPageSize = 10
const txTotal = ref(0)
const txQ = ref('')
const transactionColumns = [
  { accessorKey: 'transaction_id', header: 'Transaction ID' },
  { accessorKey: 'reference_number', header: 'Reference' },
  { accessorKey: 'service_name', header: 'Service' },
  { accessorKey: 'fee', header: 'Fee' },
  { accessorKey: 'amount', header: 'Amount' },
  { accessorKey: 'total_amount', header: 'Total' },
  { accessorKey: 'created_at', header: 'Date' },
]

const txTotalPages = computed(() => Math.max(1, Math.ceil(txTotal.value / txPageSize)))

/* Payments */
const pays = ref<any[]>([])
const payPending = ref(false)
const payPage = ref(1)
const payPageSize = 10
const payTotal = ref(0)
const payQ = ref('')
const showPaymentDetail = ref(false)
const selectedPayment = ref<any | null>(null)
const paymentColumns = [
  { accessorKey: 'transaction_id', header: 'Transaction ID' },
  { accessorKey: 'reference_number', header: 'Reference' },
  { accessorKey: 'amount', header: 'Amount' },
  { accessorKey: 'status', header: 'Status' },
  { accessorKey: 'created_at', header: 'Date' },
  { id: 'actions', header: 'Details' }
]

const payTotalPages = computed(() => Math.max(1, Math.ceil(payTotal.value / payPageSize)))

function openPaymentDetail(p: any) {
  selectedPayment.value = p
  showPaymentDetail.value = true
}

/* ---------- Utils ---------- */
function formatDate(s?: string) { return s ? new Date(s).toLocaleString() : '-' }

/**
 * formatMoney(value, currency)
 * - KHR => "1,234 ៛" (no decimals)
 * - USD/other currencies => localized currency formatting
 * - fallback: number with currency code
 */
function formatMoney(n?: number | string | null, c: string = 'USD') {
  if (n === null || n === undefined || n === '') return '-'
  // convert string numbers with commas to number
  const num =
    typeof n === 'number'
      ? n
      : (typeof n === 'string' && n.trim() !== '') ? Number(String(n).replace(/,/g, '')) : NaN
  if (!isFinite(num)) return '-'

  const cur = (c || 'USD').toString().toUpperCase()

  // Special formatting for KHR (no decimals, append Khmer symbol)
  if (cur === 'KHR' || cur === 'RIEL' || cur === '៛') {
    const intVal = Math.round(num)
    return intVal.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 }) + ' ៛'
  }

  try {
    return new Intl.NumberFormat(undefined, { style: 'currency', currency: cur, minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(num)
  } catch (e) {
    // fallback: numeric + currency code
    return num.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ` ${cur}`
  }
}

function digitsPhone(e: any) {
  const v = e?.target?.value ?? ''
  form.phone = v.startsWith('+') ? ('+' + v.slice(1).replace(/\D/g, '')) : v.replace(/\D/g, '')
}
function resetForm() {
  if (!original.value) return
  Object.assign(form, { name: original.value.name || '', phone: original.value.phone || '', role: original.value.role || 'user', password: '' })
  touched.value = false
}

/* ---------- Loaders ---------- */
async function loadUser() {
  try {
    const res = await $api(`/adm/users/${id.value}`)
    original.value = res || {}
    resetForm()
  } catch {
    toast.add({ title: 'Failed to load user', color: 'red' })
  }
}
async function loadAccounts() {
  accPending.value = true
  try {
    const res = await $api(`/adm/users/${id.value}/accounts`)
    accounts.value = res.map((acc: any) => ({
      ...acc,
      balance: Number(acc.balance ?? 0)
    }))
  } catch {
    toast.add({ title: 'Failed to load accounts', color: 'red' })
  } finally {
    accPending.value = false
  }
}

async function loadTxs(reset = false) {
  if (reset) txPage.value = 1
  txPending.value = true
  try {
    const res = await $api(`/adm/users/${id.value}/transactions`, {
      query: { q: txQ.value || undefined, page: txPage.value, page_size: txPageSize },
    })

    // normalize transaction - ensure amount is paired with correct currency
    const normalizeTx = (t: any) => {
      // `t` may include payment info (t.payment) or be an already-normalized object (t.original)
      const original = t.original ?? t
      const p = original.payment ?? original.original_payment ?? null

      // prefer payment invoice amount / invoice_currency (this is the 'Amount' you want to show)
      let amountVal: number | null = null
      let currencyVal = 'USD'

      // invoice amount candidates (strings or numbers)
      const invoiceAmtCandidate = p?.invoice_amount ?? p?.amount ?? original?.invoice_amount ?? null
      const invoiceCurCandidate = p?.invoice_currency ?? original?.invoice_currency ?? p?.currency ?? original?.currency ?? null

      const parseNum = (v: any) => {
        if (v === null || v === undefined || v === '') return null
        if (typeof v === 'number') return v
        const s = String(v).replace(/,/g, '')
        const n = Number(s)
        return Number.isFinite(n) ? n : null
      }

      const invoiceAmt = parseNum(invoiceAmtCandidate)
      const txAmt = parseNum(original?.amount ?? original?.total_amount ?? null)
      const txCurrency = (original?.currency || p?.currency || 'USD').toString().toUpperCase()

      if (invoiceAmt !== null) {
        amountVal = invoiceAmt
        currencyVal = (invoiceCurCandidate || txCurrency).toString().toUpperCase()
      } else if (txAmt !== null) {
        amountVal = txAmt
        currencyVal = txCurrency
      } else {
        amountVal = null
        currencyVal = 'USD'
      }

      // total_amount: prefer payment total_amount (usually USD-debited), otherwise transaction total_amount
      const totalAmtCandidate = p?.total_amount ?? original?.total_amount ?? null
      const totalAmt = parseNum(totalAmtCandidate)

      return {
        id: original.id ?? original.transaction_id ?? null,
        transaction_id: original.transaction_id ?? original.id ?? null,
        reference_number: original.reference_number ?? original.ref ?? null,
        amount: amountVal,
        total_amount: totalAmt,
        currency: currencyVal,
        created_at: original.created_at ?? original.cdc_transaction_datetime ?? original.createdAt ?? original.timestamp ?? null,
        service_name: original.service_name ?? original.service?.name ?? (p?.service?.name ?? null),
        service_logo_url: original.service_logo_url ?? original.service?.logo_url ?? (p?.service?.logo_url ?? null),
        type: original.type ?? original.direction ?? (original.status ? String(original.status) : '-'),
        fee: original.fee ?? p?.fee ?? null,
        customer_name: original.customer_name ?? p?.customer_name ?? null,
        original: original,
      }
    }

    let items: any[] = []
    if (Array.isArray(res)) items = res
    else items = res.items ?? []

    txs.value = items.map(normalizeTx)
    txTotal.value = (Array.isArray(res) ? res.length : (res.total ?? txs.value.length))
  } catch (err) {
    toast.add({ title: 'Failed to load transactions', color: 'red' })
    txs.value = []
    txTotal.value = 0
  } finally {
    txPending.value = false
  }
}

async function loadPays(reset = false) {
  if (reset) payPage.value = 1
  payPending.value = true
  try {
    const res = await $api(`/adm/users/${id.value}/payments`, {
      query: { q: payQ.value || undefined, page: payPage.value, page_size: payPageSize },
    })

    // normalize payment so amount + currency stay paired
    const normalizePay = (p: any) => {
      // raw object returned by API
      const original = p.original ?? p

      // helper to parse numbers safely (strip commas)
      const parseNum = (v: any) => {
        if (v === null || v === undefined || v === '') return null
        if (typeof v === 'number') return v
        const s = String(v).replace(/,/g, '')
        const n = Number(s)
        return Number.isFinite(n) ? n : null
      }

      // invoice (original) amount/currency that should be shown in Amount column
      const invoiceAmtCandidate =
        original.invoice_amount ?? original.amount ?? p.invoice_amount ?? p.amount ?? null
      const invoiceCurCandidate =
        original.invoice_currency ?? p.invoice_currency ?? original.currency ?? p.currency ?? null

      const invoiceAmt = parseNum(invoiceAmtCandidate)
      // total_amount usually is the USD debited
      const totalAmtCandidate = p.total_amount ?? original.total_amount ?? null
      const totalAmt = parseNum(totalAmtCandidate)

      // The admin rule: Amount = invoice amount + invoice currency (show original), Total = USD debited (total_amount)
      let displayAmount: number | null = null
      let displayCurrency = (invoiceCurCandidate || p.currency || original.currency || 'USD').toString().toUpperCase()

      if (invoiceAmt !== null) {
        displayAmount = invoiceAmt
        if (invoiceCurCandidate) displayCurrency = invoiceCurCandidate.toString().toUpperCase()
      } else {
        // fallback: if invoice missing, use stored payment amount and its currency
        const paymentAmt = parseNum(p.amount ?? original.amount ?? null)
        if (paymentAmt !== null) {
          displayAmount = paymentAmt
          displayCurrency = (p.currency || original.currency || 'USD').toString().toUpperCase()
        } else if (totalAmt !== null) {
          // last resort: show total amount but still mark currency based on payment
          displayAmount = totalAmt
          displayCurrency = (p.currency || original.currency || 'USD').toString().toUpperCase()
        } else {
          displayAmount = null
          displayCurrency = (p.currency || original.currency || 'USD').toString().toUpperCase()
        }
      }

      return {
        id: p.id ?? p.payment_id ?? p.transaction_id ?? p.reference_number ?? null,
        payment_id: p.payment_id ?? null,
        transaction_id: p.transaction_id ?? null,
        reference_number: p.reference_number ?? null,
        method: p.method ?? p.payment_method ?? '-',
        // normalized pair for UI:
        amount: displayAmount,
        currency: displayCurrency,
        // total_amount (usually USD-debited) kept separately
        total_amount: totalAmt,
        status: p.status ?? 'unknown',
        session_id: p.session_id ?? null,
        acknowledgement_id: p.acknowledgement_id ?? null,
        cdc_transaction_datetime: p.cdc_transaction_datetime ?? null,
        cdc_transaction_datetime_utc: p.cdc_transaction_datetime_utc ?? null,
        reversal_transaction_id: p.reversal_transaction_id ?? null,
        reversal_acknowledgement_id: p.reversal_acknowledgement_id ?? null,
        created_at: p.created_at ?? null,
        confirmed_at: p.confirmed_at ?? null,
        service_name: p.service?.name ?? original.service?.name ?? null,
        service_logo_url: p.service?.logo_url ?? original.service?.logo_url ?? null,
        original: original,
      }
    }

    let items: any[] = []
    if (Array.isArray(res)) items = res
    else items = res.items ?? []

    pays.value = items.map(normalizePay)
    payTotal.value = (Array.isArray(res) ? res.length : (res.total ?? pays.value.length))
  } catch (err) {
    toast.add({ title: 'Failed to load payments', color: 'red' })
    pays.value = []
    payTotal.value = 0
  } finally {
    payPending.value = false
  }
}

async function loadCurrencies() {
  try { currencyOptions.value = await $api('/adm/users/meta/currencies') }
  catch {}
}

/* ---------- Actions ---------- */
async function saveUser() {
  errorMsg.value = ''; successMsg.value = ''
  if (!form.name || !form.phone) {
    errorMsg.value = 'Name and phone are required'
    touched.value = true
    return
  }
  saving.value = true
  try {
    const payload: any = { name: form.name.trim(), phone: form.phone.trim(), role: form.role }
    if (form.password) payload.password = form.password.trim()
    await $api(`/adm/users/${id.value}`, { method: 'PUT', body: payload })
    successMsg.value = 'User updated successfully'
    await loadUser()
  } catch {
    errorMsg.value = 'Update failed'
  } finally { saving.value = false }
}

function openEditBalance(acc: any) {
  editingAcc.value = acc
  editBalanceValue.value = acc?.balance ?? 0
  showEditBalance.value = true
}
function getLogoUrl(path?: string) {
  if (!path) return ''
  return path.startsWith('/') ? `${useRuntimeConfig().public.apiBase}${path}` : path
}

async function saveBalance() {
  if (!editingAcc.value) return
  savingAcc.value = true
  try {
    await $api(`/adm/accounts/${editingAcc.value.id}`, {
      method: 'PATCH',
      body: { balance: Number(editBalanceValue.value ?? 0) },
    })
    toast.add({ title: 'Balance updated', color: 'green' })
    showEditBalance.value = false
    await loadAccounts()
  } catch {
    toast.add({ title: 'Failed to update balance', color: 'red' })
  } finally { savingAcc.value = false }
}

async function addAccount() {
  if (!newAccount.name || !newAccount.number) {
    toast.add({ title: 'Name and Account are required', color: 'orange' })
    return
  }
  addingAcc.value = true
  try {
    await $api(`/adm/users/${id.value}/accounts`, {
      method: 'POST',
      body: newAccount,
    })
    toast.add({ title: 'Account added successfully', color: 'green' })
    showAddAccount.value = false
    Object.assign(newAccount, { name: '', number: '', balance: 0, currency: 'USD', type: 'wallet' })
    await loadAccounts()
  } catch (e: any) {
    toast.add({ title: e?.data?.detail || 'Failed to add account', color: 'red' })
  } finally { addingAcc.value = false }
}

/* ---------- Pagination & Search ---------- */
function goTx(p: number) { txPage.value = Math.min(Math.max(1, p), txTotalPages.value); loadTxs() }
function goPay(p: number) { payPage.value = Math.min(Math.max(1, p), payTotalPages.value); loadPays() }
function reloadTxs() { loadTxs(true) }
function reloadPays() { loadPays(true) }

const statusVariant = computed(() => {
  const s = (selectedPayment?.status ?? '').toLowerCase()
  return s === 'confirmed' || s === 'success' ? 'success'
    : s === 'started' || s === 'pending' ? 'warning'
    : s === 'failed' || s === 'error' ? 'error'
    : s === 'reversed' || s === 'reversed' ? 'gray'
    : 'info'
})

async function copyField(text?: string | null, label = 'Value') {
  if (!text) return
  try {
    await navigator.clipboard.writeText(String(text))
    toast.add({ title: `${label} copied to clipboard`, color: 'success' })
  } catch (e) {
    toast.add({ title: `Failed to copy ${label}`, color: 'error' })
  }
}

function openTransaction(txId?: number | null) {
  if (!txId) return
  const url = `/adm/transactions/${txId}`
  try {
    navigateTo(url)
    showPaymentDetail.value = false
  } catch {
    window.open(url, '_blank')
  }
}

let txTimer: any = null
let payTimer: any = null
function onTxInput() { clearTimeout(txTimer); txTimer = setTimeout(() => reloadTxs(), 400) }
function onPayInput() { clearTimeout(payTimer); payTimer = setTimeout(() => reloadPays(), 400) }

/* ---------- Init ---------- */
onMounted(async () => {
  await Promise.all([loadUser(), loadAccounts(), loadTxs(), loadPays(), loadCurrencies()])
})
</script>
