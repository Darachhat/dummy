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
        'rounded-none md:rounded-xl',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full',
      ]"
    >
      <div class="flex-1 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-8">
            <h1 class="text-2xl font-bold text-gray-800">DummyBank</h1>
            <button
              v-if="!isDesktop"
              @click="sidebarOpen = false"
              class="text-gray-500 hover:text-gray-800 md:hidden"
            >
              <X class="w-5 h-5" />
            </button>
          </div>

          <nav class="space-y-3 flex-1">
            <SidebarItem label="Home" icon="Home" to="/" :collapsed="!isDesktop" />
            <SidebarItem label="Payments" icon="CreditCard" to="/payment/start" :collapsed="!isDesktop" />
            <SidebarItem label="Transactions" icon="List" to="/transactions" :collapsed="!isDesktop" />
            <SidebarItem label="Accounts" icon="User" to="/accounts" :collapsed="!isDesktop" />
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
      <!-- Mobile Navbar -->
      <div
        class="flex items-center md:hidden mb-6 sticky top-0 bg-gray-50 z-20 px-2 py-2"
      >
        <button
          @click="sidebarOpen = true"
          class="text-gray-700 hover:text-gray-900"
        >
          <Menu class="w-6 h-6" />
        </button>
        <h2 class="ml-3 text-lg font-semibold truncate">
          {{ currentPageTitle }}
        </h2>
      </div>

      <!-- Desktop header -->
      <div class="hidden md:flex justify-between items-center mb-8">
        <h2 class="text-2xl font-bold text-gray-800 capitalize">
          {{ currentPageTitle }}
        </h2>
      </div>

      <!-- Account Summary (Only for Home page) -->
      <div
        v-if="route.path === '/'"
        class="flex flex-col md:flex-row gap-6 mb-10"
      >
        <div class="bg-white rounded-xl shadow p-6 flex-1 text-center md:text-left">
          <p class="text-sm text-gray-500">Total Balance</p>
          <h1 class="text-3xl md:text-4xl font-bold text-gray-900 mt-2">
            {{ formatCurrency(balance) }}
          </h1>
        </div>

        <div
          class="bg-gradient-to-r from-gray-800 to-gray-900 text-white rounded-xl shadow-lg p-6 flex-1"
        >
          <h3 class="text-lg font-semibold">Primary Account</h3>
          <p class="text-sm mt-2 text-gray-300">{{ accountName || '—' }}</p>
          <div class="mt-6 text-xl tracking-widest break-all">
            {{ maskedAccountNumber }}
          </div>
          <div class="mt-4 text-sm text-gray-400">
            {{ accountType }}
          </div>
        </div>
      </div>

      <!-- Recent Transactions (Only for Home page) -->
      <section v-if="route.path === '/'">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-800">Recent Transactions</h3>
          <button
            @click="goTransactions"
            class="text-sm text-gray-500 hover:text-gray-800"
          >
            See all
          </button>
        </div>

        <div
          v-if="transactions.length"
          class="bg-white rounded-xl shadow divide-y divide-gray-100"
        >
          <div
            v-for="t in transactions"
            :key="t.id"
            @click="goDetail(t.id)"
            class="flex flex-col sm:flex-row sm:items-center sm:justify-between px-4 py-3 hover:bg-gray-50 transition cursor-pointer"
          >
            <div class="flex items-center gap-3 mb-2 sm:mb-0">
              <img
                v-if="t.service_logo_url"
                :src="getLogoUrl(t.service_logo_url)"
                alt="Logo"
                class="w-10 h-10 rounded-full object-contain"
              />
              <div>
                <p class="text-sm font-semibold text-gray-800">
                  {{ t.service_name || 'Transaction' }}
                </p>
                <p class="text-xs text-gray-500">
                  Ref: {{ t.reference_number }}
                </p>
              </div>
            </div>

            <div class="text-right">
              <p
                :class="[
                  'text-sm font-semibold',
                  t.direction === 'debit' ? 'text-red-600' : 'text-green-600',
                ]"
              >
                {{ t.direction === 'debit' ? '-' : '+' }}
                {{ formatCurrency(t.amount) }}
              </p>
              <p class="text-xs text-gray-500">
                {{ formatDate(t.created_at) }}
              </p>
            </div>
          </div>
        </div>

        <p v-else class="text-gray-500 text-center mt-6">
          No recent transactions available.
        </p>
      </section>

      <!-- Floating Action Button (FAB) -->
      <transition name="fade">
        <div
          v-if="!isDesktop"
          class="fixed bottom-6 right-6 flex flex-col items-end space-y-3 z-50"
        >
          <!-- Action Sheet -->
          <transition name="slide-up">
            <div
              v-if="showActions"
              class="bg-white rounded-lg shadow-lg border border-gray-200 w-44 py-2 text-sm"
            >
              <button
                v-for="action in fabActions"
                :key="action.label"
                @click="handleAction(action)"
                class="block w-full text-left px-4 py-2 hover:bg-gray-100"
              >
                {{ action.label }}
              </button>
            </div>
          </transition>

          <!-- Main FAB -->
          <button
            @click="toggleActions()"
            class="w-14 h-14 bg-gradient-to-r from-gray-800 to-gray-900 text-white rounded-full shadow-lg flex items-center justify-center hover:bg-blue-700 transition"
          >
            <Plus class="w-7 h-7" />
          </button>
        </div>
      </transition>
    </main>
  </div>
</template>

<script setup lang="ts">
import SidebarItem from '~/components/SidebarItem.vue'
import { LogOut, Menu, X, Plus } from 'lucide-vue-next'
import { useRoute } from 'vue-router'
import { useCurrency } from '~/composables/useCurrency'
import { useMediaQuery } from '@vueuse/core'

const { $api } = useNuxtApp()
const { logout } = useAuth()
const route = useRoute()

const balance = ref(0)
const transactions = ref<any[]>([])
const accountName = ref('')
const accountNumber = ref('')
const accountType = ref('Main Wallet')

const sidebarOpen = ref(false)
const showActions = ref(false)

const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase

// Responsive: desktop vs mobile
const isDesktop = useMediaQuery('(min-width: 768px)')

// Close sidebar when switching to desktop
watch(isDesktop, (val) => {
  if (val) sidebarOpen.value = false
})

const toggleActions = (state?: boolean) => {
  showActions.value = state !== undefined ? state : !showActions.value
}

const currentPageTitle = computed(() => {
  if (route.path === '/') return 'Dashboard'
  if (route.path.startsWith('/payment')) return 'Payments'
  if (route.path.startsWith('/transactions')) return 'Transactions'
  if (route.path.startsWith('/accounts')) return 'Accounts'
  return 'Dashboard'
})

// FAB Actions per page
const fabActions = computed(() => {
  if (route.path === '/') {
    return [
      { label: 'Make Payment', path: '/payment/start' },
      { label: 'View Transactions', path: '/transactions' },
    ]
  }
  if (route.path.startsWith('/payment')) {
    return [{ label: 'View Transactions', path: '/transactions' }]
  }
  if (route.path.startsWith('/transactions')) {
    return [{ label: 'Make Payment', path: '/payment/start' }]
  }
  if (route.path.startsWith('/accounts')) {
    return [{ label: 'Add Account', path: '/accounts/new' }]
  }
  return []
})

const handleAction = (action: any) => {
  toggleActions(false)
  navigateTo(action.path)
}

const maskedAccountNumber = computed(() =>
  accountNumber.value
    ? accountNumber.value.replace(/\d(?=\d{4})/g, '*')
    : '**** **** **** 0000',
)

const goDetail = (id: number) => navigateTo(`/transactions/${id}`)
const goTransactions = () => navigateTo('/transactions')

const getLogoUrl = (path: string) =>
  !path
    ? `${BACKEND_URL}/static/logos/default.png`
    : path.startsWith('http')
    ? path
    : `${BACKEND_URL}${path}`

const { format } = useCurrency()

const formatCurrency = (val?: number | string | null, currency = 'USD') => {
  return format(val, currency)
}

const formatDate = (isoString?: string) => {
  if (!isoString) return '—'
  const date = new Date(isoString)
  return date.toLocaleDateString()
}

async function loadDashboard() {
  const storedToken = localStorage.getItem('token')
  if (!storedToken) {
    console.warn('No token found, redirecting to login')
    return navigateTo('/login')
  }

  try {
    const me = await $api('/me/')
    if (!me) throw new Error('Unauthorized')

    balance.value = me.total_balance || 0

    const accounts = me.accounts || []
    if (accounts.length > 0) {
      accountName.value = accounts[0].name
      accountNumber.value = accounts[0].number
      accountType.value = accounts[0].type || 'Main Wallet'
    }

    let txs: any[] = []

    if (
      accounts.length > 0 &&
      Array.isArray(accounts[0].transactions) &&
      accounts[0].transactions.length
    ) {
      txs = accounts[0].transactions
    } else if (accounts.length > 0) {
      try {
        txs = await $api(`/accounts/${accounts[0].id}/transactions`)
      } catch (err) {
        console.warn('Failed to fetch account transactions', err)
        txs = []
      }
    } else {
      try {
        const maybeTxs = await $api('/transactions/')
        txs = Array.isArray(maybeTxs) ? maybeTxs : (maybeTxs.items || [])
      } catch (err) {
        console.warn('Failed to fetch /transactions/', err)
        txs = []
      }
    }

    transactions.value = (txs || []).slice(0, 5).map((t: any) => ({
      id: t.id,
      transaction_id: t.transaction_id,
      reference_number: t.reference_number,
      description: t.description,
      amount: t.amount ?? t.total_amount ?? 0,
      total_amount: t.total_amount ?? t.amount ?? 0,
      currency: t.currency || 'USD',
      direction: t.direction || 'debit',
      service_name: t.service_name || t.payment?.service?.name || null,
      service_logo_url: t.service_logo_url || t.payment?.service?.logo_url || null,
      created_at: t.created_at || t.createdAt || null,
    }))
  } catch (err: any) {
    console.error('Failed to load dashboard', err)
    if (err?.response?.status === 401) {
      localStorage.removeItem('token')
      navigateTo('/login')
    }
  }
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.25s ease-out;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(10px);
  opacity: 0;
}
</style>
