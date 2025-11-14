<script setup lang="ts">
definePageMeta({ layout: 'admin' })

import { ref, onMounted, computed, h } from 'vue'
import type { ColumnDef } from '@tanstack/vue-table'
import { useMyToast } from '~/composables/useMyToast'

const services = ref<any[]>([])
const pending = ref(false)
const toast = useMyToast()

const { $api } = useNuxtApp()

async function load() {
  pending.value = true
  try {
    const res = await $api('/adm/services')
    // backend returns plain array, but be defensive
    services.value = Array.isArray(res) ? res : (res.items ?? [])
  } catch (err) {
    console.error('Failed to load services:', err)
    toast.add({ title: 'Failed to load services', color: 'error' })
    services.value = []
  } finally {
    pending.value = false
  }
}

async function addService() {
  const name = prompt('Service name:')
  const code = prompt('Service code:')
  if (!name || !code) return

  try {
    await $api('/adm/services', {
      method: 'POST',
      body: {
        name,
        code,
        // keep your previous default
        logo_url: '/static/logos/default.png'
      }
    })
    toast.add({ title: 'Service added', color: 'success' })
    await load()
  } catch (err) {
    console.error('Add service failed:', err)
    toast.add({ title: 'Add service failed', color: 'error' })
  }
}

async function editService(row: any) {
  const svc = row.original as any
  const newName = prompt('New service name:', svc.name)
  const newCode = prompt('New service code:', svc.code)
  if (!newName || !newCode) return

  try {
    await $api(`/adm/services/${svc.id}`, {
      method: 'PUT',
      body: {
        name: newName,
        code: newCode,
        logo_url: svc.logo_url ?? '/static/logos/default.png',
        description: svc.description ?? null
      }
    })
    toast.add({ title: 'Service updated', color: 'success' })
    await load()
  } catch (err) {
    console.error('Update service failed:', err)
    toast.add({ title: 'Update service failed', color: 'error' })
  }
}

async function deleteService(row: any) {
  const svc = row.original as any
  if (!confirm(`Delete service "${svc.name}"?`)) return

  try {
    await $api(`/adm/services/${svc.id}`, { method: 'DELETE' })
    toast.add({ title: 'Service deleted', color: 'success' })
    await load()
  } catch (err) {
    console.error('Delete service failed:', err)
    toast.add({ title: 'Delete service failed', color: 'error' })
  }
}

/* -------- Admin topbar title -------- */
const adminTitle = useAdminTitle()
adminTitle.value = 'Service Management'

/* -------- UTable columns (TanStack style) -------- */

type RowT = Record<string, any>

const columns = ref<ColumnDef<RowT, any>[]>([
  {
    accessorKey: 'id',
    header: 'ID',
    cell: ({ getValue }) => String(getValue() ?? '-')
  },
  {
    accessorKey: 'name',
    header: 'Name',
    cell: ({ getValue }) => String(getValue() ?? '-')
  },
  {
    accessorKey: 'code',
    header: 'Code',
    cell: ({ getValue }) => String(getValue() ?? '-')
  },
  {
    accessorKey: 'logo_url',
    header: 'Logo',
    cell: ({ row }) => {
      const url = row.original.logo_url
      if (!url) return '—'
      return h('img', {
        src: url,
        class: 'h-8 w-8 rounded object-contain border'
      })
    }
  },
  {
    accessorKey: 'description',
    header: 'Description',
    cell: ({ getValue }) => String(getValue() ?? '-')
  },
  {
    accessorKey: 'actions',
    header: 'Actions',
    cell: () => ' '
  }
])

const total = computed(() => services.value.length)
</script>

<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-4">
      <div>
        <h1 class="text-2xl font-bold">Service Management</h1>
        <p class="text-sm text-gray-500">Manage OSP services available in the app.</p>
      </div>

      <div class="flex items-center gap-3">
        <div class="text-sm text-gray-600">
          Total: <span class="font-medium">{{ total }}</span>
        </div>
        <UButton color="primary" icon="i-heroicons-plus" @click="addService">
          Add Service
        </UButton>
      </div>
    </div>

    <UCard class="shadow-sm border rounded-2xl overflow-hidden">
      <UTable
        :data="services"
        :columns="columns"
        :loading="pending"
        class="min-w-full"
      >
        <!-- Actions column -->
        <template #{"actions-cell"}="{ row }">
          <div class="flex items-center gap-2">
            <UButton
              size="sm"
              variant="outline"
              @click="editService(row)"
            >
              Edit
            </UButton>

            <UButton
              size="sm"
              color="red"
              variant="ghost"
              @click="deleteService(row)"
            >
              Delete
            </UButton>
          </div>
        </template>

        <!-- Custom empty / loading states -->
        <template #loading>
          <div class="p-6 text-center text-gray-500">Loading services…</div>
        </template>

        <template #empty>
          <div class="p-6 text-center text-gray-500">
            No services found. Click <span class="font-medium">“Add Service”</span> to create one.
          </div>
        </template>
      </UTable>
    </UCard>
  </div>
</template>

<style scoped>
td {
  vertical-align: middle;
}
</style>
