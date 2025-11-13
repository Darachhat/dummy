<script setup lang="ts">
definePageMeta({ layout: 'admin' })

import { ref, onMounted, computed, h, resolveComponent } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMyToast } from '~/composables/useMyToast'
import { useCurrency } from '~/composables/useCurrency'

const route = useRoute()
const router = useRouter()
const toast = useMyToast()
const UBadge = resolveComponent('UBadge')

const payment = ref<any>(null)
const loading = ref(false)
const saving = ref(false)

const { $api } = useNuxtApp()
const { format: formatCurrency } = useCurrency()

async function loadPayment() {
  const id = route.params.id
  if (!id) {
    toast.add({ title: 'Missing payment id', color: 'error' })
    return
  }
  loading.value = true
  try {
    const res = await $api(`/adm/payments/${id}`)
    payment.value = res
  } catch (err) {
    console.error('Failed to load payment', err)
    toast.add({ title: 'Failed to load payment', color: 'error' })
  } finally {
    loading.value = false
  }
}

async function updateStatus(status: string) {
  const id = payment.value?.id
  if (!id) return
  saving.value = true
  try {
    await $api(`/adm/payments/${id}/status`, { method: 'PUT', body: status })
    toast.add({ title: 'Status updated', color: 'success' })
    await loadPayment()
  } catch (err) {
    console.error('Update failed', err)
    toast.add({ title: 'Update failed', color: 'error' })
  } finally {
    saving.value = false
  }
}

async function deletePayment() {
  const id = payment.value?.id
  if (!id) return
  if (!confirm('Delete this payment?')) return
  saving.value = true
  try {
    await $api(`/adm/payments/${id}`, { method: 'DELETE' })
    toast.add({ title: 'Payment deleted', color: 'success' })
    router.push('/adm/payments')
  } catch (err) {
    console.error('Delete failed', err)
    toast.add({ title: 'Delete failed', color: 'error' })
  } finally {
    saving.value = false
  }
}

/* -----------------------
   Date helpers
------------------------ */
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
function pad(n: number, len = 2) { return String(n).padStart(len, '0') }
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

/* formatting helpers for amounts, fee, total */
function formatAmountByInvoice(value?: number | string | null) {
  const cur = payment.value?.invoice_currency ?? payment.value?.currency ?? 'USD'
  return formatCurrency(value, cur)
}
function formatFeeUSD(value?: number | string | null) {
  return formatCurrency(value, 'USD')
}
function formatTotalUSD(value?: number | string | null) {
  return formatCurrency(value, 'USD')
}

/* admin title */
const adminTitle = useAdminTitle()
adminTitle.value = 'Payment Details'

onMounted(loadPayment)
</script>

<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-2">
        <UButton size="md" color="neutral" variant="outline" @click="router.push('/adm/payments')">Back</UButton>
      </div>

      <div>
        <h1 class="text-2xl font-semibold">Payment #{{ payment?.id ?? route.params.id }}</h1>
        <p class="text-sm text-gray-500">{{ payment?.customer_name ?? '-' }}</p>
      </div>
    </div>

    <UCard class="border rounded-2xl p-4">
      <div v-if="loading" class="text-gray-500">Loading...</div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <p class="text-sm text-gray-500">Customer</p>
          <p class="font-medium">{{ payment?.customer_name ?? '-' }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">Service</p>
          <p class="font-medium">{{ payment?.service_name ?? payment?.service_code ?? '-' }}</p>
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
              }[ (payment?.status ?? '').toString().toLowerCase() ] ?? 'neutral'"
            >
              {{ (payment?.status ?? '-').toString().toLowerCase() }}
            </component>
          </div>
        </div>

        <div>
          <p class="text-sm text-gray-500">Amount</p>
          <p class="font-medium">
            {{ formatAmountByInvoice(payment?.amount) }}
          </p>
        </div>

        <div>
          <p class="text-sm text-gray-500">Invoice Currency</p>
          <p class="font-medium">{{ payment?.invoice_currency ?? '-' }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">Fee (USD)</p>
          <p class="font-medium">{{ formatFeeUSD(payment?.fee) }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">Total (USD)</p>
          <p class="font-medium">{{ formatTotalUSD(payment?.total_amount) }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">Currency</p>
          <p class="font-medium">{{ payment?.currency ?? '-' }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">Reference</p>
          <p class="font-medium">{{ payment?.reference_number ?? payment?.reference ?? payment?.txid ?? '-' }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">Acknowledgement ID</p>
          <p class="font-medium">{{ payment?.acknowledgement_id ?? '-' }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">Session ID</p>
          <p class="font-medium break-all">{{ payment?.session_id ?? '-' }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">CDC Transaction</p>
          <p class="font-medium">
            {{ formatDateLocalMMDDYYYY_hhmmA(payment?.cdc_transaction_datetime ?? payment?.cdc_transaction_datetime_utc) }}
          </p>
        </div>

        <div>
          <p class="text-sm text-gray-500">Confirmed At</p>
          <p class="font-medium">{{ formatDateLocalMMDDYYYY_hhmmA(payment?.confirmed_at) }}</p>
        </div>

        <div>
          <p class="text-sm text-gray-500">Created</p>
          <p class="font-medium">{{ formatDateLocalMMDDYYYY_hhmmA(payment?.created_at) }}</p>
        </div>

        <div class="md:col-span-2">
          <p class="text-sm text-gray-500">Rawt</p>
          <pre class="bg-gray-50 rounded p-3 text-sm overflow-auto" style="max-height:360px;">{{ JSON.stringify(payment ?? {}, null, 2) }}</pre>
        </div>
      </div>
    </UCard>
  </div>
</template>

<style scoped>
pre { white-space: pre-wrap; }
</style>
