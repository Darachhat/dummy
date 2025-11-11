<template>
  <div class="flex min-h-screen bg-[var(--ui-bg-muted)]">
    <!-- Sidebar -->
    <aside
      :class="[ 
        'bg-[var(--ui-bg)] border-r border-[var(--ui-border)] shadow-sm z-40 transform transition-transform duration-300 ease-in-out fixed md:static md:translate-x-0',
        'h-screen md:h-auto w-64 flex flex-col justify-between p-6',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <div>
        <div class="flex items-center justify-between mb-8">
          <h1 class="text-2xl font-bold text-[var(--ui-text)]">Dummy Admin</h1>
          <UButton
            v-if="!isDesktop"
            color="neutral"
            variant="ghost"
            icon="i-lucide-x"
            @click="sidebarOpen = false"
          />
        </div>

        <!-- Navigation -->
        <nav class="space-y-2">
          <SidebarItem label="Home" icon="Home" to="/admin" />
          <SidebarItem label="User Management" icon="User" to="/admin/users" />
          <SidebarItem label="Payments" icon="CreditCard" to="/admin/payments" />
          <SidebarItem label="Transactions" icon="List" to="/admin/transactions" />
          <SidebarItem label="Service Management" icon="Settings" to="/admin/services" />
        </nav>
      </div>

      <UButton
        color="red"
        variant="subtle"
        label="Logout"
        icon="i-lucide-log-out"
        class="mt-8"
        @click="logout"
      />
    </aside>

    <!-- Main -->
    <main class="flex-1 p-4 md:p-8 overflow-x-hidden">
      <!-- Mobile Navbar -->
      <div class="flex items-center md:hidden mb-6 sticky top-0 bg-[var(--ui-bg-muted)] z-20">
        <UButton icon="i-lucide-menu" color="neutral" variant="ghost" @click="sidebarOpen = true" />
        <h2 class="ml-3 text-lg font-semibold">User Management</h2>
      </div>

      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-3">
        <h2 class="text-2xl font-bold text-[var(--ui-text-strong)]">User Management</h2>
        <div class="flex flex-wrap items-center gap-3">
          <UInput
            v-model.trim="q"
            placeholder="Search by name or phone"
            icon="i-lucide-search"
            class="w-64"
            @keyup.enter="refreshList"
          />
          <UButton label="Search" color="neutral" @click="refreshList" />
          <UButton label="+ Create User" color="primary" @click="showCreate = true" />
        </div>
      </div>

      <!-- User Table -->
      <UCard class="shadow-sm border rounded-xl overflow-hidden">
        <UTable
          :rows="userRows"
          :columns="columns"
          :loading="pending"
          loading-text="Loading users..."
          empty-text="No users found."
          :sort="sort"
          striped
          hover
          compact
          class="min-w-full"
          @update:sort="onSortChange"
        >
          <template #role-data="{ row }">
            <UBadge :label="row.role || 'user'" color="neutral" />
          </template>

          <template #created_at-data="{ row }">
            {{ formatDate(row.created_at) }}
          </template>

          <template #actions-data="{ row }">
            <div class="flex gap-2 justify-end">
              <UButton
                label="View"
                size="xs"
                color="neutral"
                variant="outline"
                :to="`/admin/users/${row.id}`"
              />
              <UButton
                label="Edit"
                size="xs"
                color="primary"
                variant="outline"
                :to="`/admin/users/${row.id}?edit=1`"
              />
              <UButton
                label="Delete"
                size="xs"
                color="red"
                variant="outline"
                :loading="deletingId === row.id"
                @click="onDelete(row)"
              />
            </div>
          </template>
        </UTable>

        <!-- Pagination -->
        <template #footer>
          <div class="flex justify-between items-center text-sm text-gray-600 mt-3">
            <span>
              Showing {{ userRows.length }} of {{ total }} users — Page {{ page }} / {{ totalPages }}
            </span>
            <div class="flex gap-2">
              <UButton
                label="Prev"
                size="xs"
                color="neutral"
                variant="outline"
                :disabled="page <= 1 || pending"
                @click="go(page - 1)"
              />
              <UButton
                label="Next"
                size="xs"
                color="neutral"
                variant="outline"
                :disabled="page >= totalPages || pending"
                @click="go(page + 1)"
              />
            </div>
          </div>
        </template>
      </UCard>

      <!-- Create User Modal -->
      <UModal v-model="showCreate" title="Create New User">
        <template #body>
          <div class="space-y-4">
            <UInput v-model="newUser.name" label="Name" placeholder="Enter user name" />
            <UInput v-model="newUser.phone" label="Phone" placeholder="Enter phone number" />
            <UInput
              v-model="newUser.password"
              label="Password"
              placeholder="Enter password"
              type="password"
            />
            <USelect
              v-model="newUser.role"
              :options="[
                { label: 'User', value: 'user' },
                { label: 'Admin', value: 'admin' },
              ]"
              label="Role"
            />
          </div>
        </template>

        <template #footer>
          <div class="flex justify-end gap-2">
            <UButton label="Cancel" color="neutral" variant="outline" @click="showCreate = false" />
            <UButton label="Create" color="primary" :loading="creating" @click="createUser" />
          </div>
        </template>
      </UModal>
    </main>
  </div>
</template>

<script setup lang="ts">
import SidebarItem from '~/components/SidebarItem.vue'
import { useMediaQuery } from '@vueuse/core'

const { $api } = useNuxtApp()
const { logout } = useAuth()
const toast = useToast()

// --- UI state ---
const isDesktop = useMediaQuery('(min-width: 768px)')
const sidebarOpen = ref(false)
const showCreate = ref(false)
const creating = ref(false)
const deletingId = ref<number | null>(null)

// --- Table & pagination ---
const q = ref('')
const page = ref(1)
const pageSize = 10
const total = ref(0)
const users = ref<any[]>([])
const pending = ref(false)
const userRows = computed(() => users.value ?? [])

const columns = [
  { id: 'id', label: 'ID', sortable: true },
  { id: 'name', label: 'Name', sortable: true },
  { id: 'phone', label: 'Phone', sortable: true },
  { id: 'role', label: 'Role', sortable: true },
  { id: 'created_at', label: 'Created', sortable: true },
  { id: 'actions', label: 'Actions' },
]

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

const sort = ref<{ column: string; direction: 'asc' | 'desc' }>({
  column: 'created_at',
  direction: 'desc',
})

const newUser = reactive({
  name: '',
  phone: '',
  password: '',
  role: 'user',
})

// --- Load Users ---
async function load() {
  pending.value = true
  try {
    const res = await $api('/admin/users', {
      query: {
        q: q.value || undefined,
        page: page.value,
        page_size: pageSize,
        sort: sort.value.column,
        dir: sort.value.direction,
      },
    })
    const data = res?.data ?? res
    users.value = data.items ?? []
    total.value = data.total ?? users.value.length
  } catch (err) {
    console.error('Failed to load users:', err)
    toast.add({ title: 'Failed to load users', color: 'red' })
    users.value = []
    total.value = 0
  } finally {
    pending.value = false
  }
}

// --- Create ---
async function createUser() {
  if (!newUser.name || !newUser.phone || !newUser.password) {
    toast.add({ title: 'All fields required', color: 'orange' })
    return
  }
  creating.value = true
  try {
    await $api('/admin/users', { method: 'POST', body: newUser })
    toast.add({ title: 'User created', color: 'green' })
    Object.assign(newUser, { name: '', phone: '', password: '', role: 'user' })
    showCreate.value = false
    await load()
  } catch {
    toast.add({ title: 'Create failed', color: 'red' })
  } finally {
    creating.value = false
  }
}

// --- Delete ---
async function onDelete(u: any) {
  if (!confirm(`Delete ${u.name || u.phone}?`)) return
  deletingId.value = u.id
  try {
    await $api(`/admin/users/${u.id}`, { method: 'DELETE' })
    toast.add({ title: 'User deleted', color: 'green' })
    await load()
  } catch {
    toast.add({ title: 'Delete failed', color: 'red' })
  } finally {
    deletingId.value = null
  }
}

function go(p: number) {
  page.value = Math.min(Math.max(1, p), totalPages.value)
  load()
}

function refreshList() {
  page.value = 1
  load()
}

function formatDate(date?: string) {
  return date ? new Date(date).toLocaleString() : '-'
}

function onSortChange(e: any) {
  if (!e?.column) return
  sort.value = { column: e.column, direction: e.direction || 'asc' }
  load()
}

onMounted(load)
</script>

<style scoped>
.router-link-active {
  background-color: var(--ui-bg-muted);
  color: var(--ui-text-strong);
}
</style>
