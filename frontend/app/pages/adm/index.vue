<script setup lang="ts">
definePageMeta({ layout: 'admin' })

import { ref, reactive, onMounted, computed, h, resolveComponent } from 'vue'
import type { ColumnDef } from '@tanstack/vue-table'
import { useMyToast } from '~/composables/useMyToast'
import { useCurrency } from '~/composables/useCurrency'

const UBadge = resolveComponent('UBadge')

const { $api } = useNuxtApp()
const toast = useMyToast()
const adminTitle = useAdminTitle()
const { format: formatCurrency } = useCurrency()

adminTitle.value = 'Admin Dashboard'

// --- Overview stats ---
const loadingOverview = ref(false)
const stats = reactive({
  users: 0,
  services: 0,
  payments: 0,
  transactions: 0,
})

// --- Latest payments table ---
const latestPayments = ref<any[]>([])
const loadingPayments = ref(false)

// Simple date formatter (MM/DD/YYYY HH:mm)
function formatDateLocal(s?: string | null): string {
  if (!s) return '-'
  const d = new Date(s)
  if (Number.isNaN(d.getTime())) return '-'
  return d.toLocaleString(undefined, {
    month: '2-digit',
    day: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// ---- Navigation helpers ----
const goTo = (path: string) => navigateTo(path)

async function loadOverview() {
  loadingOverview.value = true
  try {
    const [usersRes, servicesRes, paymentsRes, txRes] = await Promise.all([
      $api('/adm/users', { query: { page: 1, page_size: 1 } }),
      $api('/adm/services', { query: { page: 1, page_size: 1 } }),
      $api('/adm/payments', { query: { page: 1, page_size: 1 } }),
      $api('/adm/transactions', { query: { page: 1, page_size: 1 } }).catch(
        () => null, // in case you don't have transactions endpoint yet
      ),
    ])

    stats.users = usersRes?.total ?? (usersRes?.items?.length ?? 0)
    stats.services = servicesRes?.total ?? (servicesRes?.items?.length ?? 0)
    stats.payments = paymentsRes?.total ?? (paymentsRes?.items?.length ?? 0)
    stats.transactions =
      txRes?.total ?? (txRes?.items?.length ?? 0) ?? 0
  } catch (err) {
    console.error('Failed to load overview', err)
    toast.add({ title: 'Failed to load overview', color: 'error' })
  } finally {
    loadingOverview.value = false
  }
}

async function loadLatestPayments() {
  loadingPayments.value = true
  try {
    const res: any = await $api('/adm/payments', {
      query: { page: 1, page_size: 5 },
    })
    latestPayments.value = res.items ?? (Array.isArray(res) ? res : [])
  } catch (err) {
    console.error('Failed to load latest payments', err)
    toast.add({ title: 'Failed to load latest payments', color: 'error' })
    latestPayments.value = []
  } finally {
    loadingPayments.value = false
  }
}

const loadingAny = computed(
  () => loadingOverview.value || loadingPayments.value,
)

// ---- payments table columns ----
type RowT = Record<string, any>

const columns = ref<ColumnDef<RowT, any>[]>([
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
    accessorKey: 'created_at',
    header: 'Created At',
    cell: ({ getValue }) => formatDateLocal(getValue()),
  },
])

function onRowSelect(e: Event, row: any) {
  const target = e.target as HTMLElement
  if (target.closest('button') || target.closest('a')) return
  if (row.original.id) {
    goTo(`/adm/payments/${row.original.id}`)
  }
}

onMounted(async () => {
  adminTitle.value = 'Admin Dashboard'
  await Promise.all([loadOverview(), loadLatestPayments()])
})
</script>

<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div
      class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 py-1"
    >
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">
          Admin Dashboard
        </h1>
        <p class="text-sm text-gray-500">
          Overview of users, services, and payment activity.
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <UButton
          color="neutral"
          variant="outline"
          icon="i-lucide-refresh-cw"
          :loading="loadingAny"
          @click="() => { loadOverview(); loadLatestPayments(); }"
        >
          Refresh
        </UButton>
      </div>
    </div>

    <!-- Stats cards -->
    <div
      class="grid gap-4 md:grid-cols-2 xl:grid-cols-4"
    >
      <UCard
        class="border rounded-2xl shadow-sm cursor-pointer hover:shadow-md transition-shadow"
        @click="goTo('/adm/users')"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs font-semibold tracking-wide text-gray-500 uppercase">
              Total Users
            </p>
            <p class="mt-2 text-2xl font-semibold text-gray-900">
              {{ stats.users }}
            </p>
          </div>
          <span
            class="inline-flex h-10 w-10 items-center justify-center rounded-full bg-blue-50 text-blue-500"
          >
            <i class="i-lucide-users-2"></i>
          </span>
        </div>
        <p class="mt-2 text-xs text-gray-500">
          Manage customers and admins.
        </p>
      </UCard>

      <UCard
        class="border rounded-2xl shadow-sm cursor-pointer hover:shadow-md transition-shadow"
        @click="goTo('/adm/payments')"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs font-semibold tracking-wide text-gray-500 uppercase">
              Payments
            </p>
            <p class="mt-2 text-2xl font-semibold text-gray-900">
              {{ stats.payments }}
            </p>
          </div>
          <span
            class="inline-flex h-10 w-10 items-center justify-center rounded-full bg-amber-50 text-amber-500"
          >
            <i class="i-lucide-credit-card"></i>
          </span>
        </div>
        <p class="mt-2 text-xs text-gray-500">
          Review payment status and amounts.
        </p>
      </UCard>

      <UCard
        class="border rounded-2xl shadow-sm cursor-pointer hover:shadow-md transition-shadow"
        @click="goTo('/adm/transactions')"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs font-semibold tracking-wide text-gray-500 uppercase">
              Transactions
            </p>
            <p class="mt-2 text-2xl font-semibold text-gray-900">
              {{ stats.transactions }}
            </p>
          </div>
          <span
            class="inline-flex h-10 w-10 items-center justify-center rounded-full bg-purple-50 text-purple-500"
          >
            <i class="i-lucide-arrow-left-right"></i>
          </span>
        </div>
        <p class="mt-2 text-xs text-gray-500">
          Bank-side transaction records.
        </p>
      </UCard>
      <UCard
        class="border rounded-2xl shadow-sm cursor-pointer hover:shadow-md transition-shadow"
        @click="goTo('/adm/services')"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs font-semibold tracking-wide text-gray-500 uppercase">
              Services
            </p>
            <p class="mt-2 text-2xl font-semibold text-gray-900">
              {{ stats.services }}
            </p>
          </div>
          <span
            class="inline-flex h-10 w-10 items-center justify-center rounded-full bg-emerald-50 text-emerald-500"
          >
            <i class="i-lucide-layers"></i>
          </span>
        </div>
        <p class="mt-2 text-xs text-gray-500">
          Configure payment services & logos.
        </p>
      </UCard>
    </div>

    <!-- Lower section: Latest payments + Quick actions -->
    <div class="grid gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
      <!-- Latest payments -->
      <UCard class="border rounded-2xl shadow-sm overflow-hidden">
        <div class="flex items-center justify-between px-4 pt-4 pb-2">
          <div>
            <h2 class="text-sm font-semibold text-gray-800">
              Latest Payments
            </h2>
            <p class="text-xs text-gray-500">
              Last 5 payment records.
            </p>
          </div>

          <UButton
            color="neutral"
            variant="ghost"
            size="xs"
            @click="goTo('/adm/payments')"
          >
            View all
          </UButton>
        </div>

        <UTable
          :data="latestPayments"
          :columns="columns"
          :loading="loadingPayments"
          :onSelect="onRowSelect"
          class="min-w-full"
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
        </UTable>
      </UCard>

      <!-- Quick actions -->
      <UCard class="border rounded-2xl shadow-sm">
        <div class="px-4 pt-4 pb-2">
          <h2 class="text-sm font-semibold text-gray-800">
            Quick Actions
          </h2>
          <p class="text-xs text-gray-500">
            Common admin tasks in one place.
          </p>
        </div>

        <div class="px-4 pb-4 space-y-3">
          <UButton
            block
            class="justify-start"
            icon="i-lucide-user-plus"
            color="neutral"
            variant="outline"
            @click="goTo('/adm/users')"
          >
            Manage users
          </UButton>

          <UButton
            block
            class="justify-start"
            icon="i-lucide-plus-circle"
            color="neutral"
            variant="outline"
            @click="goTo('/adm/services')"
          >
            Configure services
          </UButton>

          <UButton
            block
            class="justify-start"
            icon="i-lucide-credit-card"
            color="neutral"
            variant="outline"
            @click="goTo('/adm/payments')"
          >
            Review payments
          </UButton>

          <UButton
            block
            class="justify-start"
            icon="i-lucide-arrow-left-right"
            color="neutral"
            variant="outline"
            @click="goTo('/adm/transactions')"
          >
            View transactions
          </UButton>
        </div>
      </UCard>
    </div>
  </div>
</template>
