<template>
  <div class="min-h-screen flex bg-gray-50 relative">
    <!-- Overlay for mobile -->
    <div
      v-if="sidebarOpen && !isDesktop"
      class="fixed inset-0 bg-black bg-opacity-40 z-30"
      @click="sidebarOpen = false"
    ></div>

    <!-- Sidebar -->
    <aside
      :class="[
        'bg-white shadow-sm z-40 transform transition-transform duration-300 ease-in-out fixed md:static md:translate-x-0',
        'h-screen md:h-auto w-64 flex flex-col justify-between p-6 md:min-h-screen',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <div class="flex-1 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-8">
            <h1 class="text-2xl font-bold text-gray-800">Admin</h1>
            <button
              v-if="!isDesktop"
              @click="sidebarOpen = false"
              class="text-gray-500 hover:text-gray-800 md:hidden"
            >
              <X class="w-5 h-5" />
            </button>
          </div>

          <nav class="space-y-3 flex-1">
            <SidebarItem label="Home" icon="Home" to="/admin" />
            <SidebarItem label="User Management" icon="User" to="/admin/users" />
            <SidebarItem label="Payments" icon="CreditCard" to="/admin/payments" />
            <SidebarItem label="Transactions" icon="List" to="/admin/transactions" />
            <SidebarItem label="Service Management" icon="List" to="/admin/services" />
          </nav>
        </div>

        <button
          @click="logout"
          class="flex items-center gap-2 text-gray-500 hover:text-red-600 transition mt-8"
        >
          <LogOut class="w-5 h-5" />
          <span>Logout</span>
        </button>
      </div>
    </aside>

    <!-- Main content -->
    <main class="flex-1 flex flex-col p-4 md:p-8 w-full relative">
      <!-- Header -->
      <div class="hidden md:flex justify-between items-center mb-8">
        <h2 class="text-2xl font-bold text-gray-800 capitalize">User #{{ id }}</h2>
        <NuxtLink to="/admin/users" class="px-3 py-1 border rounded-xl">Back</NuxtLink>
      </div>

      <!-- User Info -->
      <section class="rounded-2xl border bg-white mb-8">
        <div class="px-4 py-3 border-b font-medium">User Info</div>
        <div class="p-4 grid md:grid-cols-2 gap-4 text-sm">
          <FormRow label="Name">{{ user?.name || '-' }}</FormRow>
          <FormRow label="Phone">{{ user?.phone || '-' }}</FormRow>
          <FormRow label="Role">{{ user?.role || '-' }}</FormRow>
          <FormRow label="Created At">{{ formatDate(user?.created_at) }}</FormRow>
        </div>
      </section>

      <!-- ACCOUNTS TABLE -->
      <section class="rounded-2xl border bg-white mb-8">
        <div class="px-4 py-3 border-b font-medium flex justify-between items-center">
          <span>Accounts</span>
          <UButton size="sm" label="Refresh" @click="loadAll" />
        </div>

        <UTable
          :data="accounts"
          :columns="accountColumns"
          :loading="loading"
          class="h-auto"
        >
          <template #empty>
            <div class="text-center py-6 text-gray-500">No accounts found</div>
          </template>
        </UTable>
      </section>

      <!-- TRANSACTIONS TABLE -->
      <section class="rounded-2xl border bg-white mb-8">
        <div class="px-4 py-3 border-b font-medium flex justify-between items-center">
          <span>Transactions</span>
          <div class="flex gap-2">
            <UInput v-model="filterTx" placeholder="Search..." class="min-w-[200px]" />
            <UButton size="sm" label="Load More" @click="loadMoreTransactions" :disabled="transactions.length >= txTotal" />
          </div>
        </div>

        <UTable
          :data="filteredTransactions"
          :columns="transactionColumns"
          :loading="txLoading"
          sticky
          class="h-auto"
        >
          <template #empty>
            <div class="text-center py-6 text-gray-500">No transactions found</div>
          </template>
        </UTable>
      </section>

      <!-- PAYMENTS TABLE -->
      <section class="rounded-2xl border bg-white mb-8">
        <div class="px-4 py-3 border-b font-medium flex justify-between items-center">
          <span>Payments</span>
          <div class="flex gap-2">
            <UInput v-model="filterPay" placeholder="Search..." class="min-w-[200px]" />
            <UButton size="sm" label="Load More" @click="loadMorePayments" :disabled="payments.length >= payTotal" />
          </div>
        </div>

        <UTable
          :data="filteredPayments"
          :columns="paymentColumns"
          :loading="payLoading"
          sticky
          class="h-auto"
        >
          <template #empty>
            <div class="text-center py-6 text-gray-500">No payments found</div>
          </template>
        </UTable>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import SidebarItem from '~/components/SidebarItem.vue'
import { LogOut, Menu, X } from 'lucide-vue-next'
import { h, defineComponent, computed } from 'vue'
import { createColumnHelper } from '@tanstack/vue-table'

const { $api } = useNuxtApp()
const { logout } = useAuth()
const route = useRoute()
const id = computed(() => route.params.id)
const toast = useToast()

// Layout state
const isDesktop = ref(false)
const sidebarOpen = ref(false)
onMounted(() => {
  const updateScreen = () => { isDesktop.value = window.innerWidth >= 768 }
  updateScreen()
  window.addEventListener('resize', updateScreen)
})
onBeforeUnmount(() => window.removeEventListener('resize', () => {}))

// Data
const user = ref<any>(null)
const accounts = ref<any[]>([])
const transactions = ref<any[]>([])
const payments = ref<any[]>([])

// Pagination & Filters
const txPage = ref(1)
const txLimit = 10
const txTotal = ref(0)
const payPage = ref(1)
const payLimit = 10
const payTotal = ref(0)
const filterTx = ref('')
const filterPay = ref('')

// Load states
const loading = ref(false)
const txLoading = ref(false)
const payLoading = ref(false)

// Tanstack columns
const accountColumns = [
  { accessorKey: 'account_number', header: 'Account Number' },
  { accessorKey: 'balance', header: 'Balance', enableSorting: true },
  { accessorKey: 'currency', header: 'Currency' },
  { accessorKey: 'status', header: 'Status' },
]

const transactionColumns = [
  { accessorKey: 'id', header: 'ID', enableSorting: true },
  { accessorKey: 'amount', header: 'Amount', enableSorting: true },
  { accessorKey: 'currency', header: 'Currency' },
  { accessorKey: 'direction', header: 'Direction' },
  { accessorKey: 'service_name', header: 'Service' },
  { accessorKey: 'created_at', header: 'Date' },
]

const paymentColumns = [
  { accessorKey: 'id', header: 'ID', enableSorting: true },
  { accessorKey: 'reference_number', header: 'Reference' },
  { accessorKey: 'amount', header: 'Amount' },
  { accessorKey: 'currency', header: 'Currency' },
  { accessorKey: 'status', header: 'Status' },
  { accessorKey: 'service_name', header: 'Service' },
  { accessorKey: 'created_at', header: 'Date' },
]


// Computed filters
const filteredTransactions = computed(() =>
  transactions.value.filter(t =>
    Object.values(t).some(v => String(v).toLowerCase().includes(filterTx.value.toLowerCase()))
  )
)

const filteredPayments = computed(() =>
  payments.value.filter(p =>
    Object.values(p).some(v => String(v).toLowerCase().includes(filterPay.value.toLowerCase()))
  )
)

// Load data
async function loadAll(reset = true) {
  try {
    loading.value = true
    const res = await $api(`/admin/users/${id.value}?include=accounts,transactions,payments&page=${txPage.value}&limit=${txLimit}`)
    user.value = res
    accounts.value = res.accounts || []
    if (reset) {
      transactions.value = res.transactions?.items || []
      payments.value = res.payments?.items || []
    } else {
      transactions.value.push(...(res.transactions?.items || []))
      payments.value.push(...(res.payments?.items || []))
    }
    txTotal.value = res.transactions?.total || 0
    payTotal.value = res.payments?.total || 0
  } catch (err) {
    console.error(err)
    toast.add({ title: 'Failed to load data', color: 'red' })
  } finally {
    loading.value = false
  }
}

async function loadMoreTransactions() {
  if (transactions.value.length >= txTotal.value) return
  txPage.value++
  txLoading.value = true
  await loadAll(false)
  txLoading.value = false
}

async function loadMorePayments() {
  if (payments.value.length >= payTotal.value) return
  payPage.value++
  payLoading.value = true
  await loadAll(false)
  payLoading.value = false
}

onMounted(() => loadAll())

// Utilities
function formatDate(s?: string) {
  return s ? new Date(s).toLocaleString() : '-'
}

// FormRow for User Info
const FormRow = defineComponent({
  props: { label: { type: String, required: true } },
  setup(props, { slots }) {
    return () =>
      h('div', { class: 'flex flex-col' }, [
        h('div', { class: 'text-gray-500 text-xs mb-1' }, props.label),
        h('div', { class: 'font-medium' }, slots.default ? slots.default() : null),
      ])
  },
})
</script>
