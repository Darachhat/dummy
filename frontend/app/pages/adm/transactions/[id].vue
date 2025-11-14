<script setup lang="ts">
definePageMeta({ layout: 'admin' })

import { ref, onMounted, h, resolveComponent } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMyToast } from '~/composables/useMyToast'
import { useCurrency } from '~/composables/useCurrency'

const route = useRoute()
const router = useRouter()
const toast = useMyToast()
const UBadge = resolveComponent('UBadge')

const transaction = ref<any>(null)
const loading = ref(false)
const saving = ref(false)

const { $api } = useNuxtApp()
const { format: formatCurrency } = useCurrency()

async function loadTransaction() {
  const id = route.params.id
  if (!id) {
    toast.add({ title: 'Missing transaction id', color: 'error' })
    return
  }
  loading.value = true
  try {
    const res = await $api(`/adm/transactions/${id}`)
    transaction.value = res
  } catch (err) {
    console.error('Failed to load transaction', err)
    toast.add({ title: 'Failed to load transaction', color: 'error' })
  } finally {
    loading.value = false
  }
}

async function deleteTransaction() {
  const id = transaction.value?.id
  if (!id) return
  if (!confirm('Delete this transaction?')) return
  saving.value = true
  try {
    await $api(`/adm/transactions/${id}`, { method: 'DELETE' })
    toast.add({ title: 'Transaction deleted', color: 'success' })
    router.push('/adm/transactions')
  } catch (err) {
    console.error('Delete failed', err)
    toast.add({ title: 'Delete failed', color: 'error' })
  } finally {
    saving.value = false
  }
}

/* date helpers */
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
function pad(n: number) { return String(n).padStart(2, '0') }
function formatDateLocalMMDDYYYY_hhmmA(s?: string | null): string {
  const d = parseToDate(s)
  if (!d) return '-'
  const month = pad(d.getMonth() + 1)
  const day = pad(d.getDate())
  const year = d.getFullYear()
  let hh = d.getHours()
  const ampm = hh >= 12 ? 'PM' : 'AM'
  hh = hh % 12
  if (hh === 0) hh = 12
  const mm = pad(d.getMinutes())
  return `${month}/${day}/${year} ${pad(hh)}:${mm} ${ampm}`
}

/* format helpers for amounts */
function formatAmount(value?: number | string | null) {
  const cur = transaction.value?.invoice_currency ?? transaction.value?.currency ?? 'USD'
  return formatCurrency(value, cur)
}
function formatFeeUSD(value?: number | string | null) {
  return formatCurrency(value, 'USD')
}
function formatTotalUSD(value?: number | string | null) {
  return formatCurrency(value, 'USD')
}

/* admin topbar */
const adminTitle = useAdminTitle()
adminTitle.value = 'Transaction Details'

onMounted(loadTransaction)
</script>

<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-2">
        <UButton size="xl" color="neutral" variant="outline" @click="router.push('/adm/transactions')">Back</UButton>
      </div>

      <div class="text-center">
        <h1 class="text-2xl font-semibold">Transaction #{{ transaction?.id ?? route.params.id }}</h1>
        <p class="text-sm text-gray-500">{{ transaction?.transaction_id ?? '-' }}</p>
      </div>

      <!-- <div class="flex items-center gap-2">
        <UButton size="sm" color="danger" variant="ghost" :loading="saving" @click="deleteTransaction">Delete</UButton>
      </div> -->
    </div>

    <UCard class="border rounded-2xl p-4">
      <div v-if="loading" class="text-gray-500">Loading...</div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Transaction / Payment info -->
        <div>
          <p class="text-sm text-gray-500">Transaction ID</p>
          <p class="font-medium">{{ transaction?.transaction_id ?? '-' }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">Reference</p>
          <p class="font-medium">{{ transaction?.reference_number ?? '-' }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">Customer</p>
          <p class="font-medium">{{ transaction?.customer_name ?? '-' }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">Service</p>
          <p class="font-medium">{{ transaction?.service_name ?? '-' }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">Direction</p>
          <p class="font-medium">{{ transaction?.direction ?? '-' }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">Status</p>
          <div class="mt-1">
            <component
              :is="UBadge"
              class="capitalize"
              variant="subtle"
              :color="{
                confirmed: 'success',
                success: 'success',
                pending: 'neutral',
                started: 'neutral',
                failed: 'error',
                canceled: 'error'
              }[(transaction?.status ?? '').toString().toLowerCase()] ?? 'neutral'"
            >
              {{ (transaction?.status ?? '-').toString().toLowerCase() }}
            </component>
          </div>
        </div>

        <!-- Amount & currencies -->
        <div>
          <p class="text-sm text-gray-500">Amount</p>
          <p class="font-medium">{{ formatAmount(transaction?.amount) }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">Invoice Currency</p>
          <p class="font-medium">{{ transaction?.invoice_currency ?? transaction?.currency ?? '-' }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">Fee (USD)</p>
          <p class="font-medium">{{ formatFeeUSD(transaction?.fee) }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">Total (USD)</p>
          <p class="font-medium">{{ formatTotalUSD(transaction?.total_amount ?? transaction?.amount) }}</p>
        </div>

        <!-- Account / User info -->
        <div>
          <p class="text-sm text-gray-500">Account Number</p>
          <p class="font-medium">{{ transaction?.account_number ?? '-' }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">User Name</p>
          <p class="font-medium">{{ transaction?.user_name ?? '-' }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">User Phone</p>
          <p class="font-medium">{{ transaction?.user_phone ?? '-' }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">Created</p>
          <p class="font-medium">{{ formatDateLocalMMDDYYYY_hhmmA(transaction?.created_at) }}</p>
        </div>

        <div class="md:col-span-2">
          <p class="text-sm text-gray-500">Raw</p>
          <pre class="bg-gray-50 rounded p-3 text-sm overflow-auto" style="max-height:360px;">{{ JSON.stringify(transaction ?? {}, null, 2) }}</pre>
        </div>
      </div>
    </UCard>
  </div>
</template>

<style scoped>
pre { white-space: pre-wrap; }
</style>
