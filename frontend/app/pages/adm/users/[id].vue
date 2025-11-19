<!-- pages/adm/users/[id].vue -->
<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="hidden md:flex justify-between items-center">
      <div class="flex items-center gap-3">
        <NuxtLink to="/adm/users" class="px-3 py-1 border rounded-xl hover:bg-gray-50">Back</NuxtLink>
        <h2 class="text-2xl font-bold text-gray-800">{{ form.name }}</h2>
      </div>

      <!-- Right actions: Add Account + Save -->
      <div class="flex items-center gap-3">
        <!-- Add Account button (opens the Add Account modal) -->
        <UButton
          type="button"
          variant="outline"
          color="neutral"
          icon="i-lucide-plus"
          @click="showAddAccount = true"
          title="Add account for this user"
        >
          Add Account
        </UButton>

        <!-- Save user -->
        <UButton class="btn-dark" icon="i-lucide-save" :loading="saving" :disabled="!isPinValid" @click="saveUser">Save</UButton>
      </div>
    </div>

    <!-- Alerts -->
    <UAlert v-if="errorMsg" color="warning" :title="errorMsg" icon="i-lucide-alert-triangle" />
    <UAlert v-if="successMsg" color="success" :title="successMsg" icon="i-lucide-check" />

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

        <UFormField label="New Password">
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
           <div
            class="text-xs mt-1"
            :class="form.pin === '' || isPinValid ? 'text-gray-500' : 'text-red-600'"
          >
            {{ form.password === '' ? 'Leave blank to keep current password' : 'Changing password will log the user out of all sessions' }}
          </div>
        </UFormField>

        <!-- Pincode: minimal masked 4-digit input -->
        <UFormField label="Pincode (4 digits)">
          <UInput
            type="password"
            v-model="form.pin"
            inputmode="numeric"
            maxlength="4"
            color="neutral"
            placeholder="Enter 4-digit PIN"
            @input="digitsPin"
          />
          <div
            class="text-xs mt-1"
            :class="form.pin === '' || isPinValid ? 'text-gray-500' : 'text-red-600'"
          >
            {{ form.pin === '' ? 'Optional' : (isPinValid ? 'Valid PIN' : 'PIN must be 4 digits') }}
          </div>
        </UFormField>
      </div>

      <template #footer>
        <div class="flex justify-end gap-2">
          <UButton class="btn-dark" :loading="saving" :disabled="!isPinValid" @click="saveUser">Save Changes</UButton>
        </div>
      </template>
    </UCard>

    <!-- ACCOUNTS -->
    <AdminTablePage
      title="Accounts"
      :total="accounts.length"
      :data="accounts"
      :columns="accountColumns"
      :loading="accPending"
      :disable-pagination="true"
      :on-row-select="onAccountRowSelect"
      class="min-w-full"
    >
      <template #name-cell="{ row }">
        <div class="truncate">
          <NuxtLink
            v-if="row.original?.id"
            :to="`/accounts/${row.original.id}`"
            class="text-blue-600 hover:underline block truncate"
            @click.stop
          >
            {{ row.original?.name ?? '-' }}
          </NuxtLink>
          <span v-else>{{ row.original?.name ?? '-' }}</span>
        </div>
      </template>

      <template #number-cell="{ row }">
        <div class="truncate">{{ row.original?.number ?? '-' }}</div>
      </template>

      <template #balance-cell="{ row }">
        {{ formatMoney(row.original.balance, row.original.currency || 'USD') }}
      </template>

      <template #empty>
        <div class="text-center py-6 text-gray-500">No accounts found</div>
      </template>
    </AdminTablePage>

    <!-- PAYMENTS -->
    <AdminTablePage
      title="Payments"
      :data="pays"
      :columns="paymentColumns"
      :loading="payPending"
      :page="payPage"
      :total-pages="payTotalPages"
      @change-page="goPay"
      :on-row-select="onPaymentRowSelect"
      class="min-w-full"
    >
      <template #reference_number-cell="{ row }">
        <div class="truncate max-w-xs">
          <a
            href="#"
            class="text-gray-700 hover:text-blue-600 hover:underline block truncate"
            @click.prevent="openPaymentModal(row.original?.id ?? row.original?.payment_id)"
          >
            {{ row.original?.reference_number ?? '-' }}
          </a>
        </div>
      </template>

      <template #method-cell="{ row }">
        {{ row.original?.method ?? row.original?.payment_method ?? '-' }}
      </template>

      <template #amount-cell="{ row }">
        {{ row.original?.amount  || 'USD' }}
      </template>

      <template #created_at-cell="{ row }">
        {{ formatDate(row.original?.created_at ?? row.original?.cdc_transaction_datetime) }}
      </template>

      <template #status-cell="{ row }">
        <UBadge :label="row.original?.status ?? 'unknown'" :color="(row.original?.status === 'paid' || row.original?.status === 'confirmed') ? 'green' : 'orange'" />
      </template>

      <template #empty>
        <div class="text-center py-6 text-gray-500">No payments found</div>
      </template>

      <template #summary>
        Showing {{ pays.length }} of {{ payTotal }} — Page {{ payPage }} / {{ payTotalPages }}
      </template>
    </AdminTablePage>

    <!-- TRANSACTIONS -->
    <AdminTablePage
      title="Transactions"
      :data="txs"
      :columns="transactionColumns"
      :loading="txPending"
      :page="txPage"
      :total-pages="txTotalPages"
      @change-page="goTx"
      :on-row-select="onTransactionRowSelect"
      class="min-w-full"
    >
      <template #transaction_id-cell="{ row }">
        <div class="truncate">
          <a
            href="#"
            class="text-gray-700 hover:text-blue-600 hover:underline block truncate"
            @click.prevent="openTransactionModal(row.original?.id ?? row.original?.transaction_id)"
          >
            {{ row.original?.transaction_id ?? row.original?.id ?? '-' }}
          </a>
        </div>
      </template>

      <template #reference_number-cell="{ row }">
        <div class="truncate max-w-xs">
          <a
            href="#"
            class="text-gray-700 hover:text-blue-600 hover:underline block truncate"
            @click.prevent="openTransactionModal(row.original?.id ?? row.original?.transaction_id)"
          >
            {{ row.original?.reference_number ?? '-' }}
          </a>
        </div>
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
        {{row.original?.amount || 'USD' }}
      </template>

      <template #total_amount-cell="{ row }">
        {{ formatMoney(row.original?.total_amount, 'USD') }}
      </template>

      <template #created_at-cell="{ row }">
        {{ formatDate(row.original?.created_at ?? row.original?.cdc_transaction_datetime) }}
      </template>

      <template #empty>
        <div class="text-center py-6 text-gray-500">No transactions found</div>
      </template>

      <template #summary>
        Showing {{ txs.length }} of {{ txTotal }} — Page {{ txPage }} / {{ txTotalPages }}
      </template>
    </AdminTablePage>

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

    <!-- ACCOUNT DETAILS MODAL -->
    <UModal v-model:open="showAccountDetail" :title="`Account — ${accountForm.name ?? ''}`" class="items-center max-w-[400px]">
      <template #body>
        <div class="space-y-4">
          <UFormField label="Name" required>
            <UInput color="neutral" v-model.trim="accountForm.name" />
          </UFormField>

          <UFormField label="Account Number" required>
            <UInput color="neutral" v-model.trim="accountForm.number" />
          </UFormField>

          <div class="grid sm:grid-cols-2  gap-4">
            <UFormField label="Currency" required>
              <USelect color="neutral" v-model="accountForm.currency" :items="currencyOptions" />
            </UFormField>
          </div>

          <UFormField label="Balance">
            <UInput color="neutral" v-model.number="accountForm.balance" inputmode="decimal" />
          </UFormField>
        </div>
      </template>

      <template #footer>
        <div class="flex justify-between gap-15 items-center w-full">
          <div class="text-sm text-gray-600">ID: {{ selectedAccount?.id ?? '-' }}</div>
          <div class="flex gap-2">
            <UButton variant="outline" color="neutral" @click="closeAccountModal">Cancel</UButton>
            <UButton class="btn-dark" :loading="savingAccount" @click="saveAccountDetails">Save</UButton>
          </div>
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

    <!-- TRANSACTION DETAIL MODAL (UPDATED) -->
    <UModal v-model:open="showTransactionDetail" :title="`Transaction — ${selectedTransaction?.transaction_id ?? selectedTransaction?.id ?? ''}`" class="max-w-3xl">
      <template #header>
        <div class="flex items-center justify-between w-full">
          <div class="flex items-center gap-3">
            <div class="text-sm text-gray-600">Transaction</div>
            <div class="font-medium text-lg break-all">{{ selectedTransaction?.transaction_id ?? selectedTransaction?.id ?? '-' }}</div>
          </div>
          <div class="text-sm text-gray-600">{{ formatDateLocalMMDDYYYY_hhmmA(selectedTransaction?.created_at ?? selectedTransaction?.cdc_transaction_datetime) }}</div>
        </div>
      </template>

      <template #body>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div class="space-y-2">
            <label class="text-xs text-gray-500">Reference</label>
            <div class="truncate text-slate-700">{{ selectedTransaction?.reference_number ?? '-' }}</div>
          </div>

          <div class="space-y-2">
            <label class="text-xs text-gray-500">Status</label>
            <div class="text-slate-700">{{ selectedTransaction?.status ?? '-' }}</div>
          </div>

          <div class="space-y-2">
            <label class="text-xs text-gray-500">Amount</label>
            <div class="text-slate-700">{{ formatCurrency(selectedTransaction?.amount, selectedTransaction?.invoice_currency ?? selectedTransaction?.currency ?? 'USD') }}</div>
          </div>

          <div class="space-y-2">
            <label class="text-xs text-gray-500">Invoice Currency</label>
            <div class="text-slate-700">{{ selectedTransaction?.invoice_currency ?? (selectedTransaction?.currency ?? '-') }}</div>
          </div>

          <div class="space-y-2">
            <label class="text-xs text-gray-500">Total (USD)</label>
            <div class="text-slate-700">{{ formatMoney(selectedTransaction?.total_amount, 'USD') }}</div>
          </div>

          <div class="space-y-2">
            <label class="text-xs text-gray-500">Service</label>
            <div class="flex items-center gap-2">
              <img v-if="selectedTransaction?.service_logo_url" :src="getLogoUrl(selectedTransaction.service_logo_url)" class="w-6 h-6 rounded-full object-contain" />
              <div class="text-slate-700">{{ selectedTransaction?.service_name ?? '-' }}</div>
            </div>
          </div>

          <div class="space-y-2 col-span-1 sm:col-span-2">
            <label class="text-xs text-gray-500">Fee</label>
            <div class="flex items-center gap-3">
              <div class="text-slate-700">${{ selectedTransaction?.fee ?? 'USD' }}</div>
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-xs text-gray-500">User Phone</label>
            <div class="flex items-center gap-2">
              <div class="truncate text-slate-700">{{ selectedTransaction?.user_phone ?? '-' }}</div>
              <UButton size="sm" variant="ghost" color="neutral" icon="i-lucide-copy" :disabled="!selectedTransaction?.user_phone" @click="copyField(selectedTransaction?.user_phone, 'User Phone')" />
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-xs text-gray-500">Account Number</label>
            <div class="flex items-center gap-2">
              <div class="truncate text-slate-700">{{ selectedTransaction?.account_number ?? '-' }}</div>
              <UButton size="sm" variant="ghost" color="neutral" icon="i-lucide-copy" :disabled="!selectedTransaction?.account_number" @click="copyField(selectedTransaction?.account_number, 'Account Number')" />
            </div>
          </div>

          <div class="col-span-1 sm:col-span-2 pt-2">
            <label class="text-xs text-gray-500">Raw</label>
            <div class="mt-1 p-3 bg-gray-50 rounded-md text-xs text-gray-700 break-words max-h-56 overflow-auto">
              <pre class="whitespace-pre-wrap text-xs m-0">{{ JSON.stringify(selectedTransaction?.original ?? selectedTransaction ?? {}, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </template>

      <template #footer>
        <div class="flex items-center justify-between w-full">
          <div class="flex gap-2">
            <UButton variant="outline" color="neutral" @click="copyField(selectedTransaction?.reference_number, 'Reference')" :disabled="!selectedTransaction?.reference_number">
              <i class="i-lucide-copy mr-2"></i> Copy Reference
            </UButton>
          </div>

          <div class="flex gap-2">
            <UButton variant="ghost" color="neutral" @click="showTransactionDetail = false">Close</UButton>
            <UButton class="btn-dark" @click="showTransactionDetail = false">Done</UButton>
          </div>
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
            <label class="text-xs text-gray-500">Customer</label>
            <div class="flex items-center gap-2">
              <div class="truncate text-slate-700">{{ selectedPayment?.customer_name ?? '-' }}</div>
              <UButton size="sm" variant="ghost" color="neutral" icon="i-lucide-copy" :disabled="!selectedPayment?.customer_name" @click="copyField(selectedPayment?.customer_name, 'Customer')" />
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-xs text-gray-500">Amount</label>
            <div class="text-slate-700">{{ formatCurrency(selectedPayment?.amount, selectedPayment?.invoice_currency ?? selectedPayment?.currency ?? 'USD') }}</div>
          </div>

          <div class="space-y-2">
            <label class="text-xs text-gray-500">Invoice Currency</label>
            <div class="text-slate-700">{{ selectedPayment?.invoice_currency ?? (selectedPayment?.currency ?? '-') }}</div>
          </div>

          <div class="space-y-2">
            <label class="text-xs text-gray-500">Fee (USD)</label>
            <div class="text-slate-700">{{ (selectedPayment?.fee, 'USD') }}</div>
          </div>

          <div class="space-y-2">
            <label class="text-xs text-gray-500">Total (USD)</label>
            <div class="text-slate-700">{{ formatCurrency(selectedPayment?.total_amount, 'USD') }}</div>
          </div>

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

import { ref, reactive, computed, onMounted, resolveComponent, h } from 'vue'
import type { ColumnDef } from '@tanstack/vue-table'
import AdminTablePage from '~/components/AdminTablePage.vue'
import { useCurrency } from '~/composables/useCurrency'

const UBadge = resolveComponent('UBadge')

const route = useRoute()
const id = computed(() => String(route.params.id))
const { $api } = useNuxtApp()
const toast = useMyToast()

/* ---------- Helpers ---------- */
function parseToDate(s?: string | null): Date | null {
  if (!s) return null
  if (s instanceof Date) return s
  const str = String(s).trim()
  const hasTZ = /([zZ]|[+-]\d{2}:?\d{2})$/.test(str)
  const plainIsoNoTZ = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?$/
  let iso = str
  if (!hasTZ && plainIsoNoTZ.test(str)) iso = str + 'Z'
  const d = new Date(iso)
  return isNaN(d.getTime()) ? null : d
}
function formatDateLocalMMDDYYYY_hhmmA(s?: string | null): string {
  const d = parseToDate(s)
  if (!d) return '-'
  return d.toLocaleString(undefined, {
    month: '2-digit',
    day: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const { format: currencyFormat } = useCurrency()
function formatCurrency(val?: number | string | null, cur = 'USD') {
  return currencyFormat(val, cur)
}
function formatDate(s?: string) { return s ? new Date(s).toLocaleString() : '-' }

function formatMoney(n?: number | string | null, c: string = 'USD') {
  if (n === null || n === undefined || n === '') return '-'
  const num =
    typeof n === 'number'
      ? n
      : (typeof n === 'string' && n.trim() !== '') ? Number(String(n).replace(/,/g, '')) : NaN
  if (!isFinite(num)) return '-'
  const cur = (c || 'USD').toString().toUpperCase()
  if (cur === 'KHR' || cur === 'RIEL' || cur === '៛') {
    const intVal = Math.round(num)
    return intVal.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 }) + ' ៛'
  }
  try {
    return new Intl.NumberFormat(undefined, { style: 'currency', currency: cur, minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(num)
  } catch (e) {
    return num.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ` ${cur}`
  }
}

function digitsPhone(e: any) {
  const v = e?.target?.value ?? ''
  form.phone = v.startsWith('+') ? ('+' + v.slice(1).replace(/\D/g, '')) : v.replace(/\D/g, '')
}

function getLogoUrl(path?: string) {
  if (!path) return ''
  return path.startsWith('/') ? `${useRuntimeConfig().public.apiBase}${path}` : path
}

/* ---------- State ---------- */
const original = ref<any>(null)
const form = reactive({ name: '', phone: '', role: 'user', password: '', pin: '' })
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
const accountColumns: ColumnDef<Record<string, any>, any>[] = [
  { accessorKey: 'name', header: 'Account Name' },
  { accessorKey: 'number', header: 'Account Number' },
  { accessorKey: 'currency', header: 'Currency' },
  { accessorKey: 'balance', header: 'Balance' },
]

/* Account detail modal */
const showAccountDetail = ref(false)
const selectedAccount = ref<any | null>(null)
const accountForm = reactive<any>({ id: null, name: '', number: '', currency: 'USD', type: 'wallet', balance: 0 })
const savingAccount = ref(false)

/* Transactions */
const txs = ref<any[]>([])
const txPending = ref(false)
const txPage = ref(1)
const txPageSize = 10
const txTotal = ref(0)
const txQ = ref('')
const transactionColumns: ColumnDef<Record<string, any>, any>[] = [
  { accessorKey: 'id', header: 'ID' },
  { accessorKey: 'transaction_id', header: 'Transaction ID' },
  { accessorKey: 'customer_name', header: 'Customer' },
  { accessorKey: 'user_phone', header: 'User Phone' },
  { accessorKey: 'account_number', header: 'Account Number' },
  { accessorKey: 'reference_number', header: 'Reference' },
  { accessorKey: 'amount', header: 'Amount' },
  { accessorKey: 'invoice_currency', header: 'Invoice Currency' },
  { accessorKey: 'service_name', header: 'Service' },
  {
    accessorKey: 'status', header: 'Status', cell: ({ row }) => {
      const raw = row.original.status ?? ''
      const status = String(raw).trim().toLowerCase()
      const color =
        {
          confirmed: 'success',
          success: 'success',
          pending: 'neutral',
          started: 'neutral',
          failed: 'error',
          canceled: 'error',
        }[status] ?? 'neutral'
      return h(UBadge, { class: 'capitalize', variant: 'subtle', color }, () => status || '-')
    },
  },
  {
    accessorKey: 'created_at',
    header: 'Created At',
    cell: ({ getValue, row }) => formatDate(row.original.created_at ?? getValue()),
  },
]
const txTotalPages = computed(() => Math.max(1, Math.ceil(txTotal.value / txPageSize)))

/* Transaction modal state */
const showTransactionDetail = ref(false)
const selectedTransaction = ref<any | null>(null)

/* Payments */
const pays = ref<any[]>([])
const payPending = ref(false)
const payPage = ref(1)
const payPageSize = 10
const payTotal = ref(0)
const payQ = ref('')  
const showPaymentDetail = ref(false)
const selectedPayment = ref<any | null>(null)
const paymentColumns: ColumnDef<Record<string, any>, any>[] = [
  { accessorKey: 'customer_name', header: 'Customer' },
  { accessorKey: 'id', header: 'Transaction ID' },
  { accessorKey: 'service_name', header: 'Service' },
  {
    accessorKey: 'status', header: 'Status', cell: ({ getValue }) => {
      const raw = (getValue() as string | undefined) ?? ''
      const status = String(raw).trim().toLowerCase()
      const color =
        {
          confirmed: 'success',
          success: 'success',
          pending: 'neutral',
          started: 'neutral',
          failed: 'error',
          canceled: 'error',
        }[status] ?? 'neutral'
      return h(UBadge, { class: 'capitalize', variant: 'subtle', color }, () => status || '-')
    },
  },
  {
    accessorKey: 'amount', header: 'Amount', cell: ({ getValue, row }) => {
      const cur = row.original.invoice_currency ?? row.original.currency ?? 'USD'
      return formatCurrency(getValue(), cur)
    },
  },
  { accessorKey: 'invoice_currency', header: 'Invoice Currency' },
  { accessorKey: 'fee', header: 'Fee (USD)', cell: ({ getValue }) => formatCurrency(getValue(), 'USD') },
  { accessorKey: 'total_amount', header: 'Total (USD)', cell: ({ getValue }) => formatCurrency(getValue(), 'USD') },
  { accessorKey: 'currency', header: 'Currency' },
  { accessorKey: 'reference_number', header: 'Reference' },
  {
    accessorKey: 'cdc_transaction_datetime',
    header: 'CDC Time',
    cell: ({ row }) => {
      const v = row.original.cdc_transaction_datetime ?? row.original.cdc_transaction_datetime_utc
      return formatDateLocalMMDDYYYY_hhmmA(v)
    },
  },
  {
    accessorKey: 'created_at',
    header: 'Created At',
    cell: ({ getValue }) => formatDateLocalMMDDYYYY_hhmmA(getValue()),
  },
]
const payTotalPages = computed(() => Math.max(1, Math.ceil(payTotal.value / payPageSize)))

/* ---------- Helpers & normalizers ---------- */
function resetForm() {
  if (!original.value) return
  Object.assign(form, { name: original.value.name || '', phone: original.value.phone || '', role: original.value.role || 'user', password: '', pin: '' })
  touched.value = false
}

function toNumberSafe(v: any) {
  if (v === null || v === undefined || v === '') return null
  if (typeof v === 'number') return v
  const s = String(v).replace(/,/g, '')
  const n = Number(s)
  return Number.isFinite(n) ? n : null
}

/** normalize transaction object from API or local */
function normalizeTxItem(t: any) {
  const original = t.original ?? t
  const p = original.payment ?? original.original_payment ?? null
  const invoiceAmtCandidate = p?.invoice_amount ?? p?.amount ?? original?.invoice_amount ?? null
  const invoiceCurCandidate = p?.invoice_currency ?? original?.invoice_currency ?? p?.currency ?? original?.currency ?? null
  const invoiceAmt = toNumberSafe(invoiceAmtCandidate)
  const txAmt = toNumberSafe(original?.amount ?? original?.total_amount ?? null)
  const txCurrency = (original?.currency || p?.currency || 'USD')?.toString().toUpperCase()
  let amountVal = null
  let currencyVal = 'USD'
  if (invoiceAmt !== null) { amountVal = invoiceAmt; currencyVal = (invoiceCurCandidate || txCurrency).toString().toUpperCase() }
  else if (txAmt !== null) { amountVal = txAmt; currencyVal = txCurrency }
  const totalAmtCandidate = p?.total_amount ?? original?.total_amount ?? null
  const totalAmt = toNumberSafe(totalAmtCandidate)

  return {
    id: original.id ?? original.transaction_id ?? null,
    account_number: original.account_number ?? null,
    account_id: original.account_id ?? null,
    user_phone: original.user_phone ?? null,
    transaction_id: original.transaction_id ?? original.id ?? null,
    reference_number: original.reference_number ?? original.ref ?? null,
    amount: amountVal,
    total_amount: totalAmt,
    currency: currencyVal,
    status: original.status ?? 'unknown',
    invoice_currency: original.invoice_currency ?? invoiceCurCandidate ?? null,
    created_at: original.created_at ?? original.cdc_transaction_datetime ?? original.createdAt ?? original.timestamp ?? null,
    service_name: original.service_name ?? original.service?.name ?? (p?.service?.name ?? null),
    service_logo_url: original.service_logo_url ?? original.service?.logo_url ?? (p?.service?.logo_url ?? null),
    fee: toNumberSafe(original.fee ?? p?.fee ?? null),
    customer_name: original.customer_name ?? p?.customer_name ?? null,
    original: original,
  }
}

/** Normalize payment object so modal sees consistent shape */
function normalizePayment(p: any) {
  if (!p) return null
  const original = p.original ?? p
  const invoiceCurrency = original.invoice_currency ?? original.currency ?? null
  const amount = toNumberSafe(original.invoice_amount ?? original.amount ?? original.total_amount) ?? null
  const fee = toNumberSafe(original.fee ?? null)
  const total = toNumberSafe(original.total_amount ?? null)
  return {
    id: original.id ?? original.payment_id ?? original.transaction_id ?? null,
    payment_id: original.payment_id ?? null,
    transaction_id: original.transaction_id ?? null,
    reference_number: original.reference_number ?? original.ref ?? null,
    amount,
    currency: original.currency ?? null,
    invoice_currency: invoiceCurrency,
    fee,
    total_amount: total,
    customer_name: original.customer_name ?? original.customer ?? null,
    service_name: (original.service?.name ?? original.service_name) ?? null,
    service_logo_url: (original.service?.logo_url ?? original.service_logo_url) ?? null,
    status: original.status ?? null,
    session_id: original.session_id ?? null,
    acknowledgement_id: original.acknowledgement_id ?? null,
    cdc_transaction_datetime: original.cdc_transaction_datetime ?? null,
    cdc_transaction_datetime_utc: original.cdc_transaction_datetime_utc ?? null,
    created_at: original.created_at ?? null,
    confirmed_at: original.confirmed_at ?? null,
    original,
  }
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
    accounts.value = (res ?? []).map((acc: any) => ({ ...acc, balance: Number(acc.balance ?? 0) }))
  } catch {
    toast.add({ title: 'Failed to load accounts', color: 'red' })
  } finally { accPending.value = false }
}

async function loadTxs(reset = false) {
  if (reset) txPage.value = 1
  txPending.value = true
  try {
    const res = await $api(`/adm/users/${id.value}/transactions`, {
      query: { q: txQ.value || undefined, page: txPage.value, page_size: txPageSize },
    })
    let items: any[] = []
    if (Array.isArray(res)) items = res
    else items = res.items ?? []
    txs.value = items.map(normalizeTxItem)
    txTotal.value = (Array.isArray(res) ? res.length : (res.total ?? txs.value.length))
  } catch (err) {
    toast.add({ title: 'Failed to load transactions', color: 'red' })
    txs.value = []
    txTotal.value = 0
  } finally { txPending.value = false }
}

async function loadPays(reset = false) {
  if (reset) payPage.value = 1
  payPending.value = true
  try {
    const res = await $api(`/adm/users/${id.value}/payments`, {
      query: { q: payQ.value || undefined, page: payPage.value, page_size: payPageSize },
    })
    let items: any[] = []
    if (Array.isArray(res)) items = res
    else items = res.items ?? []
    pays.value = items.map((p: any) => normalizePayment(p))
    payTotal.value = (Array.isArray(res) ? res.length : (res.total ?? pays.value.length))
  } catch (err) {
    toast.add({ title: 'Failed to load payments', color: 'red' })
    pays.value = []
    payTotal.value = 0
  } finally { payPending.value = false }
}

async function loadCurrencies() {
  try { currencyOptions.value = await $api('/adm/users/meta/currencies') } catch {}
}

/* ---------- Actions ---------- */
async function saveUser() {
  errorMsg.value = ''; successMsg.value = ''
  if (!form.name || !form.phone) {
    errorMsg.value = 'Name and phone are required'
    touched.value = true
    return
  }
  // PIN client-side validation: only allow save if empty or exactly 4 digits
  if (form.pin && !isPinValid.value) {
    errorMsg.value = 'PIN must be exactly 4 numeric digits'
    return
  }
  saving.value = true
  try {
    const payload: any = { name: form.name.trim(), phone: form.phone.trim(), role: form.role }
    if (form.password) payload.password = form.password.trim()
    // only include pin if set (backend treats absence differently)
    if (form.pin && form.pin.trim() !== '') payload.pin = form.pin.trim()
    await $api(`/adm/users/${id.value}`, { method: 'PUT', body: payload })
    successMsg.value = 'User updated successfully'
    await loadUser()
  } catch (e: any) {
    errorMsg.value = e?.data?.detail || 'Update failed'
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

/* ---------- Account modal handlers ---------- */
function openAccountModal(account: any) {
  if (!account) return
  selectedAccount.value = account
  Object.assign(accountForm, {
    id: account.id ?? null,
    name: account.name ?? '',
    number: account.number ?? '',
    currency: account.currency ?? 'USD',
    type: account.type ?? 'wallet',
    balance: Number(account.balance ?? 0),
  })
  showAccountDetail.value = true
}

function closeAccountModal() {
  showAccountDetail.value = false
  selectedAccount.value = null
  Object.assign(accountForm, { id: null, name: '', number: '', currency: 'USD', type: 'wallet', balance: 0 })
}

function onAccountRowSelect(e: Event, row: any) {
  const target = e.target as HTMLElement
  if (target.closest('button') || target.closest('a')) return
  const acc = row?.original
  if (acc) openAccountModal(acc)
}

async function saveAccountDetails() {
  if (!accountForm.id) {
    toast.add({ title: 'Account missing', color: 'error' })
    return
  }
  if (!accountForm.name || !accountForm.number) {
    toast.add({ title: 'Name and account number are required', color: 'orange' })
    return
  }
  savingAccount.value = true
  try {
    const payload: any = {
      name: accountForm.name?.trim(),
      number: accountForm.number?.trim(),
      currency: accountForm.currency,
      type: accountForm.type,
      balance: Number(accountForm.balance ?? 0),
    }
    await $api(`/adm/accounts/${accountForm.id}`, { method: 'PATCH', body: payload })
    toast.add({ title: 'Account updated', color: 'success' })
    showAccountDetail.value = false
    await loadAccounts()
  } catch (err: any) {
    console.error('Failed to update account', err)
    toast.add({ title: err?.data?.detail || 'Failed to update account', color: 'error' })
  } finally { savingAccount.value = false }
}

/* ---------- Transaction / Payment modals ---------- */
async function openTransactionModal(txId?: string | number) {
  if (!txId) return
  showTransactionDetail.value = false
  selectedTransaction.value = null

  const foundLocal = txs.value.find((t: any) => String(t.id) === String(txId) || String(t.transaction_id) === String(txId))
  if (foundLocal) {
    selectedTransaction.value = foundLocal
    showTransactionDetail.value = true
    return
  }

  txPending.value = true
  try {
    const res = await $api(`/adm/users/${id.value}/transactions`, { query: { page: 1, limit: 50 } })
    const items = Array.isArray(res) ? res : (res.items ?? [])
    const found = items.find((t: any) => String(t.id) === String(txId) || String(t.transaction_id) === String(txId) || String(t.reference_number) === String(txId))
    if (found) {
      selectedTransaction.value = normalizeTxItem(found)
      showTransactionDetail.value = true
      return
    }
    toast.add({ title: 'Transaction not found', color: 'orange' })
  } catch (err: any) {
    console.error('Failed to load transaction fallback', err)
    toast.add({ title: err?.data?.detail || 'Failed to load transaction', color: 'red' })
  } finally {
    txPending.value = false
  }
}

async function openPaymentModal(paymentId?: string | number) {
  if (!paymentId) return
  showPaymentDetail.value = false
  selectedPayment.value = null

  const foundLocal = pays.value.find((p: any) =>
    String(p.id) === String(paymentId) ||
    String(p.payment_id) === String(paymentId) ||
    String(p.reference_number) === String(paymentId) ||
    String(p.transaction_id) === String(paymentId)
  )
  if (foundLocal) {
    selectedPayment.value = normalizePayment(foundLocal)
    showPaymentDetail.value = true
    return
  }

  payPending.value = true
  try {
    const res = await $api(`/adm/users/${id.value}/payments`, { query: { page: 1, limit: 50 } })
    const items = Array.isArray(res) ? res : (res.items ?? [])
    const found = items.find((p: any) =>
      String(p.id) === String(paymentId) ||
      String(p.payment_id) === String(paymentId) ||
      String(p.reference_number) === String(paymentId) ||
      String(p.transaction_id) === String(paymentId)
    )
    if (found) {
      selectedPayment.value = normalizePayment(found)
      showPaymentDetail.value = true
      return
    }
    toast.add({ title: 'Payment not found', color: 'orange' })
  } catch (err: any) {
    console.error('Failed to load payment fallback', err)
    toast.add({ title: err?.data?.detail || 'Failed to load payment', color: 'red' })
  } finally {
    payPending.value = false
  }
}

/* Open add account and prefill from selected payment */
function openAddAccountFromPayment() {
  const p = selectedPayment.value
  Object.assign(newAccount, {
    name: p?.customer_name ?? '',
    number: p?.account_number ?? p?.reference_number ?? '',
    balance: Number(p?.amount ?? 0),
    currency: (p?.invoice_currency ?? p?.currency ?? 'USD'),
    type: 'wallet',
  })
  showAddAccount.value = true
}

/* Replace openTransaction navigation: row click should open modal */
function onTransactionRowSelect(e: Event, row: any) {
  const target = e.target as HTMLElement
  if (target.closest('button') || target.closest('a')) return
  const txId = row?.original?.transaction_id ?? row?.original?.id
  if (txId) openTransactionModal(txId)
}

/* On payment row select, open transaction modal if tx id exists, otherwise payment modal */
function onPaymentRowSelect(e: Event, row: any) {
  const target = e.target as HTMLElement
  if (target.closest('button') || target.closest('a')) return
  const paymentId = row?.original?.transaction_id ?? row?.original?.id
  if (paymentId) openPaymentModal(paymentId)
  else {
    selectedPayment.value = row.original
    showPaymentDetail.value = true
  }
}

/* helper to open related account from transaction modal */
function openAccountFromTransaction(tx: any) {
  const accNum = tx?.account_number ?? tx?.account?.number
  if (!accNum) return
  const found = accounts.value.find((a: any) => a.id === tx.account_id || a.number === accNum)
  if (found) {
    openAccountModal(found)
  } else if (tx.account_id) {
    try { navigateTo(`/adm/accounts/${tx.account_id}`) } catch { window.open(`/adm/accounts/${tx.account_id}`, '_self') }
  }
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
    : s === 'reversed' ? 'gray'
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

/* ---------- PIN helper & validation ---------- */
function digitsPin(e: any) {
  const v = e?.target?.value ?? ''
  form.pin = String(v).replace(/\D/g, '').slice(0, 4)
}
const isPinValid = computed(() => {
  if (!form.pin || form.pin === '') return true
  return /^\d{4}$/.test(String(form.pin))
})

/* ---------- Init ---------- */
onMounted(async () => {
  await Promise.all([loadUser(), loadAccounts(), loadTxs(), loadPays(), loadCurrencies()])
})
</script>

<style scoped>
td { vertical-align: middle; }
</style>
