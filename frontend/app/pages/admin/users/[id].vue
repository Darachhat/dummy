]<template>
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
        <template #amount-cell="{ row }">
          {{ formatMoney(row.original.amount, row.original.currency || 'USD') }}
        </template>
        <template #created_at-cell="{ row }">
          {{ formatDate(row.original.created_at) }}
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
        <template #amount-cell="{ row }">
          {{ formatMoney(row.original.amount, row.original.currency || 'USD') }}
        </template>
        <template #created_at-cell="{ row }">
          {{ formatDate(row.original.created_at) }}
        </template>
        <template #status-cell="{ row }">
          <UBadge :label="row.original.status" :color="row.original.status === 'paid' ? 'green' : 'orange'" />
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
  { accessorKey: 'type', header: 'Type' },
  { accessorKey: 'amount', header: 'Amount' },
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
const paymentColumns = [
  { accessorKey: 'id', header: 'ID' },
  { accessorKey: 'method', header: 'Method' },
  { accessorKey: 'amount', header: 'Amount' },
  { accessorKey: 'status', header: 'Status' },
  { accessorKey: 'created_at', header: 'Date' },
]
const payTotalPages = computed(() => Math.max(1, Math.ceil(payTotal.value / payPageSize)))

/* ---------- Utils ---------- */
function formatDate(s?: string) { return s ? new Date(s).toLocaleString() : '-' }
function formatMoney(n?: number, c: string = 'USD') {
  return typeof n === 'number'
    ? n.toLocaleString(undefined, { style: 'currency', currency: c, minimumFractionDigits: 2 })
    : '-'
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
    txs.value = res.items ?? []
    txTotal.value = res.total ?? txs.value.length
  } finally { txPending.value = false }
}
async function loadPays(reset = false) {
  if (reset) payPage.value = 1
  payPending.value = true
  try {
    const res = await $api(`/admin/users/${id.value}/payments`, {
      query: { q: payQ.value || undefined, page: payPage.value, page_size: payPageSize },
    })
    pays.value = res.items ?? []
    payTotal.value = res.total ?? pays.value.length
  } finally { payPending.value = false }
}
async function loadCurrencies() {
  try { currencyOptions.value = await $api('/admin/users/meta/currencies') }
  catch { /* fallback */ }
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

let txTimer: any = null
let payTimer: any = null
function onTxInput() { clearTimeout(txTimer); txTimer = setTimeout(() => reloadTxs(), 400) }
function onPayInput() { clearTimeout(payTimer); payTimer = setTimeout(() => reloadPays(), 400) }

/* ---------- Init ---------- */
onMounted(async () => {
  await Promise.all([loadUser(), loadAccounts(), loadTxs(), loadPays(), loadCurrencies()])
})
</script>
