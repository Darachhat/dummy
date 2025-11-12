<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="hidden md:flex justify-between items-center">
      <div class="flex items-center gap-3">
        <NuxtLink to="/admin/users" class="px-3 py-1 border rounded-xl hover:bg-gray-50">Back</NuxtLink>
        <h2 class="text-2xl font-bold text-gray-800">{{ form.name}}</h2>
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
        <UFormField  label="Name" >
          <UInput v-model.trim="form.name" placeholder="Full name" @blur="touched = true" />
        </UFormField>

        <UFormField  label="Phone" >
          <UInput v-model.trim="form.phone" inputmode="tel" placeholder="Phone number" @input="digitsPhone" @blur="touched = true" />
        </UFormField>

        <UFormField  label="Role">
          <USelect
            v-model="form.role"
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
          {{ formatMoney(row.original.balance, row.original.currency) }}
        </template>

        <template #actions-cell="{ row }">
          <div class="flex justify-start">
            <UButton
              size="sm"
              variant="outline"
              class="btn-outline-dark"
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
    {{ formatMoney(row.original?.amount, row.original?.currency || 'USD') }}
  </template>

  <template #total_amount-cell="{ row }">
    {{ formatMoney(row.original?.total_amount ?? row.original?.totalAmount, row.original?.currency || 'USD') }}
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
            <UButton size="sm" variant="outline" class="btn-outline-dark" :disabled="txPage<=1 || txPending" @click="goTx(txPage-1)">Prev</UButton>
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
    {{ formatMoney(row.original?.amount, row.original?.currency || 'USD') }}
  </template>

  <template #created_at-cell="{ row }">
    {{ formatDate(row.original?.created_at ?? row.original?.cdc_payment_datetime) }}
  </template>

  <template #status-cell="{ row }">
    <UBadge :label="row.original?.status ?? 'unknown'" :color="(row.original?.status === 'paid') ? 'green' : 'orange'" />
  </template>

  <template #actions-cell="{ row }">
  <UButton size="sm" variant="outline" @click="openPaymentDetail(row.original)">Details</UButton>
</template>


  <template #empty>
    <div class="text-center py-6 text-gray-500">No payments found</div>
  </template>
</UTable>



      <template #footer>
        <div class="flex justify-between items-center text-sm text-gray-600">
          <span>Showing {{ pays.length }} of {{ payTotal }} — Page {{ payPage }} / {{ payTotalPages }}</span>
          <div class="flex gap-2">
            <UButton size="sm" variant="outline" class="btn-outline-dark" :disabled="payPage<=1 || payPending" @click="goPay(payPage-1)">Prev</UButton>
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
            <UInput v-model.trim="newAccount.name" placeholder="e.g. Main Wallet" />
          </UFormField>
          <UFormField label="Account Number" required>
            <UInput v-model.trim="newAccount.number" placeholder="e.g. 000-000-000 " />
          </UFormField>
          <div class="grid sm:grid-cols-2 gap-4">
            <UFormField label="Initial Balance" required>
              <UInput v-model.number="newAccount.balance" inputmode="decimal" placeholder="0.00" />
            </UFormField>
            <UFormField label="Currency" required>
              <USelect v-model="newAccount.currency" :items="currencyOptions" placeholder="Select currency" />
            </UFormField>
          </div>
        </div>
      </template>
      <template #footer>
        <div class="flex justify-end gap-2">
          <UButton variant="outline" class="btn-outline-dark" @click="showAddAccount=false">Cancel</UButton>
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
          <UInput v-model.number="editBalanceValue" inputmode="decimal" placeholder="0.00" />
        </UFormField>
      </template>
      <template #footer>
        <div class="flex justify-end gap-2">
          <UButton variant="outline" class="btn-outline-dark" @click="showEditBalance=false">Cancel</UButton>
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
          <UButton size="sm" variant="ghost" icon="i-lucide-copy" :disabled="!selectedPayment?.session_id" @click="copyField(selectedPayment?.session_id, 'Session ID')" />
        </div>
      </div>

      <div class="space-y-2">
        <label class="text-xs text-gray-500">Acknowledgement ID</label>
        <div class="flex items-center gap-2">
          <div class="truncate text-slate-700">{{ selectedPayment?.acknowledgement_id ?? '-' }}</div>
          <UButton size="sm" variant="ghost" icon="i-lucide-copy" :disabled="!selectedPayment?.acknowledgement_id" @click="copyField(selectedPayment?.acknowledgement_id, 'Acknowledgement ID')" />
        </div>
      </div>

      <div class="space-y-2">
        <label class="text-xs text-gray-500">CDC Transaction Datetime</label>
        <div class="flex items-center gap-2">
          <div class="truncate text-slate-700">{{ selectedPayment?.cdc_transaction_datetime ?? selectedPayment?.created_at ?? '-' }}</div>
          <UButton size="sm" variant="ghost" icon="i-lucide-copy" :disabled="!(selectedPayment?.cdc_transaction_datetime || selectedPayment?.created_at)" @click="copyField(selectedPayment?.cdc_transaction_datetime ?? selectedPayment?.created_at, 'CDC local')" />
        </div>
      </div>

      <div class="space-y-2">
        <label class="text-xs text-gray-500">CDC Transaction Datetime UTC</label>
        <div class="flex items-center gap-2">
          <div class="truncate text-slate-700">{{ selectedPayment?.cdc_transaction_datetime_utc ?? '-' }}</div>
          <UButton size="sm" variant="ghost" icon="i-lucide-copy" :disabled="!selectedPayment?.cdc_transaction_datetime_utc" @click="copyField(selectedPayment?.cdc_transaction_datetime_utc, 'CDC UTC')" />
        </div>
      </div>

      <div class="space-y-2">
        <label class="text-xs text-gray-500">Reversal Transaction ID</label>
        <div class="flex items-center gap-2">
          <div class="truncate text-slate-700">{{ selectedPayment?.reversal_transaction_id ?? '-' }}</div>
          <UButton size="sm" variant="ghost" icon="i-lucide-copy" :disabled="!selectedPayment?.reversal_transaction_id" @click="copyField(selectedPayment?.reversal_transaction_id, 'Reversal Tx')" />
        </div>
      </div>

      <div class="space-y-2">
        <label class="text-xs text-gray-500">Reversal Acknowledgement ID</label>
        <div class="flex items-center gap-2">
          <div class="truncate text-slate-700">{{ selectedPayment?.reversal_acknowledgement_id ?? '-' }}</div>
          <UButton size="sm" variant="ghost" icon="i-lucide-copy" :disabled="!selectedPayment?.reversal_acknowledgement_id" @click="copyField(selectedPayment?.reversal_acknowledgement_id, 'Reversal Ack')" />
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
        <label class="text-xs text-gray-500">Raw / Notes</label>
        <div class="mt-1 p-3 bg-gray-50 rounded-md text-xs text-gray-700 break-words max-h-36 overflow-auto">
          <pre class="whitespace-pre-wrap text-xs m-0">{{ JSON.stringify(selectedPayment?.original ?? selectedPayment ?? {}, null, 2) }}</pre>
        </div>
      </div>
    </div>
  </template>

  <template #footer>
    <div class="flex items-center justify-between w-full">
      <div class="flex gap-2">
        <UButton variant="outline" @click="copyField(selectedPayment?.reference_number, 'Reference')" :disabled="!selectedPayment?.reference_number">
          <i class="i-lucide-copy mr-2"></i> Copy Reference
        </UButton>
        <UButton variant="outline" @click="openTransaction(selectedPayment?.transaction_id)" :disabled="!selectedPayment?.transaction_id">
          <i class="i-lucide-external-link mr-2"></i> Open Transaction
        </UButton>
      </div>

      <div class="flex gap-2">
        <UButton variant="ghost" @click="showPaymentDetail = false">Close</UButton>
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
const toast = useToast()

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
  { accessorKey: 'id', header: 'ID' },
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
  { accessorKey: 'id', header: 'ID' },
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
function formatMoney(n?: number | string | null, c: string = 'USD') {
  if (n === null || n === undefined || n === '') return '-'
  const num =
    typeof n === 'number'
      ? n
      : (typeof n === 'string' && n.trim() !== '') ? Number(n.replace(/,/g, '')) : NaN
  if (!isFinite(num)) return '-'
  return num.toLocaleString(undefined, { style: 'currency', currency: c, minimumFractionDigits: 2 })
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
    const res = await $api(`/admin/users/${id.value}`)
    original.value = res || {}
    resetForm()
  } catch {
    toast.add({ title: 'Failed to load user', color: 'red' })
  }
}
async function loadAccounts() {
  accPending.value = true
  try {
    const res = await $api(`/admin/users/${id.value}/accounts`)
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
    const res = await $api(`/admin/users/${id.value}/transactions`, {
      query: { q: txQ.value || undefined, page: txPage.value, page_size: txPageSize },
    })

    const normalizeTx = (t: any) => {
      return {
        id: t.id ?? t.transaction_id ?? null,
        transaction_id: t.transaction_id ?? t.id ?? null,
        reference_number: t.reference_number ?? t.ref ?? null,
        amount: t.amount ?? t.total_amount ?? t.totalAmount ?? null,
        total_amount: t.total_amount ?? t.totalAmount ?? null,
        currency: t.currency ?? 'USD',
        created_at: t.created_at ?? t.cdc_transaction_datetime ?? t.createdAt ?? t.timestamp ?? null,
        service_name: t.service_name ?? (t.service?.name ?? null),
        service_logo_url: t.service_logo_url ?? (t.service?.logo_url ?? null),
        type: t.type ?? t.direction ?? (t.status ? String(t.status) : '-'),
        fee: t.fee ?? null,
        customer_name: t.customer_name ?? null,
        original: t,
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
    const res = await $api(`/admin/users/${id.value}/payments`, {
      query: { q: payQ.value || undefined, page: payPage.value, page_size: payPageSize },
    })

    const normalizePay = (p: any) => {
      const service = p?.service ?? {}
      return {
         id: p.id ?? p.payment_id ?? p.transaction_id ?? p.reference_number ?? null,
        payment_id: p.payment_id ?? null,
        transaction_id: p.transaction_id ?? null,
        reference_number: p.reference_number ?? null,
        method: p.method ?? p.payment_method ?? '-',
        amount: p.amount ?? null,
        total_amount: p.total_amount ?? null,
        currency: p.currency ?? 'USD',
        status: p.status ?? 'unknown',
    
        session_id: p.session_id ?? null,
        acknowledgement_id: p.acknowledgement_id ?? null,
        cdc_transaction_datetime: p.cdc_transaction_datetime ?? null,
        cdc_transaction_datetime_utc: p.cdc_transaction_datetime_utc ?? null,
        reversal_transaction_id: p.reversal_transaction_id ?? null,
        reversal_acknowledgement_id: p.reversal_acknowledgement_id ?? null,
        created_at: p.created_at ?? null,
        confirmed_at: p.confirmed_at ?? null,
        service_name: service?.name ?? null,
        service_logo_url: service?.logo_url ?? null,
        original: p,
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
  try { currencyOptions.value = await $api('/admin/users/meta/currencies') }
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
    await $api(`/admin/users/${id.value}`, { method: 'PUT', body: payload })
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
    await $api(`/admin/accounts/${editingAcc.value.id}`, {
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
    await $api(`/admin/users/${id.value}/accounts`, {
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
  // open admin transaction page or show toast if not available
  const url = `/admin/transactions/${txId}`
  // try to navigate with Nuxt
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

