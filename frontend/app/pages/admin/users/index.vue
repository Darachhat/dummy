<template>
  <div class="flex min-h-screen">
    <!-- Sidebar -->
    <aside
      :class="[
        'border-r shadow-sm z-40 transform transition-transform duration-300 ease-in-out fixed md:static md:translate-x-0',
        'h-screen md:h-auto w-64 flex flex-col justify-between p-6',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <div>
        <div class="flex items-center justify-between mb-8">
          <h1 class="text-2xl font-bold ">Dummy Admin</h1>
          <UButton
            v-if="!isDesktop"
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
      <div class="flex items-center md:hidden mb-6 sticky top-0  z-20">
        <UButton icon="i-lucide-menu" color="neutral" variant="ghost" @click="sidebarOpen = true" />
        <h2 class="ml-3 text-lg font-semibold">User Management</h2>
      </div>

      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-3">
        <h2 class="text-2xl font-bold ">User Management</h2>
        <div class="flex flex-wrap items-center gap-3">
          <UInput
            v-model.trim="q"
            placeholder="Search by name or phone"
            icon="i-lucide-search"
            class="w-64"
            @keyup.enter="refreshList"
          />
          <UButton color="#162556 border-1 border-[#162556]" label="Search" @click="refreshList" />
          <UButton color="#162556 border-1 border-[#162556]" label="+ Create User" @click="showCreate = true" />
        </div>
      </div>

     <!-- USERS TABLE -->
<UCard class="shadow-sm border rounded-xl overflow-hidden">
  <UTable
    :data="users"
    class="min-w-full"
  >
    <template v-slot:default="{ row }">
      <tr class="border-b ">
        <td class="p-3">{{ row.id }}</td>
        <td class="p-3 font-medium">{{ row.name || '-' }}</td>
        <td class="p-3">{{ row.phone || '-' }}</td>
        <td class="p-3">
          <UBadge :label="row.role || 'user'"/>
        </td>
        <td class="p-3">{{ formatDate(row.created_at) }}</td>
        <td class="p-3 text-right">
          <div class="flex gap-2 justify-end">
            <UButton
              label="View"
              :to="`/admin/users/${row.id}`"
            />
            <UButton
              label="Edit"
              :to="`/admin/users/${row.id}?edit=1`"
            />
            <UButton
              label="Delete"
              :loading="deletingId === row.id"
              @click="onDelete(row)"
            />
          </div>
        </td>
      </tr>
    </template>
  </UTable>

  <!-- Pagination -->
  <template #footer>
    <div class="flex justify-between items-center text-sm text-gray-600 mt-3">
      <span>
        Showing {{ users.length }} of {{ total }} users — Page {{ page }} / {{ totalPages }}
      </span>
      <div class="flex gap-2">
        <UButton
          label="Prev"
          color="neutral"
          variant="outline"
          :disabled="page <= 1 || pending"
          @click="go(page - 1)"
        />
        <UButton
          label="Next"
          color="info"
          
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

const columns = [
  { id: 'id', header: 'ID', accessorKey: 'id', sortable: true },
  { id: 'name', header: 'Name', accessorKey: 'name', sortable: true },
  { id: 'phone', header: 'Phone', accessorKey: 'phone', sortable: true },
  { id: 'role', header: 'Role', accessorKey: 'role', sortable: true },
  { id: 'created_at', header: 'Created', accessorKey: 'created_at', sortable: true },
  { id: 'actions', header: 'Actions' },
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

// --- Fetch users ---
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

    // Handle backend response
    users.value = res.items ?? []
    total.value = res.total ?? users.value.length
  } catch (err) {
    console.error('Failed to load users:', err)
    toast.add({ title: 'Failed to load users', color: 'red' })
    users.value = []
    total.value = 0
  } finally {
    pending.value = false
  }
}

async function createUser() {
  if (!newUser.name || !newUser.phone || !newUser.password) {
    toast.add({ title: 'All fields are required', color: 'orange' })
    return
  }

  creating.value = true
  try {
    const payload = {
      name: newUser.name.trim(),
      phone: newUser.phone.trim(),
      password: newUser.password.trim(),
      role: newUser.role,
    }

    const res = await $api('/admin/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (res?.id) toast.add({ title: 'User created successfully', color: 'green' })
    else toast.add({ title: 'Failed to create user', color: 'red' })

    Object.assign(newUser, { name: '', phone: '', password: '', role: 'user' })
    showCreate.value = false
    await load()
  } catch (err) {
    console.error(err)
    toast.add({ title: 'Create failed', color: 'red' })
  } finally {
    creating.value = false
  }
}


// --- Delete user ---
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

// --- Pagination controls ---
function go(p: number) {
  page.value = Math.min(Math.max(1, p), totalPages.value)
  load()
}
function refreshList() {
  page.value = 1
  load()
}

// --- Sorting ---
function onSortChange({ column, direction }: any) {
  if (!column) return
  sort.value = { column, direction: direction || 'asc' }
  load()
}

// --- Date formatter ---
function formatDate(date?: string) {
  if (!date) return '-'
  const d = new Date(date)
  return `${d.toLocaleDateString()} ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
}

onMounted(load)
</script>

<style scoped>
</style>
