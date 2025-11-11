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
            <h1 class="text-2xl font-bold text-gray-800">Dummy Admin</h1>
            <button
              v-if="!isDesktop"
              @click="sidebarOpen = false"
              class="text-gray-500 hover:text-gray-800 md:hidden"
            >
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- ADMIN NAV -->
          <nav class="space-y-3 flex-1">
            <SidebarItem label="Home" icon="Home" to="/admin" :collapsed="!isDesktop" />
            <SidebarItem label="User Management" icon="User" to="/admin/users" :collapsed="!isDesktop" />
            <SidebarItem label="Payments" icon="CreditCard" to="/admin/payments" :collapsed="!isDesktop" />
            <SidebarItem label="Transactions" icon="List" to="/admin/transactions" :collapsed="!isDesktop" />
            <SidebarItem label="Service Management" icon="List" to="/admin/services" :collapsed="!isDesktop" />
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
      <div class="flex items-center md:hidden mb-6 sticky top-0 bg-gray-50 z-20 px-2">
        <button @click="sidebarOpen = true" class="text-gray-700 hover:text-gray-900">
          <Menu class="w-6 h-6" />
        </button>
        <h2 class="ml-3 text-lg font-semibold">User Management</h2>
      </div>

      <!-- Page Header -->
      <div class="hidden md:flex justify-between items-center mb-8">
        <h2 class="text-2xl font-bold text-gray-800 capitalize">User Management</h2>

        <div class="flex items-center gap-3">
          <input
            v-model.trim="q"
            type="search"
            placeholder="Search by name or phone"
            class="border rounded-xl px-4 py-2 w-64"
            @keyup.enter="refreshList"
          />
          <button class="px-4 py-2 rounded-xl border" @click="refreshList">Search</button>
        </div>
      </div>

      <!-- Users Table -->
      <section class="space-y-6">
        <div class="overflow-x-auto rounded-2xl border bg-white">
          <table class="min-w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="text-left p-3 cursor-pointer" @click="sortBy('id')">
                  ID <span class="ml-1">{{ sortIndicator('id') }}</span>
                </th>
                <th class="text-left p-3 cursor-pointer" @click="sortBy('name')">
                  Name <span class="ml-1">{{ sortIndicator('name') }}</span>
                </th>
                <th class="text-left p-3 cursor-pointer" @click="sortBy('phone')">
                  Phone <span class="ml-1">{{ sortIndicator('phone') }}</span>
                </th>
                <th class="text-left p-3 cursor-pointer" @click="sortBy('role')">
                  Role <span class="ml-1">{{ sortIndicator('role') }}</span>
                </th>
                <th class="text-left p-3 cursor-pointer" @click="sortBy('created_at')">
                  Created <span class="ml-1">{{ sortIndicator('created_at') }}</span>
                </th>
                <th class="text-right p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id" class="border-t">
                <td class="p-3">{{ u.id }}</td>
                <td class="p-3">{{ u.name }}</td>
                <td class="p-3">{{ u.phone }}</td>
                <td class="p-3">
                  <span class="inline-block rounded-full px-2 py-0.5 text-xs border">
                    {{ u.role || 'user' }}
                  </span>
                </td>
                <td class="p-3">{{ formatDate(u.created_at) }}</td>
                <td class="p-3 text-right space-x-2">
                  <NuxtLink :to="`/admin/users/${u.id}`" class="px-3 py-1 border rounded-xl">View</NuxtLink>
                  <NuxtLink :to="`/admin/users/${u.id}?edit=1`" class="px-3 py-1 border rounded-xl">Edit</NuxtLink>
                  <button
                    class="px-3 py-1 border rounded-xl"
                    @click="onDelete(u)"
                    :disabled="deletingId===u.id"
                  >
                    {{ deletingId===u.id ? 'Deleting…' : 'Delete' }}
                  </button>
                </td>
              </tr>
              <tr v-if="!pending && users.length === 0">
                <td colspan="6" class="p-6 text-center text-gray-500">No users found.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-600">Page {{ page }} of {{ totalPages || 1 }}</div>
          <div class="flex gap-2">
            <button class="px-3 py-1 border rounded-xl" :disabled="page<=1 || pending" @click="go(page-1)">Prev</button>
            <button class="px-3 py-1 border rounded-xl" :disabled="page>=totalPages || pending" @click="go(page+1)">Next</button>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import SidebarItem from '~/components/SidebarItem.vue'
import { LogOut, Menu, X } from 'lucide-vue-next'

type Role = 'user' | 'admin'
interface User { id: number; name?: string; phone: string; role: Role; created_at?: string }
interface Paginated<T> { items: T[]; total: number }

const { $api } = useNuxtApp()
const { logout } = useAuth()

const isDesktop = ref(false)
const sidebarOpen = ref(false)

onMounted(() => {
  const updateScreen = () => { isDesktop.value = window.innerWidth >= 768 }
  updateScreen()
  window.addEventListener('resize', updateScreen)
})
onBeforeUnmount(() => window.removeEventListener('resize', () => {}))

const q = ref('')
const page = ref(1)
const pageSize = ref(10)
const sort = ref<{field:string, dir:'asc'|'desc'}>({ field: 'created_at', dir: 'desc' })

const users = ref<User[]>([])
const total = ref(0)
const pending = ref(false)
const deletingId = ref<number | null>(null)

const totalPages = computed(() => Math.max(1, Math.ceil((total.value || 0) / pageSize.value)))

function sortBy(field: string) {
  if (sort.value.field === field) {
    sort.value.dir = sort.value.dir === 'asc' ? 'desc' : 'asc'
  } else {
    sort.value.field = field
    sort.value.dir = 'asc'
  }
  page.value = 1
  load()
}
function sortIndicator(field: string) {
  if (sort.value.field !== field) return '↕'
  return sort.value.dir === 'asc' ? '▲' : '▼'
}
function go(p: number) {
  page.value = Math.min(Math.max(1, p), totalPages.value || 1)
  load()
}
function refreshList() {
  page.value = 1
  load()
}
function formatDate(s?: string) { return s ? new Date(s).toLocaleString() : '-' }

async function load() {
  pending.value = true
  try {
    // Your backend endpoint
    const res = await $api<Paginated<User> | User[]>('/admin/users/', {
      query: {
        q: q.value || undefined,
        page: page.value,
        page_size: pageSize.value,
        sort: sort.value.field,
        dir: sort.value.dir,
      },
    })
    // Accept either paginated shape or plain array
    // @ts-ignore
    users.value = Array.isArray(res) ? res : (res.items || [])
    // @ts-ignore
    total.value = Array.isArray(res) ? users.value.length : (res.total ?? users.value.length)
  } catch (e) {
    console.error(e)
    users.value = []
    total.value = 0
  } finally {
    pending.value = false
  }
}

async function onDelete(u: User) {
  const ok = confirm(`Delete ${u.name || u.phone} (ID ${u.id})? This cannot be undone.`)
  if (!ok) return
  deletingId.value = u.id
  try {
    await $api(`/admin/users/${u.id}`, { method: 'DELETE' })
    users.value = users.value.filter(x => x.id !== u.id)
    total.value = Math.max(0, total.value - 1)
    await load()
  } catch (e) {
    console.error(e)
    alert('Delete failed')
  } finally {
    deletingId.value = null
  }
}

// initial load
onMounted(load)
</script>

<style scoped>
a.router-link-active {
  background-color: #f3f4f6;
  color: #111827;
}
</style>
