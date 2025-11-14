<!-- frontend/app/pages/adm/users/index.vue -->
<template>
  <AdminTablePage
    title="User Management"
    :data="users"
    :columns="columns"
    :loading="pending"
    :page="page"
    :total-pages="totalPages"
    :on-row-select="onRowSelect"
    :disable-pagination="pending"
    @change-page="go"
  >
    <!-- Top-right actions -->
    <template #actions>
      <UButton
        variant="solid"
        class="btn-dark"
        label="+ Create User"
        @click="showCreate = true"
      />
    </template>

    <!-- Custom cell for created_at -->
    <template #created_at-cell="{ row }">
      {{ formatDate(row.original.created_at) }}
    </template>

    <!-- Empty state -->
    <template #empty>
      <div class="p-6 text-center text-gray-500">
        No users found.
      </div>
    </template>

    <!-- Bottom-left summary -->
    <template #summary>
      Showing {{ users.length }} of {{ total }} users — Page {{ page }} / {{ totalPages }}
    </template>
  </AdminTablePage>

  <!-- Create User Modal -->
  <UModal v-model:open="showCreate" title="Create New User">
    <template #body>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 p-2">
        <UFormField label="Name">
          <UInput
            v-model="newUser.name"
            icon="i-lucide-user"
            color="neutral"
            placeholder="Enter user name"
            size="lg"
          />
        </UFormField>

        <UFormField label="Phone">
          <UInput
            v-model="newUser.phone"
            icon="i-lucide-phone"
            type="tel"
            color="neutral"
            placeholder="Enter phone number"
            size="lg"
          />
        </UFormField>

        <UFormField label="Password">
          <UInput
            v-model="newUser.password"
            icon="i-lucide-lock"
            type="password"
            color="neutral"
            placeholder="Enter password"
            size="lg"
          />
        </UFormField>

        <UFormField label="Role">
          <USelect
            v-model="newUser.role"
            color="neutral"
            :items="[
              { label: 'User', value: 'user' },
              { label: 'Admin', value: 'admin' },
            ]"
            placeholder="Select role"
            size="lg"
          />
        </UFormField>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end gap-3 py-2 px-3">
        <UButton
          label="Cancel"
          color="neutral"
          variant="outline"
          @click="showCreate = false"
        />
        <UButton
          label="Create"
          class="btn-dark"
          :loading="creating"
          :disabled="!newUser.name || !newUser.phone || !newUser.password"
          @click="createUser"
        />
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin' })

import { useMediaQuery } from '@vueuse/core'
import type { ColumnDef } from '@tanstack/vue-table'

type RowT = Record<string, any>

const { $api } = useNuxtApp()
const { logout } = useAuth()
const toast = useMyToast()

// set mobile top-bar title (layout reads this)
const adminTitle = useAdminTitle()
onMounted(() => { adminTitle.value = 'User Management' })

// --- UI state ---
const isDesktop = useMediaQuery('(min-width: 768px)')
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

const columns: ColumnDef<RowT, any>[] = [
  { accessorKey: 'id', header: 'ID' },
  { accessorKey: 'name', header: 'Name' },
  { accessorKey: 'phone', header: 'Phone' },
  { accessorKey: 'role', header: 'Role' },
  { accessorKey: 'created_at', header: 'Created' },
]

function getActions(user: any) {
  return [
    [
      {
        label: 'Edit',
        icon: 'i-lucide-edit',
        onSelect: () => navigateTo(`/adm/users/${user.id}?edit=1`),
      },
    ],
    [
      {
        label: 'Delete',
        icon: 'i-lucide-trash',
        color: 'error',
        onSelect: () => onDelete(user),
      },
    ],
  ]
}

function onRowSelect(e: Event, row: any) {
  const target = e.target as HTMLElement
  if (target.closest('button') || target.closest('a')) return
  navigateTo(`/adm/users/${row.original.id}`)
}

const totalPages = computed(() =>
  Math.max(1, Math.ceil(total.value / pageSize)),
)

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
    const res = await $api('/adm/users', {
      query: {
        q: q.value || undefined,
        page: page.value,
        page_size: pageSize,
        sort: sort.value.column,
        dir: sort.value.direction,
      },
    })
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
    const res = await $api('/adm/users', {
      method: 'POST',
      body: {
        ...newUser,
        name: newUser.name.trim(),
        phone: newUser.phone.trim(),
        password: newUser.password.trim(),
      },
    })
    toast.add({
      title: res?.id ? 'User created successfully' : 'Failed to create user',
      color: res?.id ? 'green' : 'red',
    })
    Object.assign(newUser, {
      name: '',
      phone: '',
      password: '',
      role: 'user',
    })
    showCreate.value = false
    await load()
  } catch (err) {
    console.error(err)
    toast.add({ title: 'Create failed', color: 'red' })
  } finally {
    creating.value = false
  }
}

async function onDelete(u: any) {
  if (!confirm(`Delete ${u.name || u.phone}?`)) return
  deletingId.value = u.id
  try {
    await $api(`/adm/users/${u.id}`, { method: 'DELETE' })
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
  if (!date) return '-'
  const d = new Date(date)
  return `${d.toLocaleDateString()} ${d.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  })}`
}

onMounted(load)
</script>
