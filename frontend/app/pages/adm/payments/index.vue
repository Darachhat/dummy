<!-- frontend/app/pages/adm/payments/index.vue -->
<script setup lang="ts">
definePageMeta({ layout: 'admin' })

import { ref, onMounted, computed, h, resolveComponent } from 'vue'
import type { ColumnDef } from '@tanstack/vue-table'
import { useMyToast } from '~/composables/useMyToast'
import { useCurrency } from '~/composables/useCurrency'
import AdminTablePage from '~/components/AdminTablePage.vue'

const UBadge = resolveComponent('UBadge')

const payments = ref<any[]>([])
const pending = ref(false)
const page = ref(1)
const pageSize = 10
const total = ref(0)
const toast = useMyToast()
const { $api } = useNuxtApp()
const { format: formatCurrency } = useCurrency()

async function load() {
  pending.value = true
  try {
    const res = await $api('/adm/payments', {
      query: { page: page.value, page_size: pageSize },
    })
    const raw = res.items ?? (Array.isArray(res) ? res : [])
    payments.value = raw
    total.value = res.total ?? payments.value.length
  } catch (err) {
    console.error('Failed to load payments:', err)
    toast.add({ title: 'Failed to load payments', color: 'error' })
    payments.value = []
    total.value = 0
  } finally {
    pending.value = false
  }
}

async function removePayment(id: number) {
  if (!confirm('Delete this payment?')) return
  try {
    await $api(`/adm/payments/${id}`, { method: 'DELETE' })
    toast.add({ title: 'Payment deleted', color: 'success' })
    await load()
  } catch (err) {
    console.error('Delete failed', err)
    toast.add({ title: 'Delete failed', color: 'error' })
  }
}

function go(p: number) {
  page.value = Math.max(1, p)
  load()
}

const adminTitle = useAdminTitle()
onMounted(() => {
  adminTitle.value = 'Payment Management'
  load()
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil((total.value || payments.value.length) / pageSize)),
)

const openDetail = (id: number) => navigateTo(`/adm/payments/${id}`)

/* -----------------------
   DATE HELPERS
------------------------ */
function parseToDate(s?: string | null): Date | null {
  if (!s) return null
  if (s instanceof Date) return s
  const str = String(s).trim()
  const hasTZ = /([zZ]|[+-]\d{2}:?\d{2})$/.test(str)
  const plainIsoNoTZ =
    /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?$/
  let iso = str
  if (!hasTZ && plainIsoNoTZ.test(str)) iso = str + 'Z'
  const d = new Date(iso)
  return isNaN(d.getTime()) ? null : d
}

function pad(n: number) {
  return String(n).padStart(2, '0')
}

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

type RowT = Record<string, any>

/* -----------------------------
    TABLE COLUMNS
------------------------------*/

const columns: ColumnDef<RowT, any>[] = [
  {
    accessorKey: 'id',
    header: 'ID',
    cell: ({ getValue }) => String(getValue() ?? '-'),
  },
  {
    accessorKey: 'customer_name',
    header: 'Customer',
    cell: ({ getValue }) => String(getValue() ?? '-'),
  },
  {
    accessorKey: 'service_name',
    header: 'Service',
    cell: ({ getValue }) => String(getValue() ?? '-'),
  },
  // STATUS with BADGE
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ getValue }) => {
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

      return h(
        UBadge,
        { class: 'capitalize', variant: 'subtle', color },
        () => status || '-',
      )
    },
  },
  // AMOUNT uses INVOICE CURRENCY
  {
    accessorKey: 'amount',
    header: 'Amount',
    cell: ({ getValue, row }) => {
      const cur =
        row.original.invoice_currency ??
        row.original.currency ??
        'USD'
      return formatCurrency(getValue(), cur)
    },
  },
  {
    accessorKey: 'invoice_currency',
    header: 'Invoice Currency',
    cell: ({ getValue }) => String(getValue() ?? '-'),
  },
  // FEE — ALWAYS USD
  {
    accessorKey: 'fee',
    header: 'Fee (USD)',
    cell: ({ getValue }) => formatCurrency(getValue(), 'USD'),
  },
  // TOTAL — ALWAYS USD
  {
    accessorKey: 'total_amount',
    header: 'Total (USD)',
    cell: ({ getValue }) => formatCurrency(getValue(), 'USD'),
  },
  {
    accessorKey: 'currency',
    header: 'Currency',
    cell: ({ getValue }) => String(getValue() ?? '-'),
  },
  {
    accessorKey: 'reference_number',
    header: 'Reference',
    cell: ({ getValue }) => String(getValue() ?? '-'),
  },
  {
    accessorKey: 'cdc_transaction_datetime',
    header: 'CDC Time',
    cell: ({ row }) => {
      const v =
        row.original.cdc_transaction_datetime ??
        row.original.cdc_transaction_datetime_utc
      return formatDateLocalMMDDYYYY_hhmmA(v)
    },
  },
  {
    accessorKey: 'created_at',
    header: 'Created At',
    cell: ({ getValue }) =>
      formatDateLocalMMDDYYYY_hhmmA(getValue()),
  },
]

/* Navigate row */
function onRowSelect(e: Event, row: any) {
  const target = e.target as HTMLElement
  if (target.closest('button') || target.closest('a')) return
  openDetail(row.original.id)
}
</script>

<template>
  <AdminTablePage
    title="Payment Management"
    :data="payments"
    :columns="columns"
    :loading="pending"
    :page="page"
    :total-pages="totalPages"
    :on-row-select="onRowSelect"
    :disable-pagination="pending"
    @change-page="go"
  >
    <template #loading>
      <div class="p-6 text-center text-gray-500">
        Loading payments…
      </div>
    </template>

    <template #empty>
      <div class="p-6 text-center text-gray-500">
        No payments found.
      </div>
    </template>

    <template #summary>
      Showing {{ payments.length }} of {{ total || payments.length }} —
      Page {{ page }} / {{ totalPages }}
    </template>
  </AdminTablePage>
</template>

<style scoped>
td {
  vertical-align: middle;
}
</style>
