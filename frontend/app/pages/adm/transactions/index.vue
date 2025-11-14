<script setup lang="ts">
definePageMeta({ layout: 'admin' })

import { ref, onMounted, computed, h, resolveComponent } from 'vue'
import { type ColumnDef } from '@tanstack/vue-table'
import { useMyToast } from '~/composables/useMyToast'
import { useCurrency } from '~/composables/useCurrency'

const UBadge = resolveComponent('UBadge')

const transactions = ref<any[]>([])
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
    const res = await $api('/adm/transactions', { query: { page: page.value, page_size: pageSize } })
    const raw = res.items ?? (Array.isArray(res) ? res : [])
    transactions.value = raw
    total.value = res.total ?? transactions.value.length
  } catch (err) {
    console.error('Failed to load transactions:', err)
    toast.add({ title: 'Failed to load transactions', color: 'error' })
    transactions.value = []
    total.value = 0
  } finally {
    pending.value = false
  }
}

async function removeTx(id: number) {
  if (!confirm('Delete this transaction?')) return
  try {
    await $api(`/adm/transactions/${id}`, { method: 'DELETE' })
    toast.add({ title: 'Transaction deleted', color: 'success' })
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
  adminTitle.value = 'Transactions'
  load()
})

const totalPages = computed(() => Math.max(1, Math.ceil((total.value || transactions.value.length) / pageSize)))

const openDetail = (id: number) => navigateTo(`/adm/transactions/${id}`)

/* date helper */
function parseDate(s?: string | null) {
  if (!s) return null
  const d = new Date(String(s))
  if (isNaN(d.getTime())) return null
  return d
}
function formatDateLocal(s?: string | null) {
  const d = parseDate(s)
  if (!d) return '-'
  return d.toLocaleString(undefined, { hour12: true })
}

/* Columns */
type RowT = Record<string, any>
const columns = ref<ColumnDef<RowT, any>[]>([
  {
    accessorKey: 'id',
    header: 'ID',
    cell: ({ getValue }) => String(getValue() ?? '-')
  },
  {
    accessorKey: 'transaction_id',
    header: 'Transaction ID',
    cell: ({ getValue }) => String(getValue() ?? '-')
  },
  {
    accessorKey: 'customer_name',
    header: 'User Name',
    cell: ({ getValue, row }) => String(getValue() ?? row.original.user_name ?? '-')
  },
  {
    accessorKey: 'user_phone',
    header: 'User Phone',
    cell: ({ getValue, row }) => String(getValue() ?? row.original.customer_phone ?? row.original.phone ?? '-')
  },
  {
    accessorKey: 'account_number',
    header: 'Account Number',
    cell: ({ getValue, row }) => String(row.original.account_number ?? getValue() ?? '-')
  },
  {
    accessorKey: 'reference_number',
    header: 'Reference',
    cell: ({ getValue }) => String(getValue() ?? '-')
  },
  {
    accessorKey: 'amount',
    header: 'Amount',
    cell: ({ getValue, row }) => {
      const cur = row.original.invoice_currency ?? row.original.currency ?? 'USD'
      return formatCurrency(getValue() as number | string | null, cur)
    }
  },
  {
    accessorKey: 'invoice_currency',
    header: 'Invoice Currency',
    cell: ({ getValue }) => String(getValue() ?? '-')
  },
  {
    accessorKey: 'service_name',
    header: 'Service',
    cell: ({ getValue }) => String(getValue() ?? '-')
  },

  // Status column with UBadge
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => {
      const raw = row.original.status ?? ''
      const status = String(raw).trim().toLowerCase()
      const color = {
        confirmed: 'success',
        success: 'success',
        pending: 'neutral',
        started: 'neutral',
        failed: 'error',
        canceled: 'error'
      }[status] ?? 'neutral'
      return h(UBadge, { class: 'capitalize', variant: 'subtle', color }, () => status || '-')
    }
  },

  {
    accessorKey: 'created_at',
    header: 'Created At',
    cell: ({ getValue, row }) => formatDateLocal(row.original.created_at ?? getValue())
  },
])

function onRowSelect(e: Event, row: any) {
  const target = e.target as HTMLElement
  if (target.closest('button') || target.closest('a')) return
  const id = row.original.id
  if (id) openDetail(id)
}
</script>

<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-2xl font-bold">Transaction Management</h1>
      <div class="text-sm text-gray-600">Showing {{ transactions.length }} of {{ total || transactions.length }}</div>
    </div>

    <UCard class="shadow-sm border rounded-xl overflow-hidden">
      <UTable
        :data="transactions"
        :columns="columns"
        :loading="pending"
        :onSelect="onRowSelect"
        class="min-w-full"
      >
        <template #loading>
          <div class="p-6 text-center text-gray-500">Loading transactions…</div>
        </template>

        <template #empty>
          <div class="p-6 text-center text-gray-500">No transactions found.</div>
        </template>
      </UTable>

      <template #footer>
        <div class="flex items-center justify-between p-3 text-sm text-gray-600">
          <div>Page {{ page }} / {{ totalPages }}</div>
          <div class="flex gap-2">
            <UButton label="Prev" color="neutral" variant="outline" :disabled="page <= 1 || pending" @click="go(page-1)" />
            <UButton label="Next" class="btn-dark" :disabled="page >= totalPages || pending" @click="go(page+1)" />
          </div>
        </div>
      </template>
    </UCard>
  </div>
</template>

<style scoped>
td { vertical-align: middle; }
.break-ref { max-width: 220px; word-break: break-word; }
</style>
